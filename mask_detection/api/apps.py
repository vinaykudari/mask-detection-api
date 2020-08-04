from django.apps import AppConfig
from .predictor import get_face_detection_model, get_mask_detection_learner


class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        get_face_detection_model()
        get_mask_detection_learner()
