from PIL import Image as PILImage
from django.db.models import Max, Sum

from django.http import JsonResponse
from rest_framework.views import APIView

from .models import Image, PredictedImageDetails
from .predictor import analyse


class GetStats(APIView):
	def get(self, request):
		total_no_images = Image.objects.all().values('id').aggregate(Max('id'))

		return JsonResponse(
			{
				'total_no_images': total_no_images['id__max'],
			}
		)
		
		
class MaskDetectionAPI(APIView):
	def get(self, request):
		response = {
			"error": "Method GET does not exists"
		}
		
		return JsonResponse(response)
	
	def post(self, request):
		image = request.FILES.get('image')
		if not image:
			return JsonResponse(
				{
					"error": """Missing file. Request should include a Content-Disposition header with a image parameter."""
				}
			)
		
		try:
			PILImage.open(image)
		except Exception as e:
			return JsonResponse(
				{
					"error": """File provided is either corrupt or not a valid Image"""
				}
			)
		
		is_mask_detected, image_details = analyse(image)
		
		if request.POST.get('consent_to_store'):
			image_obj = Image.objects.create(image=image)
			PredictedImageDetails.objects.create(
				image=image_obj,
				faces=image_details['no_of_faces'],
				faces_with_masks=image_details['no_of_faces_with_mask']
			)
		
		response = {
			'mask_detected': is_mask_detected,
			'image_details': image_details
		}
		
		return JsonResponse(response)
