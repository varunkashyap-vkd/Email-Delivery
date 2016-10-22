from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import render, get_object_or_404, redirect, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST,require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .import models, forms
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.http import JsonResponse
from account import models as AccountModels
from mail import models as MailModels
from django.db.models import Max
from django.db import connection
from django.conf import settings
import os
from django.db.models import Q
from shutil import copyfile



							#Left navigation bar functionality start.
@require_http_methods(['GET', 'POST'])
@login_required
def sendMail(request):
	if request.method == 'GET':
		f = forms.SendMailForm()
		return HttpResponse(render(request, 'mail/sendMail.html', {'f' : f, 'heading' : 'Send an Email'}))

	f = forms.SendMailForm(request.POST, request.FILES)

	if not f.is_valid():
		return HttpResponse(render(request, 'mail/sendMail.html', {'f' : f, 'heading' : 'Send an Email'}))	
		
	recepients 		= f.cleaned_data['to'].split(", ")
	for r in recepients:
		if AccountModels.MyUser.objects.filter(username = r).count() != 1:
			string = "You entered some invalid usernames."
			context = {'message' : string, 'link' : reverse('sendMail'), 'title' : 'Back'}
			return HttpResponse(render(request, 'common/success_LoggedIn.html', context))

	subject 		= f.cleaned_data['subject']	
	body 			= f.cleaned_data['body']
	sender 			= request.user
	attachment 		= f.cleaned_data['attachment']

	newMessage = MailModels.Message.objects.create(subject = subject, body = body, sender = sender, attachment = attachment)
	newMessage.save()

	for username in recepients:
		receiver = AccountModels.MyUser.objects.get(username = username)
		obj = AccountModels.Receives.objects.create(receiver = receiver, message = newMessage)
		obj.save()

	string = 'Your message has been sent.'
	context = {'message' : string, 'link' : reverse('home', kwargs = {'id' : request.user.userID}), 'title' : 'Home'}
	return HttpResponse(render(request, 'common/success_LoggedIn.html', context))


@require_http_methods(['GET', 'POST'])
@login_required
def sentMail(request):
	allSent = MailModels.Message.objects.filter(Q(sender = request.user),  Q(isDraft = False), Q(status = '1')).order_by('-dateTime')
	final = []

	for item in allSent:
		recipients = item.received_by.all()
		receivers = ''
		for r in recipients:
			receivers += r.username + ', '

		obj = {
			'message' : item,
			'receivers' : receivers[:-2]
		}
		final.append(obj)

	return HttpResponse(render(request, 'mail/sentMail.html', {'list' : final}))


@require_http_methods(['GET', 'POST'])
@login_required
def drafts(request):
	allDrafts = MailModels.Message.objects.filter(Q(sender = request.user), Q(isDraft = True), Q(status = '1')).order_by('-dateTime')
	context = {'drafts' : allDrafts}
	return HttpResponse(render(request, 'mail/drafts.html', context))


@require_http_methods(['GET', 'POST'])
@login_required
def profile(request):
	sentMails = models.Message.objects.filter(sender = request.user, isDraft = False)
	count = sentMails.count()

	allReceived = request.user.receivedMessages.all()
	receivedCount = allReceived.count()
	lastSentDate = sentMails.aggregate(Max('dateTime'))['dateTime__max']
	lastReceivedDate = allReceived.aggregate(Max('dateTime'))['dateTime__max']
	draftsCount = MailModels.Message.objects.filter(Q(sender = request.user), Q(isDraft = True), Q(status = '1')).count()

	context = {'sentMailsCount' : count, 'receivedMailsCount' : receivedCount, 'lastSentDate' : lastSentDate, 'lastReceivedDate' : lastReceivedDate, 'draftsCount' : draftsCount}
	return HttpResponse(render(request, 'mail/profile.html', context))


@require_http_methods(['GET', 'POST'])
@login_required
def trash(request):
	inbox = MailModels.Message.objects.filter(receives__receiver = request.user, receives__status = '0').order_by('-dateTime')
	sentMail = MailModels.Message.objects.filter(sender = request.user, status = '0', isDraft = False).order_by('-dateTime')
	draft = MailModels.Message.objects.filter(sender = request.user, isDraft = True, status = '0').order_by('-dateTime')
	sentList = []
	for item in sentMail:
		receivedBy = item.received_by.all()
		receivers = ''
		for r in receivedBy:
			receivers += r.username + ', '
		obj = {'message' : item, 'receivers' : receivers[:-2]}
		sentList.append(obj)

	return HttpResponse(render(request, 'mail/trash.html', {'inbox' : inbox, 'sentMail' : sentList, 'draft' : draft}))
							#Left navigation bar functionality end.



							#Message options functionality start.
@require_http_methods(['GET', 'POST'])
@login_required
def reply(request, targetUserID):
	if request.method == 'GET':
		recepient = AccountModels.MyUser.objects.get(userID = targetUserID).username
		context = {'f' : forms.SendMailForm({'to' : recepient}), 'heading' : 'Send a Reply'}
		return HttpResponse(render(request, 'mail/sendMail.html', context))

	f = forms.SendMailForm(request.POST, request.FILES)
	if not f.is_valid():
		recepient = AccountModels.MyUser.objects.get(userID = targetUserID).username
		context = {'f' : f, 'heading' : 'Send a Reply'}
		return HttpResponse(render(request, 'mail/sendMail.html', context))

	if AccountModels.MyUser.objects.filter(userID = targetUserID).count() != 1:
		string = "You entered some invalid usernames."
		context = {'message' : string, 'link' : reverse('sendMail'), 'title' : 'Back'}
		return HttpResponse(render(request, 'common/success_LoggedIn.html', context))

	recepientUser 	= AccountModels.MyUser.objects.get(userID = targetUserID)
	subject 		= f.cleaned_data['subject']	
	body 			= f.cleaned_data['body']
	sender 			= request.user
	attachment 		= f.cleaned_data['attachment']

	newMessage = MailModels.Message.objects.create(subject = subject, body = body, sender = sender, attachment = attachment)
	newMessage.save()
	obj = AccountModels.Receives.objects.create(receiver = recepientUser, message = newMessage)
	obj.save()
	string = 'Your reply has been sent.'
	context = {'message' : string, 'link' : reverse('home', kwargs = {'id' : request.user.userID}), 'title' : 'Home'}
	return HttpResponse(render(request, 'common/success_LoggedIn.html', context))


@require_http_methods(['GET', 'POST'])
@login_required
def forward(request, messageID):
	if request.method == 'GET':
		message = models.Message.objects.get(messageID = messageID)
		obj = {'subject' : message.subject, 'body' : message.body}
		fileObject = {'attachment' : message.attachment}
		context = {'f' : forms.SendMailForm(obj, fileObject), 'heading' : 'Forward this message', 'fromForward' : '1'}
		return HttpResponse(render(request, 'mail/sendMail.html', context))

	f = forms.SendMailForm(request.POST, request.FILES)
	if not f.is_valid():
		context = {'f' : f, 'heading' : 'Forward this message'}
		return HttpResponse(render(request, 'mail/sendMail.html', context))

	recepientUser 	= AccountModels.MyUser.objects.get(username = f.cleaned_data['to'])
	sender 			= request.user
	subject 		= f.cleaned_data['subject']	
	body 			= f.cleaned_data['body']
	attachment 		= f.cleaned_data['attachment']

	newMessage = MailModels.Message.objects.create(subject = subject, body = body, sender = sender, attachment = attachment)
	newMessage.save()
	obj = AccountModels.Receives.objects.create(receiver = recepientUser, message = newMessage)
	obj.save()
	string = 'Your message has been forwarded.'
	context = {'message' : string, 'link' : reverse('home', kwargs = {'id' : request.user.userID}), 'title' : 'Home'}
	return HttpResponse(render(request, 'common/success_LoggedIn.html', context))


@require_http_methods(['GET', 'POST'])
@csrf_exempt
@login_required
def saveDraft(request):
	subject = request.POST['subject'] 
	body = request.POST['body']
	attachment = request.FILES.get('attachment')

	if len(subject) == 0 or len(body) == 0:
		string = "'Subject' and 'Body' fields can not be left blank while saving a draft."
		return JsonResponse({'response' : string, 'result' : 'blankFields'})

	if MailModels.Message.objects.filter(sender = request.user, subject = subject, body = body, isDraft = True).count() >= 1:
		string = 'You can not save two drafts having identical values for subject and body.'
		return JsonResponse({'response' : string, 'result' : 'duplicate'})

	newMessage = MailModels.Message.objects.create(subject = subject, body = body, sender = request.user, isDraft = True, attachment = attachment)
	newMessage.save()
	string = 'Draft saved successfully.'
	return JsonResponse({'response' : string, 'result' : 'success'})


@require_http_methods(['GET', 'POST'])
@csrf_exempt
@login_required
def downloadImage(request):
	sourceAddress = request.GET.get('address')
	
	imageName =	sourceAddress.split('/')[-1]
	targetAddress = '/home/varun/Downloads/' + imageName 

	os.system('touch ' + targetAddress)
	copyfile(sourceAddress, targetAddress)
	return JsonResponse({'response' : targetAddress})
							#Message options functionality end.



							#Viewing functionality start.
@require_http_methods(['GET', 'POST'])
@login_required
def viewInboxMessage(request, messageID):
	message = models.Message.objects.get(messageID = messageID)
	receivers = message.received_by.all()
	string = ''
	for r in receivers:
		string += r.username + ', '

	allReceived = request.user.receivedMessages.filter(receives__status = '1').order_by('-dateTime')
	context = {'message' : message, 'allReceived' : allReceived, 'recepients' : string[:-2]}
	return HttpResponse(render(request, 'mail/viewInboxMessage.html', context))	


@require_http_methods(['GET', 'POST'])
@login_required
def viewSentMailMessage(request, messageID):
	message = models.Message.objects.get(messageID = messageID)
	receivers = message.received_by.all()
	string = ''
	for r in receivers:
		string += r.username + ', '

	context = {'message' : message, 'recepients' : string[:-2], 'outbox' : True}
	return HttpResponse(render(request, 'mail/viewSentMailMessage.html', context))


@require_http_methods(['GET', 'POST'])
@login_required
def viewDraft(request, draftID):
	message = MailModels.Message.objects.get(messageID = draftID)
	return HttpResponse(render(request, 'mail/viewDraftMessage.html', {'message' : message}))


@require_http_methods(['GET', 'POST'])
@login_required
def viewTrashMessage(request, messageID):
	message = MailModels.Message.objects.get(messageID = messageID)
	receivers = message.received_by.all()
	string = ''
	for r in receivers:
		string += r.username + ', '

	return HttpResponse(render(request, 'mail/viewTrashMessage.html', {'message' : message, 'recepients' : string[:-2]}))
							#Viewing functionality end.



							#Delete functionality start.
@require_http_methods(['GET', 'POST'])
@login_required
def deleteFromInbox(request, messageID):
	message = MailModels.Message.objects.get(messageID = messageID)

	if not message:
		return HttpResponse('Invalid access.')

	obj = AccountModels.Receives.objects.get(receiver = request.user, message = message)
	obj.status = '0'
	obj.save()
	string = 'This message has been deleted.'
	context = {'message' : string, 'link' : reverse('home', kwargs= {'id' : request.user.userID}), 'title' : 'Back to Inbox'}
	return HttpResponse(render(request, 'common/success_LoggedIn.html', context))


@require_http_methods(['GET', 'POST'])
@login_required
def deleteFromOutbox(request, messageID):
	message = MailModels.Message.objects.get(messageID = messageID)

	if not message:
		return HttpResponse('Invalid access.')

	message.status = '0'
	message.save()
	string = 'This message has been deleted.'
	context = {'message' : string, 'link' : reverse('sentMail'), 'title' : 'Back to Sent Mail'}
	return HttpResponse(render(request, 'common/success_LoggedIn.html', context))


@require_http_methods(['GET', 'POST'])
@login_required
def deleteFromDraft(request, messageID):
	message = MailModels.Message.objects.get(messageID = messageID, isDraft = True)

	if not message:
		return HttpResponse('Invalid access.')

	message.status = '0'
	message.save()
	string = 'This message has been deleted.'
	context = {'message' : string, 'link' : reverse('drafts'), 'title' : 'Back to Drafts.'}
	return HttpResponse(render(request, 'common/success_LoggedIn.html', context))
							#Delete functionality end.




@require_http_methods(['GET', 'POST'])
@login_required
def getMessage(request, messageID):
	message = models.Message.objects.get(messageID = messageID)
	receivers = message.received_by.all()
	string = ''
	for r in receivers:
		string += r.username + ', '

	url = ''
	path = ''
	if message.attachment:
		url = message.attachment.url
		path = message.attachment.path

	returnObject = {'recipients' : string[:-2], 'from' : message.sender.username, 'on' : str(message.dateTime), 'subject' : message.subject, 'url' : url, 'body' : message.body, 'path' : path, 'messageID' : message.messageID, 'senderID' : message.sender.userID}
	return JsonResponse({'response' : returnObject})


@require_http_methods(['GET', 'POST'])
@login_required
def restore(request, messageID):
	message = MailModels.Message.objects.get(messageID = messageID)
	string = ''

	if message.sender == request.user:
		message.status = '1'
		message.save()
		if message.isDraft == False:
			string = "This message has been restored in 'Sent Mail'."

		else:
			string = "This message has been restored in 'Drafts'."
		
	else:
		obj = AccountModels.Receives.objects.get(receiver = request.user, message = message)
		obj.status = '1'
		obj.save()
		string = "This message has been restored in 'Inbox'."

	context = {'message' : string, 'link' : reverse('trash'), 'title' : 'Back to Trash'}
	return HttpResponse(render(request, 'common/success_LoggedIn.html', context))
