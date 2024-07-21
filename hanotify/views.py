
from json_files.states import states
from json_files.cities import cities
from others.models import State, City
from django.http import JsonResponse
from django.contrib.auth.models import User 
from rest_framework.decorators import api_view, permission_classes


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