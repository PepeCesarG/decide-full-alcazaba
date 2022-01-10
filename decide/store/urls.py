from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.StoreView.as_view(), name='store'),
    path('store-bot/', views.StoreBotView.as_view()),
]
