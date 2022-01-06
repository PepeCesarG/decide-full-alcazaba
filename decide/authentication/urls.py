from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from .views import GetUserView, LogoutView, RegisterView,SigninView,ProfileView,LoginView


urlpatterns = [
    path('login/', obtain_auth_token),
    path('logout/', LogoutView.as_view()),
    path('getuser/', GetUserView.as_view()),
    path('register/', RegisterView.as_view()),
    path('sign-in/', SigninView.as_view()),
    path('profile/', ProfileView.as_view(), name="profile"),
    path('form-login/', LoginView.as_view()),
]
