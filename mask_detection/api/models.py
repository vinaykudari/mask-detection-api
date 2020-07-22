from django.db import models

# Create your models here.


class File(models.Model):
	image = models.ImageField(blank=False, null=True)
	created = models.DateTimeField(auto_now_add=True)
