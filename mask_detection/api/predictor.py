from pathlib import Path

import cv2
from PIL import Image as PILImage

from fastai.vision import load_learner, Image
from numpy import asarray
from torchvision.transforms import Compose, ToPILImage, Resize, ToTensor

from mask_detection.settings import MEDIA_ROOT

MASK_DETECTION_MODEL_PATH = Path(MEDIA_ROOT)/'models/mask-detection/'
FACE_DETECTION_PROTO_TXT_PATH = Path(MEDIA_ROOT)/'models/face-detection/deploy.prototxt'
FACE_DETECTION_MODEL_PATH = Path(MEDIA_ROOT)/'models/face-detection/res10_300x300_ssd_iter_140000.caffemodel'
RES = 224
FACE_DETECTION_THRESHOLD = 0.6
MASK_DETECTION_THRESHOLD = 0.8

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
    faces = []
    height, width, _ = img_mat.shape

    face_detection_model = get_face_detection_model()
    blob = cv2.dnn.blobFromImage(
        image=img_mat,
        scalefactor=1.0,
        size=(height, width),
        swapRB=False,
        crop=False
    )
    face_detection_model.setInput(blob)
    predictions = face_detection_model.forward()

    for i in range(predictions.shape[2]):
        accuracy = predictions[0, 0, i, 2]
        if accuracy > FACE_DETECTION_THRESHOLD:
            box = predictions[0, 0, i, 3:7]
            x1, y1, x2, y2 = box.astype("int")
            faces.append([x1, y1, x2-x1, y2-y1])

    return faces


def is_wearing_mask(face):
    x, y, w, h = face
    mask_detection_learner = get_mask_detection_learner()
    face_with_padding = face[max(y-20, 0):y+h+20, max(x-20, 0):x+w+20]

    img = Image(TRANSFORMATIONS(face_with_padding))
    pred_class, pred_idx, outputs = mask_detection_learner.predict(img)
    if outputs[0] < MASK_DETECTION_THRESHOLD:
        return False

    return outputs[0]


def analyse(image):
    faces = get_faces_from(image)
    no_of_faces = len(faces)
    faces_with_mask = []

    for face in faces:
        mask_accuracy = is_wearing_mask(face)
        if mask_accuracy:
            faces_with_mask.append(face)

    response = {
        'no_of_faces': no_of_faces,
        'face_coordinates': faces,
        'no_of_faces_with_mask': len(faces_with_mask),
        'face_with_mask_coordinates': faces_with_mask,
    }

    return response['no_of_faces_with_mask'] > 0, response


