import uuid

from django.db import models


def randomize_filename(self, filename):
	extension = filename.split(".")[-1]
	new_filename = f'{uuid.uuid4()}.{extension}'
	return f'images/{new_filename}'


class Image(models.Model):
	id = models.AutoField(primary_key=True)
	image = models.ImageField(
		upload_to=randomize_filename,
		blank=False,
		null=True,
	)
	created = models.DateTimeField(auto_now_add=True)
	
	
class Feedback(models.Model):
	FEEDBACK_CHOICES = (
		("1", "Positive"),
		("-1", "Negative"),
	)
	
	id = models.AutoField(primary_key=True)
	image = models.ForeignKey(
		Image,
		related_name='feedback',
		on_delete=models.PROTECT
	)
	type = models.CharField(
		max_length=10,
		choices=FEEDBACK_CHOICES,
		default="1"
	)
	created = models.DateTimeField(auto_now_add=True)


class PredictedImageDetails(models.Model):
	image = models.ForeignKey(
		Image,
		related_name='predicted_image_details',
		on_delete=models.PROTECT
	)
	faces = models.IntegerField(
		blank=False,
		null=False
	)
	faces_with_masks = models.IntegerField(
		blank=False,
		null=False
	)
	faces_with_masks_worn_improperly = models.IntegerField(
		blank=False,
		null=False
	)
	created = models.DateTimeField(auto_now_add=True)


class ActualImageDetails(models.Model):
	image = models.ForeignKey(
		Image,
		related_name='actual_image_details',
		on_delete=models.PROTECT
	)
	faces = models.IntegerField(
		blank=True,
		null=False
	)
	faces_with_masks = models.IntegerField(
		blank=True,
		null=False
	)
	faces_with_masks_worn_improperly = models.IntegerField(
		blank=False,
		null=False,
	)
	created = models.DateTimeField(auto_now_add=True)
