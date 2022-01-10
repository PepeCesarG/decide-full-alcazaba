from rest_framework import serializers
import os
from rest_framework.exceptions import AuthenticationFailed

from django.contrib.auth.models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_staff')

class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = google.Google.validate(auth_token)
        try:
            user_data['sub']
        except:
            raise serializers.ValidationError(
                'El token es invalido. Por favor prueba a logearte de nuevo'
            )

        if user_data['aud'] != "150285852294-dth6aoumllndds0h9fdfjt8dd5rcieeu.apps.googleusercontent.com":

            raise AuthenticationFailed('Quien eres?')

        user_id = user_data['sub']
        email = user_data['email']
        name = user_data['name']
        provider = 'google'

        return register_social_user(
            provider=provider, user_id=user_id, email=email, name=name)
