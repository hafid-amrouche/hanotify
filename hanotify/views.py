from django.http import JsonResponse
from django.contrib.auth.models import User 

def home(request):
    return JsonResponse({
        'message' : 'Home'
    }, status=200)

def checkUsername(request):
    username = request.GET.get('username').strip().lower()
    users_exist = User.objects.filter(username=username).exists()
    return JsonResponse({
        'username': username,
        'isValid': not users_exist
    }, safe=True)