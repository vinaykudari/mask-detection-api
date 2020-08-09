import os

import cv2
from django.conf.global_settings import MEDIA_ROOT
from fastai.vision import load_learner

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
