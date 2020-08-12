from django.urls import path

from django.conf.urls import url
from django.urls import include

from rest_framework import routers

from . import views
from .viewsets import MaskDetectorViewSet

# app_name = 'api'
# router = routers.DefaultRouter()
# router.register('', MaskDetectorViewSet, basename='predict')

urlpatterns = [
    # url(r'^', include(router.urls)),
    path('predict/', views.MaskDetectionAPI.as_view(), name='predict'),
    path('get_stats/', views.GetStats.as_view(), name='get_stats')
]
