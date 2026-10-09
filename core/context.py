from django.conf import settings
def brand(request): return {'demo_mode':settings.DEMO_MODE}
