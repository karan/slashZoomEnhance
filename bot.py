# Built-in imports
import logging
import os
import shutil
import time

# Third-party dependencies
import requests
import tweepy
from ttp import ttp

# Custom imports
from face_detect import process
try:
    import config
except:
    import config_example as config


# Gloabl variable init
TWEET_LENGTH = 140
IMAGE_URL_LENGTH = 23
MAX_TWEET_TEXT_LENGTH = TWEET_LENGTH - IMAGE_URL_LENGTH - 1
DOTS = '...'
BACKOFF = 0.5 # Initial wait time before attempting to reconnect
MAX_BACKOFF = 300 # Maximum wait time between connection attempts
MAX_IMAGE_SIZE = 3072 * 1024 # bytes
USERNAME = 'slashZoomE'

# BLACKLIST
# Do not respond to queries by these accounts
BLACKLIST = [
    'pixelsorter',
    'lowpolybot',
    'slashkarebear',
    'slashgif',
    'slashremindme',
    USERNAME,
]


logging.basicConfig(filename='logger.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Twitter client
auth = tweepy.OAuthHandler(config.twitter['key'], config.twitter['secret'])
auth.set_access_token(config.twitter['access_token'],
                      config.twitter['access_token_secret'])
api = tweepy.API(auth)
# Tweet parser
parser = ttp.Parser()
# backoff time
backoff = BACKOFF


def download_image(url):
    r = requests.get(url, stream=True)

    filename = ''
    if r.status_code == 200:
        filename = 'images/%s.png' % url
        with open(filename, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

    logging.info('download_image: %s--%s' % (url, filename)
    return filename


def parse_tweet(status):
    if hasattr(status.entities, 'media') and len(status.entities.media) > 0 and \
        status.entities.media.type == 'photo':
        img_url = status.entities.media[0].media_url
    else:
        tweet_from = status.user.screen_name
        tweet_text = status.text

        query = tweet_text[tweet_text.index('@%s' % USERNAME) + len('@%s' % USERNAME) + 1:]

        result = parser.parse(tweet_text)
        tagged_users = result.users + [tweet_from]
        tagged_hashtags = result.tags
        tagged_urls = result.urls

        for user in tagged_users:
            query = query.replace('@%s' % user, '')
        for tag in tagged_hashtags:
            query = query.replace('#%s' % tag, '')
        for url in tagged_urls:
            query = query.replace('%s' % url, '')

        logging.info('parse_tweet: %s--%s' % (tagged_users, query))

        user = api.get_user(tagged_users[0])
        img_url = user.profile_image_url

    logging.info('parse_tweet: %s--%s--%s' % (tagged_users, img_url))
    return tagged_users, img_url


def generate_reply_tweet(users, symbol, quote):
    reply = '%s' % ' '.join(['@%s' % user for user in users if user != USERNAME])
    if len(reply) > MAX_TWEET_TEXT_LENGTH:
        reply = reply[:MAX_TWEET_TEXT_LENGTH - len(DOTS) - 1] + DOTS

    logging.info('generate_reply_tweet: %s' % reply)
    return reply


class StreamListener(tweepy.StreamListener):

    def on_status(self, status):
        global backoff

        backoff = BACKOFF
        # Collect logging and debugging data
        tweet_id = status.id
        tweet_text = status.text
        tweet_from = status.user.screen_name

        if tweet_from.lower() not in BLACKLIST and not hasattr(status, 'retweeted_status'):
            logging.info('on_status: %s--%s' % (tweet_id, tweet_text))

            # Parse tweet for search term
            tagged_users, img_url = parse_tweet(status)
            filename = download_image(img_url)
            try:
                result_filename = process(filename)
                reply_tweet = generate_reply_tweet(tagged_users)
                reply_status = api.update_with_media(filename=result_filename,
                                                     status=reply_tweet,
                                                     in_reply_to_status_id=tweet_id)

                logging.info('on_status_sent: %s %s' % (reply_status.id_str, reply_status.text))
            except Exception, e:
                logging.error('face_detect error: %s' % e)
                err_tweet = '@%s Something\' not quite right here. cc: @karangoel' tweet_from
                reply_status = api.update_status(status=err_tweet,
                                                 in_reply_to_status_id=tweet_id)
        return True

    def on_error(self, status_code):
        global backoff
        logging.info('on_error: %d' % status_code)

        if status_code == 420:
            backoff = backoff * 2
            logging.info('on_error: backoff %s seconds' % backoff)
            time.sleep(backoff)
            return True


if not os.path.exists('images/'):
    os.makedirs('images/')

stream_listener = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
try:
    stream.userstream(_with='user', replies='all')
except Exception as e:
    logging.ERROR('stream_exception: %s' % e)
    raise e
