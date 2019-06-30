from django.contrib.auth.models import User

try:
    User.objects.get(username="admin")
    print('True')
except User.DoesNotExist:
    print('False')