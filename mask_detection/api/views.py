from PIL import Image as PILImage
from django.db.models import Max, Sum

from django.http import JsonResponse
from rest_framework.views import APIView

from .models import Image, PredictedImageDetails, ActualImageDetails
from .predictor import analyse


class GetStats(APIView):
	def get(self, request):
		total_no_images = Image.objects.all().values('id').aggregate(Max('id'))

		return JsonResponse(
			{
				'total_no_images': total_no_images['id__max'],
			}
		)
	
	
class SaveFeedback(APIView):
	def post(self, request):
		image_id = request.POST.get('image_id')
		actual_no_of_faces = request.POST.get('actual_no_of_faces')
		actual_no_of_faces_with_masks = request.POST.get('actual_no_of_faces_with_masks')
		
		message = 'Thanks for your feedback!'
		status = 'success'
		
		try:
			ActualImageDetails.objects.create(
				image_id=image_id,
				faces=actual_no_of_faces,
				faces_with_masks=actual_no_of_faces_with_masks
			)
		except Exception as e:
			message = f'''
						Feedback could not be saved,
						please make sure image_id is valid and other
						values are integers
						
						Exception = {e}
					'''
			status = 'failed'
		
		return JsonResponse(
			{
				status: message
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
		
		if not request.POST.get('consent_to_store'):
			image = None
			
		image_obj = Image.objects.create(image=image)
		PredictedImageDetails.objects.create(
			image=image_obj,
			faces=image_details['no_of_faces'],
			faces_with_masks=image_details['no_of_faces_with_mask']
		)
		
		response = {
			'mask_detected': is_mask_detected,
			'image_details': image_details,
			'image_id': image_obj.id
		}
		
		return JsonResponse(response)
