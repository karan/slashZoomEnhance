# slashStock

Zoom, Enhance built into Twitter. Automatically finds a face and zooms on it.

<Insert GIF>

### Usage

You can summon the bot by either:

1. Attaching an image
2. Tagging a user

#### Examples:

<Show example tweets>

### Where is this bot running?

Currently I'm running this bot on a 1GB [DigitalOcean](https://www.digitalocean.com/?refcode=422889a8186d) instance (Use that link to get a free VPS for 2 months). The bot is not resource-intensive and uses a couple dozen MBs of RAM.

## Running

#### Requirements

- Python 2+
- pip

#### Instructions 

Create a file called `config.py` that looks like `config_example.py`. Fill in the necessary values.

For Twitter config:

1. Register your app
2. Get your app's key and secret.
3. Create token and get the token and secret by running `oauth.py`

Then, to run the bot:

```bash
$ ./install.sh
$ python bot.py
```

## License 

Apache 2.0
