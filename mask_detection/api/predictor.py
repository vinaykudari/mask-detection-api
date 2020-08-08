import os

import cv2
import numpy as np
from PIL import Image as PILImage
from django.conf.global_settings import MEDIA_ROOT
from fastai.vision import load_learner, Image
from numpy import asarray
from torchvision.transforms import Compose, ToPILImage, Resize, ToTensor

from django.conf import settings

MASK_DETECTION_MODEL_PATH = os.path.join(
    MEDIA_ROOT,
    'uploads/models/mask-detection/'
)
FACE_DETECTION_ARCH_PATH = os.path.join(
    MEDIA_ROOT,
    'uploads/models/face-detection/yolov3-face.cfg'
)
FACE_DETECTION_MODEL_PATH = os.path.join(
    MEDIA_ROOT,
    'uploads/models/face-detection/yolov3-face.weights'
)
RES = 224
FACE_DETECTION_CONFIDENCE = 0.4
FACE_DETECTION_THRESHOLD = 0.4
MASK_DETECTION_THRESHOLD = 0.9

TRANSFORMATIONS = Compose([
    ToPILImage(),
    Resize((RES, RES)),
    ToTensor(),
])


def get_face_detection_model():
    face_detection_model = cv2.dnn.readNetFromDarknet(
        FACE_DETECTION_ARCH_PATH,
        FACE_DETECTION_MODEL_PATH
    )
    face_detection_model.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    face_detection_model.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

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
    face_coordinates, confidence, face_details = [], [], []
    height, width = img_mat.shape[:2]

    face_detection_model = settings.FACE_DETECTION_MODEL
    blob = cv2.dnn.blobFromImage(
        img_mat,
        1 / 255.,
        (416, 416),
        1,
        crop=False
    )
    face_detection_model.setInput(blob)
    layers_names = face_detection_model.getLayerNames()
    predictions = face_detection_model.forward(
        [
            layers_names[i[0] - 1]
            for i in face_detection_model.getUnconnectedOutLayers()
        ]
    )

    for out in predictions:
        out = out[out[:, -1] > FACE_DETECTION_THRESHOLD]
        if out.any():
            face_coordinates = out[:, :4] * np.array([width, height, width, height]).T
            face_coordinates = face_coordinates.astype(int)
            face_coordinates[:, 0] = face_coordinates[:, 0] - face_coordinates[:, 2] / 2
            face_coordinates[:, 1] = face_coordinates[:, 1] - face_coordinates[:, 3] / 2
            confidence = out[:, 5]

    face_coordinates = face_coordinates.tolist()
    confidence = confidence.tolist()

    indexes = cv2.dnn.NMSBoxes(
        face_coordinates,
        confidence,
        FACE_DETECTION_CONFIDENCE,
        FACE_DETECTION_THRESHOLD
    )

    if indexes.any():
        for i in indexes.flatten():
            face_details.append(
                {
                    'coordinates': face_coordinates[i],
                    'confidence': confidence[i]
                }
            )

    return face_details, img_mat


def is_wearing_mask(face, image):
    x, y, w, h = face
    height, width = image.shape[:2]
    mask_detection_learner = settings.MASK_DETECTION_LEARNER
    x1, y1 = max(x-20, 0), max(y-20, 0)
    x2, y2 = min(x+w+20, width), min(y+h+20, height)
    face_with_padding = image[y1:y2, x1:x2]

    img = Image(TRANSFORMATIONS(face_with_padding))
    pred_class, pred_idx, outputs = mask_detection_learner.predict(img)
    if outputs[0] < MASK_DETECTION_THRESHOLD:
        return False

    return outputs[0]


def analyse(image):
    image_details, image = get_faces_from(image)
    faces_with_mask = []
    face_details = []

    for i in range(len(image_details)):
        mask_accuracy = is_wearing_mask(image_details[i]['coordinates'], image)
        if mask_accuracy:
            faces_with_mask.append(
                {
                    'id': i,
                    'mask_confidence': mask_accuracy.item(),
                }
            )
        face_details.append(
            {
                'id': i,
                'face_confidence': image_details[i]['confidence'],
                'coordinates': image_details[i]['coordinates'],
            }
        )

    response = {
        'no_of_faces': len(image_details),
        'no_of_faces_with_mask': len(faces_with_mask),
        'face_details': face_details,
        'faces_with_mask': faces_with_mask,
    }

    return response['no_of_faces_with_mask'] > 0, response
