from django.conf.urls import include
from django.urls import re_path
from django.contrib import admin

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'', include('library.urls')),
    re_path(r'^', include('library.urls')),
]
handler404 = "library.views.page_not_found_view"