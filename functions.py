import re
import hashlib
import re
from django.utils.text import slugify as django_slugify


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