from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from .views import GetUserView, LogoutView, RegisterView,SigninView,ProfileView,SignupView,ListUsers,GetUserDetails


urlpatterns = [
    path('login/', obtain_auth_token),
    path('logout/', LogoutView.as_view()),
    path('getuser/', GetUserView.as_view()),
    path('register/', RegisterView.as_view()),
    path('sign-in/', SigninView.as_view()),
    path('sign-up/', SignupView.as_view()),
    path('profile/', ProfileView.as_view(), name="profile"),
    path('getallusers/', ListUsers.as_view()),
    path('getuserdetails/<int:user_id>/', GetUserDetails.as_view()),
]
