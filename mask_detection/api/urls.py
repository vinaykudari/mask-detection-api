from django.conf.urls import url

from .views import MaskDetector
app_name = 'api'


urlpatterns = [
    url(r'predict/', MaskDetector.as_view(), name="predict"),
]
