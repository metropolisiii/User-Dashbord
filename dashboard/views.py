from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import logout
from dashboard.utils import *
from dashboard.models import *
from dashboard.forms import *
import os.path
from dash.settings import USER_PHOTO_LOCATION, MAIL_NOTIFYEES
from django.http import JsonResponse
import requests
import json
import feedparser
from django.core.mail import send_mail

def Home(request):
	from django.contrib.auth import login	
	data = {}
	data['userphoto'] = "/static/images/blank_photo.png"	
	upload_photo_form = UploadPhotoForm()
	update_info_form = UpdateInfoForm()
	tv_token = ""
	subscriptions_data = json.dumps({})
	token = None
	data['quicklinks_column_size'] = 3
	
	if request.user.is_authenticated():
		data['quicklinks_column_size'] = 4
		#Get user information, specically the tokens. If none exist, the user must first login
		try:
			u = User.objects.get(username = request.user.username)
		except:
			return redirect('/login/')
		
		profile = Profile.objects.get(user=u)
		update_info_form = UpdateInfoForm(instance = profile, profiletype = u.profile.type)
		
		#Get yser profile information
		data['usertype'] = u.profile.type
		data['fullname'] = u.profile.firstname+" "+u.profile.lastname
		data['company'] = u.profile.company
		data['email'] = u.profile.email
		data['title'] = u.profile.title
		data['address'] = u.profile.address		
		data['address'] = data['address'] + ', ' + u.profile.city if data['address'] != "" and u.profile.city != "" else data['address']
		data['address'] = data['address'] + ', ' + u.profile.state if data['address'] != "" and u.profile.state != "" else data['address']
		data['address'] = data['address'] + ', ' + u.profile.zip if data['address'] != "" and u.profile.zip != "" else data['address']
		data['phone'] = u.profile.phone
		data['bio'] = u.profile.comments
		data['username'] = request.user
		
		#Get SSO tokens
		tv_token = u.profile.tv_token
		token = u.profile.token
		
		
		#check if photo exists. If it does, assign to data index. If not, use the blank icon
		photo_path = USER_PHOTO_LOCATION+request.user.username+".jpg"
		if os.path.isfile(photo_path):
			data['userphoto'] = "/static/user_photos/"+request.user.username+".jpg"	
			
		#Get the user's subscriptions. Must obtain an auth token first
		subscriptions_token = u.profile.subscriptions_token
		
		if u.profile.type != 'vendor':
			if subscriptions_token:
				try:
					subscriptions = requests.get(url+'subscriptions', headers={"Authorization":"Token "+subscriptions_token}, verify=False)				
				except:
					send_mail('Dashboard - EventRSS Did Not Load', 'EventRSS did not load', 'no-reply@dash.com', MAIL_NOTIFYEES)
					subscriptions = json.dumps({})
			else:
				subscriptions = json.dumps({})
			
			try:
				subscriptions_data = subscriptions.json()
			except:
				logout(request)
				return redirect("/")
				
	#Get Specification categories and doctypes
	specs_criteria = getSpecsCriteria()
	specs_categories = specs_criteria[0]
	doctypes = specs_criteria[1]
	
	#Get TV Videos
	if tv_token != "":
		r = requests.get('https://tv.dash.com/rest/media/', headers={"Authorization":"Token "+tv_token}, verify=False)
		
	else:
		r = requests.get('https://tv.dash.com/rest/media/', verify=False)
	
	try:
		tv = r.json()
	except:
		tv = json.dumps({})
		send_mail('Dashboard - TV Did Not Load', tv_token+' '+r.content, 'no-reply@dash.com', MAIL_NOTIFYEES)
	
	#Get Recent Events
	try:
		rss = feedparser.parse('http://www.dash.com/?feed=eventrss')
	except:
		rss = {}
		rss['entries'] = []
		send_mail('Dashboard - EventRSS Did Not Load', 'EventRSS did not load', 'no-reply@dash.com', MAIL_NOTIFYEES)
		
	#Get subscriptions information
	response = render(request, 'dashboard2.html', {'data': data, 'upload_photo_form':upload_photo_form, 'update_info_form':update_info_form, 'tv':tv, 'subscriptions':subscriptions_data, 'rss':rss, 'specs_categories':specs_categories, 'doctypes':doctypes})
	
	#Finalize Crowd SSO by setting cookie
	if token: 		
		response.set_cookie('crowd_token_key',token, domain='.dash.com', httponly=True)
	
	
	return response
	
#Save user image
def ImageSave(request):		
	if request.method == 'POST':
		form = UploadPhotoForm(request.POST, request.FILES)
		if form.is_valid():
			data = {}
			photo_new, created = Image.objects.get_or_create(username=request.user.username)
			photo_new.docfile = request.FILES['img']
			photo_new.save()
			
			with open ("/var/www/dash/static/user_photos/"+request.user.username+".jpg", 'rb') as file:
				fileContent = file.read()
				
			#Save to Active Directory
			userinfo = getUserInfo(request.user.username)
			l = initializeAD()
			try:
				l.modify_s(userinfo['dn'], [(ldap.MOD_REPLACE, 'thumbnailPhoto', [fileContent])])
			except ldap.LDAPError, error_message:
				log(request.user.username, "xxx", "LDAP Error changing thumbnailPhoto: %s" % error_message )
			return JsonResponse({'status':'success', 'url':"/static/user_photos/"+request.user.username+".jpg"})
		return JsonResponse({'status':'error', 'message':form.errors})
	return JsonResponse({'status':'error', 'message':'Invalid request'})
	
#Updates user information in Active Directory and Database
def UpdateInfo(request):
	if request.method == 'POST':
		try:
			u = User.objects.get(username = request.user.username)
		except:
			return redirect('/login/')
		profile = Profile.objects.get(user=u)
		form = UpdateInfoForm(request.POST, instance=profile, profiletype = profile.type)
		if form.is_valid():		
			form.save()
			data = form.cleaned_data
			#Save to Active Directory
			userinfo = getUserInfo(request.user.username)
			old_values = {'title':userinfo['title'], 'streetAddress':userinfo['address'],'l':userinfo['city'],'st':userinfo['state'],'postalCode':userinfo['zip'],'telephoneNumber':userinfo['phone'],'description':userinfo['comments']}
			new_values = {'title':data['title'], 'streetAddress':data['address'],'l':data['city'], 'st':data['state'],'postalCode':data['zip'],'telephoneNumber':data['phone'],'description':data['comments']}
			
			l = initializeAD()
		
			attrs = [
				(ldap.MOD_REPLACE, 'mail', [data['email'].encode("utf-8")]), 
			]
			attrs.append((ldap.MOD_REPLACE, 'title', [data['title'].encode("utf-8")])) if data['title'] != "" else attrs.append((ldap.MOD_REPLACE, 'title', ['-']))
			attrs.append((ldap.MOD_REPLACE, 'streetAddress', [data['address'].encode("utf-8")])) if data['address'] != "" in data else attrs.append((ldap.MOD_REPLACE, 'streetAddress', ['-']))
			attrs.append((ldap.MOD_REPLACE, 'l', [data['city'].encode("utf-8")])) if data['city'] != "" else attrs.append((ldap.MOD_REPLACE, 'l', ['-']))
			attrs.append((ldap.MOD_REPLACE, 'st', [data['state'].encode("utf-8")])) if data['state'] != "" else attrs.append((ldap.MOD_REPLACE, 'st', ['-']))
			attrs.append((ldap.MOD_REPLACE, 'postalCode', [data['zip'].encode("utf-8")])) if data['zip'] != "" else attrs.append((ldap.MOD_REPLACE, 'postalCode', ['-']))
			attrs.append((ldap.MOD_REPLACE, 'telephoneNumber', [data['phone'].encode("utf-8")])) if data['phone'] != "" else attrs.append((ldap.MOD_REPLACE, 'telephoneNumber', ['-']))
			attrs.append((ldap.MOD_REPLACE, 'description', [data['comments'].encode("utf-8")])) if data['comments'] != "" else attrs.append((ldap.MOD_REPLACE, 'description', ['-']))
			
			try:
				l.modify_s(userinfo['dn'], attrs)
			except ldap.LDAPError, error_message:
				log("Anonymous", "xxx", "LDAP Error Modifying User Info: %s" % error_message)
				return JsonResponse({'status':'error', 'message':'There was an error saving your profile.'})
			return JsonResponse({'status':'success'}) 
		return JsonResponse({'status':'error', 'message':form.errors})
	return JsonResponse({'status':'error', 'message':'Invalid request'})
	
def Login(request):
	from django.contrib.auth import authenticate, login
	data = {"error":False}
	
	if request.user.is_authenticated():
		return redirect('/')
	form = LoginForm()
	if request.method == 'POST':
		form = LoginForm(request.POST)
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None and user.is_active:
			login(request, user)
			return redirect('/')
		else:
			data['error'] = True

	return render(request, 'login.html', {'form':form, 'data':data})

			
	
def Logout(request):
	logout(request)
	r = requests.delete(CROWD_BASE_URL+'usermanagement/1/session/'+token, auth=(APP_USER, APP_PASS), headers={'Content-Type':'application/json', 'Accept':'application/json'} )
	return redirect('/')