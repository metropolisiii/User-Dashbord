from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from dashboard.utils import *
from dash.settings import USER_PHOTO_LOCATION

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	type = models.CharField(max_length=25)
	firstname = models.CharField(max_length=100)
	lastname = models.CharField(max_length=100)
	company = models.CharField(max_length=255)
	email = models.CharField(max_length=255)
	title = models.CharField(max_length=255,blank=True,null=True)
	address = models.CharField(max_length=500, blank=True,null=True, verbose_name="Street Address")
	city = models.CharField(max_length=255,blank=True,null=True)
	state = models.CharField(max_length=100, blank=True,null=True, verbose_name="State/Province")
	zip = models.CharField(max_length=15, blank=True,null=True, verbose_name="Postal/Zip Code")
	phone = models.CharField(max_length=20, blank=True,null=True, verbose_name="Telephone Number")
	comments = models.TextField(blank=True,null=True, verbose_name="Bio")
	tv_token = models.CharField(max_length=50, blank=True, null=True)
	subscriptions_token = models.CharField(max_length=500, blank=True, null=True)	
	token = models.CharField(max_length=25, blank=True, null=True)

def create_profile(sender, **kwargs):
	user = kwargs["instance"]
	if kwargs["created"]:
		u = getUserInfo(user.username, photo = True)
		
		profile = Profile(
			user=user, 
			type=u['type'], 
			firstname=u['firstname'], 
			lastname=u['lastname'],
			company=u['company'],
			email=u['email'],
			title=u['title'],
			address = u['address'],
			city = u['city'],
			state = u['state'],
			zip = u['zip'],
			phone = u['phone'],
			comments = u['comments']
		)
		profile.save()
post_save.connect(create_profile, sender=User)

def path_and_rename(instance, filename):
	import os.path
	filename = '{}.jpg'.format(instance.username)
	if os.path.isfile(USER_PHOTO_LOCATION+filename):
		os.remove(USER_PHOTO_LOCATION+filename)
	upload_to = USER_PHOTO_LOCATION
	# get filename
	
	
	# return the whole path to the file
	return os.path.join(upload_to, filename)
		
class Image(models.Model):
	docfile = models.ImageField(upload_to=path_and_rename, blank=True, null=True)
	username = models.CharField(max_length=255)
	def clean_image(self):
		image = self.cleaned_data.get('docfile',False)
		if image:
			if image._size > 100*1024:
				raise ValidationError("Image file too large ( > 4mb )")
			return image
		else:
			raise ValidationError("Couldn't read uploaded image")
	