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
        if user and user.check_password(password):  
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class SessionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve all sessions for the authenticated user"""
        sessions = Session.objects.filter(user=request.user)
        serializer = SessionSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new session for the authenticated user"""
        session = Session.objects.create(user=request.user)
        serializer = SessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        """Retrieve all messages for a given session (must belong to user)"""
        session = get_object_or_404(Session, id=session_id, user=request.user)
        messages = Message.objects.filter(session=session)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, session_id):
        """Send a message within a session and trigger n8n workflow"""
        session = get_object_or_404(Session, id=session_id, user=request.user)

        # Get user message from request data
        content = request.data.get("content")
        if not content:
            return Response({"error": "Message content is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Store user message in the database
        message = Message.objects.create(session=session, content=content, sender="user")
        serializer = MessageSerializer(message)

        # Prepare data to send to n8n webhook
        data = {
            "sessionId": str(session.id),
            "userInput": content,
            "userId": str(request.user.id)
        }

        try:
            # Call n8n workflow to process the message
            response = requests.post(
                settings.N8N_WEBHOOK_URL,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            response_data = response.json()
        except requests.RequestException:
            return Response({"error": "Failed to connect to n8n"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": serializer.data, "n8n_response": response_data}, status=status.HTTP_201_CREATED)
