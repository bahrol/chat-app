from django.contrib import admin

from .models import ChatBox, Message

# Register your models here.
admin.site.register(ChatBox)
admin.site.register(Message)
