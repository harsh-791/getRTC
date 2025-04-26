from django.urls import path
from . import views

urlpatterns = [
    path('process-image/', views.process_image, name='process_image'),
    path('screenshots/<int:record_id>/', views.get_screenshots, name='get_screenshots'),
] 