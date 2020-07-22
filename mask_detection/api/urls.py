from django.conf.urls import url

from api.views import Predict
app_name = 'api'


urlpatterns = [
    url(r'predict/$', Predict.as_view(), name="predict"),
]
