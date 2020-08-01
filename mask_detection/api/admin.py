from django.contrib import admin

# Register your models here.
from .models import Image, PredictedImageDetails, ActualImageDetails

admin.site.register(Image)
admin.site.register(PredictedImageDetails)
admin.site.register(ActualImageDetails)
