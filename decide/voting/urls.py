from django.urls import path
from . import views


urlpatterns = [
    path('add/', views.VotingFormView.as_view(), name='voting'),
    path('add_question/', views.QuestionFormView.as_view(), name='voting'),
    path('', views.VotingView.as_view(), name='voting'),
    path('<int:voting_id>/', views.VotingUpdate.as_view(), name='voting'),
    path('success/', views.SuccessView.as_view(), name='voting'),
]
