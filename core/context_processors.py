from django.conf import settings
from django.utils import translation

def language_info(request):
    """Add language information to template context"""
    try:
        return {
            'LANGUAGE_CODE': translation.get_language(),
            'LANGUAGES': settings.LANGUAGES,
            'CURRENT_LANGUAGE': dict(settings.LANGUAGES).get(translation.get_language(), 'English'),
        }
    except Exception as e:
        # Return default values if there's an error
        print(f"Context processor error: {e}")
        return {
            'LANGUAGE_CODE': 'en',
            'LANGUAGES': settings.LANGUAGES,
            'CURRENT_LANGUAGE': 'English',
        } 