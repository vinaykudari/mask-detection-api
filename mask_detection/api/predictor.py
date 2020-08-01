import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image as PILImage
from fastai.vision import load_learner, Image
from numpy import asarray
from torchvision.transforms import Compose, ToPILImage, Resize, ToTensor

from mask_detection.settings import MEDIA_ROOT

MASK_DETECTION_MODEL_PATH = '/Users/vinaykudari/uploads/models/mask-detection/'
FACE_DETECTION_PROTO_TXT_PATH = '/Users/vinaykudari/uploads/deploy.prototxt.txt'
FACE_DETECTION_MODEL_PATH = '/Users/vinaykudari/uploads/res10_300x300_ssd_iter_140000.caffemodel'
RES = 224
FACE_DETECTION_THRESHOLD = 0.8
MASK_DETECTION_THRESHOLD = 0.9

TRANSFORMATIONS = Compose([
        ToPILImage(),
        Resize((RES, RES)),
        ToTensor(),
    ])


def get_face_detection_model():
    face_detection_model = cv2.dnn.readNetFromCaffe(
        FACE_DETECTION_PROTO_TXT_PATH,
        FACE_DETECTION_MODEL_PATH
    )

    return face_detection_model


def get_mask_detection_learner():
    learner = load_learner(
        MASK_DETECTION_MODEL_PATH
    )

    return learner


def get_faces_from(image):
    img = PILImage.open(image)
    img_RGB = img.convert('RGB')
    img_mat = asarray(img_RGB)
    face_coordinates = []
    height, width = img_mat.shape[:2]

    face_detection_model = get_face_detection_model()
    blob = cv2.dnn.blobFromImage(
        image=cv2.resize(img_mat, (300, 300)),
        scalefactor=1.0,
        size=(300, 300),
        mean=(123.0, 117.0, 104.0),
        swapRB=False,
        crop=False
    )
    face_detection_model.setInput(blob)
    predictions = face_detection_model.forward()

    for i in range(predictions.shape[2]):
        accuracy = predictions[0, 0, i, 2]
        if accuracy > FACE_DETECTION_THRESHOLD:
            box = predictions[0, 0, i, 3:7] * np.array([width, height, width, height])
            x1, y1, x2, y2 = box.astype("int")
            face_coordinates.append(np.array([x1, y1, x2-x1, y2-y1]))

    return face_coordinates, img_mat


def is_wearing_mask(face, image):
    x, y, w, h = face
    mask_detection_learner = get_mask_detection_learner()
    x, y = max(x, 0), max(y, 0)
    print(f'x={x}, y={y}, w={w}, h={h}')
    print(f'y+h={y+h}, x+w = {x+w}')
    face_with_padding = image[y:y+h, x:x+w]

    img = Image(TRANSFORMATIONS(face_with_padding))
    pred_class, pred_idx, outputs = mask_detection_learner.predict(img)
    if outputs[0] < MASK_DETECTION_THRESHOLD:
        return False

    return outputs[0]


def analyse(image):
    faces, image = get_faces_from(image)
    faces_with_mask = []
    face_details = []
    i = 1

    for face in faces:
        mask_accuracy = is_wearing_mask(face, image)
        if mask_accuracy:
            faces_with_mask.append(
                {
                    'id': i
                }
            )
        face_details.append(
            {
                'id': i,
                'coordinates': face.tolist()
            }
        )
        i += 1

    response = {
        'no_of_faces': i-1,
        'face_details': face_details,
        'no_of_faces_with_mask': len(faces_with_mask),
        'faces_with_mask': faces_with_mask,
    }

    return response['no_of_faces_with_mask'] > 0, response


