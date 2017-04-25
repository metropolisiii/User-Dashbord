from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import ModelForm
from dashboard.models import Profile
import requests
import json
from django.http import HttpResponse

class UploadPhotoForm(forms.Form):
	img = forms.ImageField(label='Select an image (Optimal Dimensions: 230 x 230)')

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30, widget=forms.TextInput(attrs={'class':'form-control', 'name':'username'}))
    password = forms.CharField(label="Password", max_length=30, widget=forms.PasswordInput(attrs={'class':'form-control', 'name':'password'}))
	
class UpdateInfoForm(ModelForm):
	class Meta:
		model = Profile
		fields = ['email','title','address','city','state','zip','phone', 'company','comments']
		
	def __init__(self, *args, **kwargs):
		if 'profiletype' in kwargs:
			self.profiletype = kwargs.pop('profiletype')
			super(UpdateInfoForm, self).__init__(*args, **kwargs)
			if self.profiletype == 'member':
				#Get companies from registration app and make them choices in a dropdown menu
				r = requests.get('https://apps.dash.com/account_registration/rest/member_companies/')
				r = r.json()
			
				companies = forms.ChoiceField(choices = r)
				self.fields['company'] = forms.ChoiceField(
					choices = [(company['account'], company['account']) for company in r]
				)
