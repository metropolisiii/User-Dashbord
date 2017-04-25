from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views
from dashboard.forms import LoginForm
from django.conf.urls.static import static

admin.autodiscover()

urlpatterns = [
	url(r'^admin/', include(admin.site.urls)),
	url(r'^', include('dashboard.urls')),
	url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    url(r'^logout/$', views.logout, {'next_page': '/login/'}),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
