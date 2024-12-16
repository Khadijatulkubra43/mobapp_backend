import re
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    username = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)  # Allow blank email

    def validate_username(self, value):
        # Check for spaces or disallowed characters
        if " " in value:
            raise serializers.ValidationError("Usernames cannot contain spaces.")
        if not re.match("^[a-zA-Z0-9_.-]+$", value):
            raise serializers.ValidationError(
                "Usernames can only contain letters, numbers, dots, underscores, and hyphens."
            )
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def save(self, request):
        # Call the parent save method to create the user
        user = super().save(request)
        
        # Set first_name and last_name
        user.first_name = self.validated_data.get('first_name', '')
        user.last_name = self.validated_data.get('last_name', '')
        
        # Allow blank email and handle appropriately
        email = self.validated_data.get('email', '')
        if email:
            user.email = email
        
        # Save the user instance with updated fields
        user.save()
        return user
