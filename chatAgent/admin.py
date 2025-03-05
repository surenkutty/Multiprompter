from django.contrib import admin
from .models import User, Session, Message

admin.site.register(User)
admin.site.register(Session)
admin.site.register(Message)

# Register your models here.
