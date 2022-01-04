from django.urls import path
from .views import *


urlpatterns = [
    path('<int:voting_id>/', VisualizerView.as_view()),
    path('<int:voting_id>/graficos', VisualizerView2.as_view(), name='graficos'),
    path('<int:voting_id>/pdf', VisualizerView3.as_view(), name = 'pdf'),
]
