from django.shortcuts import get_object_or_404
from django.conf import settings
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .models import User, Session, Message
from .serializers import UserSerializer, SessionSerializer, MessageSerializer

class UserView(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):  # Use check_password instead of authenticate
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class SessionView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id=None):
        if session_id:
            session = get_object_or_404(Session, id=session_id, user=request.user)
            serializer = SessionSerializer(session)
            return Response(serializer.data)
        sessions = Session.objects.filter(user=request.user)
        serializer = SessionSerializer(sessions, many=True)
        return Response(serializer.data)

    def post(self, request):
        session = Session.objects.create(user=request.user)
        serializer = SessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MessageView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        session = get_object_or_404(Session, id=session_id, user=request.user)
        messages = session.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, session_id):
        session = get_object_or_404(Session, id=session_id, user=request.user)

        message_content = request.data.get('message')
        if not message_content:
            return Response({"error": "Message content is required"}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            'sessionId': str(session_id),
            'userInput': message_content,
            'userId': str(request.user.id)
        }

        response = requests.post(
            settings.N8N_WEBHOOK_URL,
            json=data,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code != 200:
            return Response({"error": "n8n webhook call failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        Message.objects.create(session=session, content=message_content, sender='user')

        return Response(response.json(), status=status.HTTP_201_CREATED)
