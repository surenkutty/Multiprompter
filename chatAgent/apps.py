from django.apps import AppConfig


class ChatagentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatAgent'
    
    def ready(self):
        import chatAgent.signals 
