from wand.image import Image

import cv2
import sys

CASCADE_PATH = 'haarcascade_frontalface_default.xml'
NUM_IMAGES = 4

# Create the haar cascade
faceCascade = cv2.CascadeClassifier(CASCADE_PATH)

def get_faces(imagePath):
  # Read the image
  image = cv2.imread(imagePath)
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

  # Detect faces in the image
  faces = faceCascade.detectMultiScale(
      gray,
      scaleFactor=1.1,
      minNeighbors=5,
      minSize=(30, 30),
      flags = cv2.cv.CV_HAAR_SCALE_IMAGE
  )

  print "Found {0} faces!".format(len(faces))
  return faces


def scale(imagePath, face):
  # cloneImg.save(filename='{0}-{1}.jpg'.format(imagePath, i))

  face_x, face_y, face_w, face_h = face

  with Image(filename=imagePath) as img:
    img_w = img.size[0]
    img_h = img.size[1]

    w_delta = ((img_w - face_w) / 2) / NUM_IMAGES
    h_delta = ((img_h - face_h) / 2) / NUM_IMAGES

    gifImg = Image()

    for i in range(NUM_IMAGES, -1, -1):
      with img.clone() as cloneImg:
        if i == 0:
          cloneImg.crop(face_x, face_y, width=face_w, height=face_h)
          cloneImg.transform(resize='%dx%d' % (img_w, img_h))
        else:
          left = max(0, face_x - i * w_delta)
          top = max(0, face_y - i * h_delta)
          right = min(img_w, face_x + face_w + i * w_delta)
          bottom = min(img_h, face_y + face_h + i * h_delta)

          cloneImg.crop(left, top, right, bottom)
          cloneImg.transform(resize='%dx%d' % (img_w, img_h))
        gifImg.sequence.append(cloneImg)

    for frame in gifImg.sequence:
      with frame:
        frame.delay = 20
    gifImg.save(filename='%s.gif' % imagePath)
    gifImg.close()
    return '%s.gif' % imagePath


def process(imagePath):
  faces = get_faces(imagePath)

  if len(faces) > 0:
    face = faces[0]
    return scale(imagePath, face)

  return None
