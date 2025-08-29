from django.apps import AppConfig

class UsersConfig(AppConfig):  # change UsersConfig to your app's name
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'  # replace with your app name

    def ready(self):
        import users.signals  # import the signals
