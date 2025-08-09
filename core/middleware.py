from django.utils import translation
from django.conf import settings

class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Check if user has a language preference
            if request.user.is_authenticated and hasattr(request.user, 'preferred_language'):
                language = request.user.preferred_language
                if language in [lang[0] for lang in settings.LANGUAGES]:
                    translation.activate(language)
                    request.LANGUAGE_CODE = language
        except Exception as e:
            # Log error but don't break the request
            print(f"Language middleware error: {e}")
        
        response = self.get_response(request)
        return response 