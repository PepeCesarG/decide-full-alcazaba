from django.urls import path, include
from . import views, admin


urlpatterns = [
    path('', views.CensusCreate.as_view(), name='census_create'),
    path('voters/', views.VoterCreate.as_view(), name='voter_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
    path('import-csv/', views.CensusCreate.as_view(), name='census_csv_import'),
]
