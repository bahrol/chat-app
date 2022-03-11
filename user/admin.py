from django.contrib import admin

from .models import User, Group, GroupMember, GroupJoinRequest, GroupConnectionRequest

# Register your models here.
admin.site.register(User)
admin.site.register(Group)
admin.site.register(GroupMember)
admin.site.register(GroupJoinRequest)
admin.site.register(GroupConnectionRequest)
