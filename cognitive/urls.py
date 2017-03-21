from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from cognitive.apps.main import urls as main_urls
from cognitive.apps.users import urls as users_urls
from cognitive.apps.atlas import urls as atlas_urls
import cognitive.settings as settings

urlpatterns = [
    url(r'^', include(main_urls)),
    url(r'^', include(atlas_urls)),
    url(r'^accounts/', include(users_urls)),
    # enable this (and disable above) when ready to set up social auth
    #url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', admin.site.urls),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
