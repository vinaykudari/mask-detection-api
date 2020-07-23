from django.db import models

# Create your models here.


class Image(models.Model):
	id = models.AutoField(primary_key=True)
	image = models.ImageField(
		upload_to='images/',
		blank=False,
		null=True
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
