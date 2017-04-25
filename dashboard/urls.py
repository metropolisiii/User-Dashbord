from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView
from . import views
from forms import LoginForm

urlpatterns = [
	url(r'^$', views.Home),
	url(r'^login/$', views.Login),
	url(r'^image_save/$', views.ImageSave),
	url(r'^update_info/$', views.UpdateInfo)
]