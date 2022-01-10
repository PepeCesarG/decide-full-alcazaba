from django.urls import path
from .views import *


urlpatterns = [
    path('<int:voting_id>/', VisualizerView.as_view()),
    path('<int:voting_id>/graficos', VisualizerView2.as_view(), name='graficos'),
    path('all', VisualizerGetAll.as_view()),
    path('allCensus', VisualizerGetAllCensus.as_view()),
    path('allUsers', VisualizerGetAllUsers.as_view()),
    path('<int:voting_id>/pdf', VisualizerView3.as_view(), name = 'pdf'),
    path('details/<int:voting_id>', VisualizerDetails.as_view()),
]
