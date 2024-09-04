from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from others.models import State
from .serializers import UserSerializerWithToken
from django.contrib.auth.hashers import make_password
import json, os
from django.db.models import Q
from django.db.models import Avg
from django.utils.translation import gettext as _
from user.models import UserToken
import json
from django.contrib.auth import authenticate
from django.contrib.auth.models import User 
from functions import is_acceptable_string, is_only_latin_and_arabic_letters
from time import sleep
from store.models import StateShippingCost, Domain
from contants import media_files_domain, stores_domain
import requests
from django.conf import settings
from store.models import Store

@api_view(['POST'])
def login(request):
    
    data = json.loads(request.body)
    username= data.get('username').lower()
    password = data.get('password')
    user = authenticate(request, username=username, password=password)
    if not user:
        message = {'detail': _('There is no user with this username and password.')}
        return JsonResponse(message, status=400)
    serializer = UserSerializerWithToken(user).data
    UserToken.objects.create(
        user = user,
        token = serializer['token']
    )
    return Response(serializer)

@api_view(['POST'])
def register(request):
    
    try :
        data = json.loads(request.body)
        first_name = data['first_name']
        last_name = data['last_name']
        username = data['username'].lower()
        password = data['password']
        confirmPassword = data['password']
        if len(first_name) < 3 or not(is_only_latin_and_arabic_letters(first_name)) :
            message = {'detail': _('First name is not acceptable')}
            return JsonResponse(message, status=400)
        
        elif len(last_name) < 3 or not(is_only_latin_and_arabic_letters(last_name))  :
            message = {'detail': _('Last name is not acceptable')}
            return JsonResponse(message, status=400)
        
        elif username=='' or (not is_acceptable_string(username)) :
            message = {'detail': _('Username is not acceptable')}
            return JsonResponse(message, status=400)
        
        elif User.objects.filter(username=username) :
            message = {'detail': _('This username {} is taken try another one').format(username)}
            return JsonResponse(message, status=400)
        
        elif password == '':
            message = {'detail': _('Password cannot be empty')}
            return JsonResponse(message, status=400)
        
        elif len(password) < 8 :
            message = {'detail': _('Password should have at least 8 characters')}
            return JsonResponse(message, status=400)
        
        elif not is_acceptable_string(password) :
            message = {'detail': _('Password is not acceptable')}
            return JsonResponse(message, status=400)
        
        elif password != confirmPassword:
            message = {'detail': _('Passwords Do not match')}
            return JsonResponse(message, status=400)
        
        user = User.objects.create(
            first_name=first_name,
            last_name = last_name,
            username=username,
            password=make_password(password)
        )
        store = Store.objects.create(owner=user)
      
        store_domain = Domain.objects.create(
            store=store,
            domain = f'store-{store.id}.{stores_domain}'
        )

        shipping_costs = [StateShippingCost(
            store= store,
            state_id = state_id,
        ) for state_id in range(1, 59)]
        StateShippingCost.objects.bulk_create(shipping_costs)
        userData = UserSerializerWithToken(user, many=False).data

        receiver_url = media_files_domain + '/make-user-directory'
        response = requests.post(receiver_url,{
            'store': json.dumps({
                'domain': store_domain.domain,
                'id': store.id,
                'logo': None,
                'bordersRounded': True,
                'primaryColor': store.color_primary,
                'name': '',
                'description': '',
            }),
            'user_id': user.id,
            'MESSAGING_KEY': settings.MESSAGING_KEY
        })
        print(response)
        if not response.ok:
            message = {
                'detail': _('User was not created please try again'),
                'error 1': ''
            }
            return JsonResponse(message, status=400)
        return Response(userData)
    
    except Exception as e:
        print('Error at hontify/user/views/register l122')
        try:
            user.delete()
        except :
            print('Error at hontify/user/views/register l126')
        message = {
            'detail': _('User was not created please try again'),
            "error 2": str(e)
            }
        return JsonResponse(message, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    
    data = json.loads(request.body)
    try :
        token = data.get('token')
        UserToken.objects.get(token=token, user=request.user).delete()
    except Exception as e:
        print(e)
        pass
    return JsonResponse({'detail': 'TOKEN_NOT_DELETED'})