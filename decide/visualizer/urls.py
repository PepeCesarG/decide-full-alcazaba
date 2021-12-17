from django.urls import path
from .views import *


urlpatterns = [
    path('<int:voting_id>/', VisualizerView.as_view()),
]
