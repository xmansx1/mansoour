from .models import SiteSettings

def site_settings(request):
    try:
        return {'site_settings': SiteSettings.objects.first()}
    except:
        return {'site_settings': None}
