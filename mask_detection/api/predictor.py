from django.conf import settings
from PIL import Image as PILImage

import cv2
import numpy as np
from fastai.vision import Image
from numpy import asarray
from torchvision.transforms import Compose, ToPILImage, Resize, ToTensor
from environ import Env

env = Env()

RES = 224
FACE_DETECTION_CONFIDENCE = env.float('FACE_DETECTION_CONFIDENCE', 0.4)
FACE_DETECTION_THRESHOLD = env.float('FACE_DETECTION_THRESHOLD', 0.4)
MASK_DETECTION_THRESHOLD = env.float('MASK_DETECTION_THRESHOLD', 0.95)

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
	faces = []
	face_coordinates, confidence, indexes = [], [], np.array([])
	img_height, img_width = img_mat.shape[:2]
	
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
	
	if face_coordinates and confidence:
		indexes = np.array(cv2.dnn.NMSBoxes(
			face_coordinates,
			confidence,
			FACE_DETECTION_CONFIDENCE,
			FACE_DETECTION_THRESHOLD
		))
	
	if indexes.any():
		for i in indexes.flatten():
			faces.append(
				{
					'coordinates': {
						'x1': max(face_coordinates[i][0], 0),
						'y1': max(face_coordinates[i][1], 0),
						'width': face_coordinates[i][2],
						'height': face_coordinates[i][3],
					},
					'confidence': confidence[i]
				}
			)
	
	return len(faces), faces, img_mat


def is_wearing_mask(face, image):
	height, width = image.shape[:2]
	x1, y1 = max(face['x1'] - 20, 0), max(face['y1'] - 20, 0)
	x2, y2 = min(face['x1'] + face['width'] + 20, width), min(face['y1'] + face['height'] + 20, height)
	face_with_padding = image[y1:y2, x1:x2]
	
	img = Image(TRANSFORMATIONS(face_with_padding))
	pred_class, pred_idx, outputs = mask_detection_learner.predict(img)
	
	return outputs[0].item()


def analyse(image):
	no_of_faces, faces, image = get_faces_from(image)
	no_of_faces_with_mask = 0
	face_details = {'id': {}}
	
	for i in range(no_of_faces):
		mask_confidence = is_wearing_mask(faces[i]['coordinates'], image)
		if mask_confidence > MASK_DETECTION_THRESHOLD:
			no_of_faces_with_mask += 1
		
		face_details['id'][i+1] = {
			'face_confidence': faces[i]['confidence'],
			'face_coordinates': faces[i]['coordinates'],
			'mask_confidence': mask_confidence
		}
	
	response = {
		'faces': no_of_faces,
		'faces_with_mask': no_of_faces_with_mask,
		'face': face_details,
	}
	
	return response['faces_with_mask'] > 0, response
