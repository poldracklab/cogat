from django.contrib.auth.models import User
username = 'admin'
password = 'adminpassword'
if not User.objects.get(username):
    User.objects.create_superuser(username=username, password=password, email='') 
else:
    msg = ("User {} already exists, update scripts/create_superuser.py if you "
           "would like a different superuser")
    print(msg.format(username))
