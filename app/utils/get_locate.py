from flask import request

# get user location from cookies
def get_locale():
    language = request.cookies.get('language')
    if language is not None:
        return language
    if language == 'null':
        return 'en'  # default language
    return 'en'  # default language