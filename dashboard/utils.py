import ldap
import requests
import json
from dashboard.models import *

""" Is the string a substring of another string in a list """
def isSubstringInList(l, str):
	for item in l:
		if item.find(str) > -1:
			return str	
			
""" Initialize Active Directory	"""	
def initializeAD(): 
	from dash.settings import AUTH_LDAP_SERVER_URI, AUTH_LDAP_BIND_DN, AUTH_LDAP_BIND_PASSWORD
	try:
		ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, 0)
		l = ldap.initialize(AUTH_LDAP_SERVER_URI)
		l.simple_bind_s(AUTH_LDAP_BIND_DN, AUTH_LDAP_BIND_PASSWORD)
		l.set_option(ldap.OPT_REFERRALS, ldap.OPT_OFF)
		l.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
		l.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
		l.set_option( ldap.OPT_X_TLS_DEMAND, False )
		l.set_option(ldap.OPT_NETWORK_TIMEOUT, 10.0)
		ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT,0)
	except ldap.LDAPError, e:
		print e
	return l
	
#Determine if a user is a vendor, member, employee, etc
def getUserType(user):	
	if 'memberOf' not in user[0][1]:
		return False
	if isSubstringInList(user[0][1]['memberOf'],'cl-members'):
		return "member"
	if isSubstringInList(user[0][1]['memberOf'],'cl-vendors'):
		return "vendor"
	if isSubstringInList(user[0][1]['memberOf'],'cl-employees'):
		return "employee"
	return False
	
#Gets the user's photo information from AD, stores the photo on the server, and returns the location of the photo
def storeUserPhoto(user):
	from dash.settings import USER_PHOTO_LOCATION
	
	if 'thumbnailPhoto' in user[0][1]: 		
		photo = user[0][1]['thumbnailPhoto'][0]
		with open(USER_PHOTO_LOCATION+user[0][1]['sAMAccountName'][0]+".jpg","wb") as fh:
			fh.write(photo)
	return False

def getUserInfo(username, photo = False):
	l=initializeAD()
	attrlist = ['sAMAccountName', 'memberOf','givenName','sn', 'company','mail','title','streetAddress','l','st','postalCode','telephoneNumber','description','dn']
	if photo:
		attrlist.append('thumbnailPhoto')
	user=l.search_ext_s("OU=community,DC=dash,DC=com", ldap.SCOPE_SUBTREE, "(sAMAccountName="+username+")", attrlist=attrlist)
	storeUserPhoto(user)
	firstname = user[0][1]['givenName'][0] if 'givenName' in user[0][1] else ""
	company = user[0][1]['company'][0] if 'company' in user[0][1] else ""
	email = user[0][1]['mail'][0] if 'mail' in user[0][1] else ""
	title = user[0][1]['title'][0] if 'title' in user[0][1] else ""
	address = user[0][1]['streetAddress'][0] if 'streetAddress' in user[0][1] else ""
	city = user[0][1]['l'][0] if 'l' in user[0][1] else ""
	state= user[0][1]['st'][0] if 'st' in user[0][1] else ""
	zip = user[0][1]['zip'][0] if 'zip' in user[0][1] else ""
	phone = user[0][1]['telephoneNumber'][0] if 'telephoneNumber' in user[0][1] else ""
	comments = user[0][1]['description'][0] if 'description' in user[0][1] else ""
	dn = user[0][0]
	
	return {
		'type':getUserType(user),
		'firstname':firstname,
		'lastname':user[0][1]['sn'][0],
		'company':company,
		'email':email,
		'title':title,
		'address':address,
		'city':city,
		'state':state,
		'zip':zip,
		'phone':phone,
		'comments':comments,
		'dn':dn
	}
	

""" Logs a message to a log file """
def log(userID, ip, message):
	from django.core.files import File
	from dash.settings import LOGFILE
	import time

	t = time.strftime("%c")
	with open(LOGFILE, 'a') as f:
		logfile = File(f)
		logfile.write(t + '\t' + message.encode('utf-8') + '\n')
		logfile.close
		
def getCrowd(request):
	import requests
	from dash.settings import CROWD_BASE_URL, APP_USER, APP_PASS
		
	token = request.COOKIES.get('crowd_token')
	if token:
		r = requests.get(CROWD_BASE_URL+'usermanagement/1/session/'+token, auth=(APP_USER, APP_PASS), headers={'Content-Type':'application/json', 'Accept':'application/json'} )
		return r
	return None
	
def getSpecsCriteria():	
	from dash.settings import ZZ_ALFRESCO_PASS
	
	specs = requests.get(url, auth=('zz_alfresco',ZZ_ALFRESCO_PASS), verify=False) 
	doctypes = requests.get(url, auth=('zz_alfresco',ZZ_ALFRESCO_PASS), verify=False )
	doctypes = doctypes.text.split('\n')
	return (specs.text, doctypes)
	
def processTVToken(user, password, token):
	from dashboard.models import Profile
	#Get tv token and store in database
	tv_token = requests.post('https://tv.dash.com/api-token-auth/', headers={'Content-Type':'application/json', 'Accept':'application/json'}, json = {'username':user.username, 'password':password}, verify = False)
	c = tv_token.json()
	profile = Profile.objects.get(user = user)
	profile.tv_token = c['token']
	profile.token = token
	profile.save()	
	
def processSubscriptionsToken(user, password):
	from dashboard.models import Profile
	#Get subscriptions token and store in database
	subscriptions_token = requests.post('https://community.dash.com/subscriptions/rest/authenticate', auth=(user.username, password), verify = False)
	if subscriptions_token.status_code == 200:
		s = subscriptions_token.json()
		profile = Profile.objects.get(user = user)
		profile = Profile.objects.get(user = user)
		profile.subscriptions_token = s['jwt']
		profile.save()
	
def processTokens(user, password, token):
	processTVToken(user, password, token)
	processSubscriptionsToken(user, password)
	