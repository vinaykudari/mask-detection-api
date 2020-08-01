import PIL
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from .models import Image


class ImageSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Image
		fields = ('pk', 'image', )
