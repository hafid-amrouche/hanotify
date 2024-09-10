import re, hashlib, re, requests
from django.utils.text import slugify as django_slugify
from django.utils import timezone


def is_acceptable_string(s):
    # Define the regex pattern to allow only Latin letters, numbers, and specified special characters
    pattern = r"^[A-Za-z0-9@\-_.]+$"
    
    # Compile the regex pattern
    regex = re.compile(pattern)
    
    # Test if the entire string matches the regex pattern
    return bool(regex.match(s))


def is_only_latin_and_arabic_letters(s):
    # Define the regex pattern for Latin and Arabic letters
    pattern = r"^[A-Za-z\u00C0-\u00FF\u0100-\u017F\u0180-\u024F\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+$"
    
    # Compile the regex pattern
    regex = re.compile(pattern)
    
    # Test if the entire string matches the regex pattern
    return bool(regex.match(s))

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def generate_token_from_id(id_value):
    # Convert the ID to a string if it's not already
    id_str = str(id_value)
    
    # Hash the ID using SHA-256
    hashed_id = hashlib.sha256(id_str.encode()).hexdigest()
    
    return hashed_id

def ship_to(company_name, order):
    pass

def custom_slugify(value):
    # Convert spaces or underscores to hyphens
    value = re.sub(r'[\s_]+', '-', value)
    
    # Remove any characters that aren't alphanumeric, hyphens, or Arabic characters
    value = re.sub(r'[^\w\u0621-\u064A-]+', '', value, flags=re.UNICODE)
    
    # Slugify using Django's default slugify
    return django_slugify(value, allow_unicode=True)

def hash_data(data):
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def send_event_to_facebook(event_name, FACEBOOK_PIXEL_ID, FACEBOOK_ACCESS_TOKEN, event_data):
    url = f"https://graph.facebook.com/v14.0/{FACEBOOK_PIXEL_ID}/events"

    user_data = {
        'ph': hash_data(event_data.get('phone', '')),
        'fn': hash_data(event_data.get('first_name', '')),
        'ln': hash_data(event_data.get('last_name', '')),
        'ct': hash_data(event_data.get('city', '')),
        'st': hash_data(event_data.get('state', '')),
        'country': hash_data(event_data.get('country', '')),
        'client_ip_address' : event_data.get('client_ip_address', '')
    }
    
    payload = {
        'data': [{
            'event_name': event_name,
            'event_time': int(timezone.now().timestamp()),
            'user_data': user_data,
            'custom_data': event_data.get('custom_data', {}),
        }],
        'access_token': FACEBOOK_ACCESS_TOKEN,
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    print('HOOOOOOOOOOOOOOOOOO')
    return response.json()