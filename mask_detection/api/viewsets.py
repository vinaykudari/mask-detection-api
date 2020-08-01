from rest_framework import viewsets, renderers
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Image
from .serializers import ImageSerializer


class ImageUploadParser(FileUploadParser):
	media_type = 'image/*'


class MaskDetectorViewSet(viewsets.ModelViewSet):
	model = Image
	queryset = Image.objects.all()
	serializer_class = ImageSerializer
	parser_classes = (MultiPartParser, ImageUploadParser,)

	@action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
	def predict(self):
		image = self.get_object()
		return Response('mask')
