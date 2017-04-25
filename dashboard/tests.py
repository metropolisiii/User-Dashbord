from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from dashboard.models import *

class AuthenticationTestCases(TestCase):
	def setUp(self):
		self.c = Client()
		user = User.objects.create(username='employee-test', password='12345', first_name='Employee', last_name='Test', email='etest@dash.com')
		profile = Profile.objects.get(user = user)
		profile.type='employee'
		profile.save()
		with open('testpass.txt') as f:
			self.password = f.read().strip()
		
	#User goes to login page
	def test_user_goes_to_login_page(self):
		response = self.c.get('/login/')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Username")
		self.assertContains(response, "Password")

	# Employee successfully logs in
	def test_employee_successfully_logs_in(self):
		response = self.c.post("/login/", {'username':'employee-test', 'password':self.password})
		self.assertEqual(response.status_code, 302)
	
	# Member successfully logs in
	def test_member_successfully_logs_in(self):
		response = self.c.post("/login/", {'username':'membertest', 'password':self.password})
		self.assertEqual(response.status_code, 302)
		

	# Vendor successfully logs in
	def test_vendor_successfully_logs_in(self):
		response = self.c.post("/login/", {'username':'vendortest', 'password':self.password})
		self.assertEqual(response.status_code, 302)
		
		
	# User login is unsuccessful
	def test_user_login_is_unsuccessful(self):
		response = self.c.post("/login/", {'username':'vendortest', 'password':'not_correct'})
		self.assertContains(response, "Your username and password didn't match")
		response = self.c.get("/")
		session = self.c.session
		self.assertEqual('usertype' not in session, True)

	# Unauthorized user tries to log in
	def test_unauthorized_user_tries_to_log_in(self):
		response = self.c.post("/login/", {'username':'contractor-test', 'password':'not_correct'})
		self.assertContains(response, "Your username and password didn't match")
		response = self.c.get("/")
		session = self.c.session
		self.assertEqual('usertype' not in session, True)

	# User logs out
	def test_user_logs_out(self):
		response = self.c.post("/login/", {'username':'vendortest', 'password':self.password})
		response = self.c.get("/logout/")
		response = self.c.get("/")
		session = self.c.session
		self.assertEqual('usertype' not in session, True)

		

# Home test
class HomepageTests(TestCase):
	def setUp(self):
		self.c = Client()
		with open('testpass.txt') as f:
			self.password = f.read().strip()
				
	# Unauthorized user goes to home page
	def test_unauthenticated_user_goes_to_home_page(self):
		response = self.c.get('/')
		self.assertContains(response, "<a class=\"btn btn-info\" href=\"/login/\">Log in</a>")
		self.assertContains(response, "/static/images/blank_photo.png")
		self.assertNotContains(response, "Subscriptions")

	# Member goes to dashboard
	def test_member_goes_to_dashboard(self):		
		self.c.login(username='membertest', password=self.password)
		response = self.c.get('/')
		self.assertContains(response, "Hello Member Tester,")
		self.assertContains(response, "blank_photo.png")
		self.assertContains(response, "Company: ")
		self.assertContains(response, "membertester@dash.com")
		self.assertContains(response, "Member Docs")
		
	# Vendor goes to dashboard
	def test_vendor_goes_to_dashboard(self):
		self.c.login(username='vendortest', password=self.password)
		response = self.c.get('/')
		self.assertContains(response, "Hello Vendor Tester,")
		self.assertContains(response, "blank_photo.png")
		self.assertContains(response, "Company: ")
		self.assertContains(response, "vendortester@dash.com")
		self.assertContains(response, "Vendor Docs")

	# Employee goes to dashboard
	def test_employee_goes_to_dashboard(self):
		self.c.login(username='employee-test', password=self.password)
		response = self.c.get('/')
		self.assertContains(response, "Hello Employee Test,")
		self.assertContains(response, "employee-test.jpg")
		self.assertContains(response, "Company: dash")
		self.assertContains(response, "employee-test@dash.com")
		self.assertContains(response, "Employee Docs")
		
# Update Info TestCase
class UpdateInfoTests(TestCase):
	def setUp(self):
		self.c = Client()
		with open('testpass.txt') as f:
			self.password = f.read().strip()
	
	# User goes to edit info
	def test_user_goes_to_edit_info(self):
		self.c.login(username='employee-test', password=self.password)
		response = self.c.get('/')
		self.assertContains(response, 'value="employee-test@dash.com"')
	
	# User is missing required fields
	def test_user_is_missing_a_required_field(self):
		self.c.login(username='employee-test', password=self.password)
		response = self.c.post('/update_info/',{})
		self.assertContains(response, 'error')



# Subscriptions Tests
# User has subscriptions
# User subscribes to new subscription
# Employee sends subscription
# User removes subscription

# Majordomo Tests
# User has working groups
# User subscribes to new working group

# Conferences Tests
# Conferences are happening for members
# Conferences are happening for vendors
# Member registers for Conference
# Vendor registers for Conference

