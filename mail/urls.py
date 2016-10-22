"""EmailDelivery URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from .import views

urlpatterns = [
    url(r'^sendMail$',                                  views.sendMail,             name = 'sendMail'),
    url(r'^sentMail$',                                  views.sentMail,             name = 'sentMail'),
    url(r'^drafts$',                                    views.drafts,               name = 'drafts'),
    url(r'^trash$',                                     views.trash,                name = 'trash'),
    url(r'^profile$',                                   views.profile,              name = 'profile'),

    url(r'^saveDraft$',                                 views.saveDraft,            name = 'saveDraft'),
    url(r'^(?P<messageID>\d+)/forward$',                views.forward,              name = 'forward'),
    url(r'^(?P<targetUserID>\d+)/reply$',               views.reply,                name = 'reply'),
    url(r'^downloadImage$',                             views.downloadImage,        name = 'downloadImage'),

    url(r'^(?P<draftID>\d+)/viewDraft$',                views.viewDraft,            name = 'viewDraft'),
    url(r'^(?P<messageID>\d+)/viewInboxMessage$',       views.viewInboxMessage,     name = 'viewInboxMessage'),
    url(r'^(?P<messageID>\d+)/viewSentMailMessage$',    views.viewSentMailMessage,  name = 'viewSentMailMessage'),
    url(r'^(?P<messageID>\d+)/viewTrashMessage$',       views.viewTrashMessage,     name = 'viewTrashMessage'),

    url(r'^(?P<messageID>\d+)/deleteFromInbox$',        views.deleteFromInbox,      name = 'deleteFromInbox'),
    url(r'^(?P<messageID>\d+)/deleteFromDraft$',        views.deleteFromDraft,      name = 'deleteFromDraft'),
    url(r'^(?P<messageID>\d+)/deleteFromOutbox$',       views.deleteFromOutbox,     name = 'deleteFromOutbox'),

    url(r'^(?P<messageID>\d+)/restore$',                views.restore,              name = 'restore'),
    url(r'^getMessage/(?P<messageID>\d+)$',             views.getMessage,           name = 'getMessage'),
]
