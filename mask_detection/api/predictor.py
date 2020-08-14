import cv2
import numpy as np
from PIL import Image as PILImage

from fastai.vision import Image
from numpy import asarray
from torchvision.transforms import Compose, ToPILImage, Resize, ToTensor

from django.conf import settings

RES = 224
FACE_DETECTION_CONFIDENCE = 0.5
FACE_DETECTION_THRESHOLD = 0.4
MASK_DETECTION_THRESHOLD = 0.96

TRANSFORMATIONS = Compose([
	ToPILImage(),
	Resize((RES, RES)),
	ToTensor(),
])

face_detection_model = settings.FACE_DETECTION_MODEL
mask_detection_learner = settings.MASK_DETECTION_LEARNER


def get_faces_from(image):
	img = PILImage.open(image)
	img_RGB = img.convert('RGB')
	img_mat = asarray(img_RGB)
	face_details = []
	face_coordinates, confidence, indexes = [], [], np.array([])
	img_height, img_width = img_mat.shape[:2]
	
	blob = cv2.dnn.blobFromImage(
		img_mat,
		1 / 255.,
		(416, 416),
		[0, 0, 0],
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
		for detection in out:
			scores = detection[5:]
			conf = scores[np.argmax(scores)]
			if conf > FACE_DETECTION_THRESHOLD:
				face_width = int(detection[2] * img_width)
				face_height = int(detection[3] * img_height)
				x1 = int(int(detection[0] * img_width) - face_width / 2)
				y1 = int(int(detection[1] * img_height) - face_height / 2)
				
				confidence.append(float(conf))
				face_coordinates.append([x1, y1, face_width, face_height])

	confidence = np.array(confidence)
	face_coordinates = np.array(face_coordinates)
	
	if face_coordinates.any() and confidence.any():
		face_coordinates = face_coordinates.tolist()
		confidence = confidence.tolist()
		
		indexes = np.array(cv2.dnn.NMSBoxes(
			face_coordinates,
			confidence,
			FACE_DETECTION_CONFIDENCE,
			FACE_DETECTION_THRESHOLD
		))
	
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
	x1, y1 = max(x - 20, 0), max(y - 20, 0)
	x2, y2 = min(x + w + 20, width), min(y + h + 20, height)
	face_with_padding = image[y1:y2, x1:x2]
	
	img = Image(TRANSFORMATIONS(face_with_padding))
	pred_class, pred_idx, outputs = mask_detection_learner.predict(img)
	if outputs[0] < MASK_DETECTION_THRESHOLD:
		return False
	
	return outputs[0]


def analyse(image):
	image_details, image = get_faces_from(image)
	faces_with_mask = {}
	face_details = {}
	
	for i in range(len(image_details)):
		mask_accuracy = is_wearing_mask(image_details[i]['coordinates'], image)
		if mask_accuracy:
			faces_with_mask[i] = {
				'mask_confidence': mask_accuracy.item(),
			}
		
		face_details[i] = {
			'face_confidence': image_details[i]['confidence'],
			'coordinates': image_details[i]['coordinates'],
		}
	
	response = {
		'no_of_faces': len(image_details),
		'no_of_faces_with_mask': len(faces_with_mask),
		'face_details': face_details,
		'faces_with_mask': faces_with_mask,
	}
	
	return response['no_of_faces_with_mask'] > 0, response
