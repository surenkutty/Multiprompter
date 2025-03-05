from django.urls import path, include
from .views import SessionView, MessageView, UserView, LoginView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register('users', UserView, basename='user')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('', include(router.urls)),
    path('sessions/', SessionView.as_view(), name='sessions'),
    path('sessions/<uuid:session_id>/', SessionView.as_view(), name='session_detail'),
    path('sessions/<uuid:session_id>/messages/', MessageView.as_view(), name='messages'),
    path('rest/token/', obtain_auth_token, name='api_token_auth'),
]
