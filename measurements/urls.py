# from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('',calculate_distance_view,name="calaculate-view")
    
]