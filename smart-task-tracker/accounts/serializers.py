from .models import User
from rest_framework import serializers
from .constants import USER_EXISTS_MESSAGE, EMAIL_EXISTS_MESSAGE
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password']
        
    def validate(self, data):
        email = data.get('email')
        username = data.get('username')

        if User.objects.filter(email=email, is_deleted=False).exists():
            raise serializers.ValidationError({"email": EMAIL_EXISTS_MESSAGE})

        if User.objects.filter(username=username, is_deleted=False).exists():
            raise serializers.ValidationError({"username": USER_EXISTS_MESSAGE})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']

class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])