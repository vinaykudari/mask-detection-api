import json

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Image
from .serializers import ImageSerializer

import PIL


class ImageUploadParser(FileUploadParser):
	media_type = 'image/*'


class MaskDetector(APIView):
	parser_class = (ImageUploadParser,)

	def post(self, request, *args, **kwargs):
		if 'file' not in request.data:
			raise ParseError("No image found")
		file = request.data.get('file')

		try:
			image = PIL.Image.open(file)
			image.verify()
		except PIL.UnidentifiedImageError as e:
			raise ParseError(e)

		Image.objects.create(image=image)

		return Response(status=status.HTTP_202_ACCEPTED)
