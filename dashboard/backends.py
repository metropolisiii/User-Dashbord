from django.conf import settings
from django.contrib.auth.models import User
import requests
import json
from dash.settings import APP_USER, APP_PASS, CROWD_AUTH_GROUPS, CROWD_BASE_URL
from dashboard.models import processTokens

# Crowd authenticator
class KirbyCrowd:
	def authenticate(self, username=None, password=None):
		url = CROWD_BASE_URL+'usermanagement/1/session'
		params = {"username":username, "password":password}
			
		#Credentials authentication
		r = requests.post(url, json=params, auth=(APP_USER, APP_PASS), headers={'Content-Type':'application/json', 'Accept':'application/json'})		
		userinfo = r.json()
		if r.status_code == 200 or r.status_code == 201:		
			#Find out if user is in an authorized group
			r = requests.get(CROWD_BASE_URL+'usermanagement/1/user/group/direct?username='+username, auth=(APP_USER, APP_PASS), headers={'Content-Type':'application/json', 'Accept':'application/json'})
			if r.status_code == 200 or r.status_code == 201:
				response = r.json()
				for group in response['groups']:
					if group['name'] in CROWD_AUTH_GROUPS:
						#If user is authorized, create user
						user, created = User.objects.get_or_create(username=username, is_active=True)
						token = userinfo['token']						
						processTokens(user, password, token)
						return user
		return None
		
	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None
			
	