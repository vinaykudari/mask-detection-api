from django.http import JsonResponse
from rest_framework.views import APIView

from .predictor import analyse


class MaskDetectionAPI(APIView):
	def get(self, request):
		image = request.FILES['image']
		is_mask_detected, image_details = analyse(image)

		return JsonResponse(
			{
				'is_mask_detected': is_mask_detected,
				'image_details': image_details
			}
		)
