from django import forms
from .import models

class LoginForm(forms.Form):
	username = forms.CharField(max_length = 35)
	password = forms.CharField(max_length = 35, widget = forms.PasswordInput)

	def clean_username(self):
		username = self.cleaned_data['username']
		if models.MyUser.objects.filter(username = username).count() != 1:
			raise forms.ValidationError('No such user exists.')
		return username


class ForgotPasswordForm(forms.Form):
	username = forms.CharField(max_length = 35)

	def clean_username(self):
		username = self.cleaned_data['username']

		if models.MyUser.objects.filter(username = username).count() != 1:
			raise forms.ValidationError('No such user exists.')
		return username


class ResetPasswordForm(forms.Form):
	newPassword = forms.CharField(max_length = 35, widget = forms.PasswordInput)
	confirmPassword = forms.CharField(max_length = 35, widget = forms.PasswordInput)

	def clean_confirmPassword(self):
		newPassword = self.cleaned_data['newPassword']
		confirmPassword = self.cleaned_data['confirmPassword']

		if confirmPassword != newPassword:
			raise forms.ValidationError('Two passwords dont match')
		return confirmPassword


class SignupForm(forms.Form):
	username 		= forms.CharField(max_length = 35)
	email 			= forms.EmailField(max_length = 35)
	firstName 		= forms.CharField(max_length = 35)
	middleName 		= forms.CharField(max_length = 35, required = False)
	lastName 		= forms.CharField(max_length = 35, required = False)
	password 		= forms.CharField(max_length = 35, widget = forms.PasswordInput)
	confirmPassword = forms.CharField(max_length = 35, widget = forms.PasswordInput)
	dob 			= forms.DateField(widget = forms.SelectDateWidget)

	def getYear(self):
		return self.cleaned_data['dob'].year

	def clean_username(self):
		username = self.cleaned_data['username']
		if models.MyUser.objects.filter(username = username).count() == 1:
			raise forms.ValidationError('Username already taken, try a different one.')
		return username

	def clean_password(self):
		password = self.cleaned_data['password']
		if len(password) < 5:
			raise forms.ValidationError('Password must be atleast 5characters long.')
		return password

	def clean_email(self):
		email = self.cleaned_data['email']

		if "@" not in email or ".com" not in email:
			raise forms.ValidationError('Enter a valid E-mail address.')
		return email

	def clean_confirmPassword(self):
		password = self.cleaned_data['password']
		confirmPassword = self.cleaned_data['confirmPassword']

		if password != confirmPassword:
			raise forms.ValidationError('The two passwords dont match.')
		return self.cleaned_data