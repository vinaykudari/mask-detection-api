from PIL import Image as PILImage
from django.db.models import Max, Sum

from django.http import JsonResponse
from rest_framework.views import APIView

from .models import Image, PredictedImageDetails, ActualImageDetails, Feedback
from .predictor import analyse


class GetStats(APIView):
	def get(self, request):
		stats = PredictedImageDetails.objects.aggregate(**{
			'total_no_faces': Sum('faces'),
			'total_no_faces_with_masks': Sum('faces_with_masks'),
			'total_no_images': Max('image_id')
			}
		)

		return JsonResponse(
			{
				'stats': stats,
			}
		)
	
	
class SaveFeedback(APIView):
	def post(self, request):
		image_id = request.POST.get('image_id')
		feedback = request.POST.get('feedback')
		
		message = 'Thanks for your feedback!'
		status = 'success'
		
		if not image_id or not feedback:
			return JsonResponse(
				{
					'failed': 'Invalid POST data, Image ID and Feedback are needed'
				}
			)
		
		predicted_image_details = PredictedImageDetails.objects.filter(image_id=image_id).first()
		
		if not predicted_image_details:
			return JsonResponse(
				{
					'failed': 'Invalid Image ID, cannot save feedback'
				}
			)
		
		Feedback.objects.update_or_create(
			image_id=image_id,
			defaults={
				'type': feedback
			},
		)

		if feedback != 1:
			actual_no_of_faces = request.POST.get('actual_no_of_faces', -1)
			actual_no_of_faces_with_masks = request.POST.get('actual_no_of_faces_with_masks', -1)
		else:
			actual_no_of_faces = predicted_image_details.faces
			actual_no_of_faces_with_masks = predicted_image_details.faces_with_masks
			
		try:
			ActualImageDetails.objects.update_or_create(
				image_id=image_id,
				defaults={
					'faces': actual_no_of_faces,
					'faces_with_masks': actual_no_of_faces_with_masks
				},
			)
		except Exception as e:
			message = f'''
						Feedback could not be saved,
						please make sure Image ID is valid and other
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
			faces=image_details['faces'],
			faces_with_masks=image_details['faces_with_mask']
		)
		
		response = {
			'mask_detected': is_mask_detected,
			'image_details': image_details,
			'image_id': image_obj.id
		}
		
		return JsonResponse(response)
