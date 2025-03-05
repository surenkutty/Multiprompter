from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User,Session, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}  

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])  # Hash password before saving
        return super().create(validated_data)

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'