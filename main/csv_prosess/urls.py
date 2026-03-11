from django.urls import path

from . import views

urlpatterns = [
    path("", views.upload_report, name="upload_report"),
]
