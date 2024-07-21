import re

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