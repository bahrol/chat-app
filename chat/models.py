from django.db import models

from user.models import User


# Create your models here.
class ChatBox(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.PROTECT, related_name='user1')
    user2 = models.ForeignKey(User, on_delete=models.PROTECT, related_name='user2')

    @property
    def last_message(self):
        return self.messages.last()

    @property
    def messages(self):
        return Message.objects.filter(chat=self).order_by('-timestamp')

    class Meta:
        unique_together = ('user1', 'user2')


class Message(models.Model):
    USER_1 = 1
    USER_2 = 2
    SENDER_CHOICES = (
        (USER_1, "User 1"),
        (USER_2, "User 2"),
    )

    sender = models.SmallIntegerField(choices=SENDER_CHOICES, default=USER_1)   # 1: user1 in chat box. 2: user2 in chat box
    chat = models.ForeignKey(ChatBox, on_delete=models.PROTECT)
    text = models.CharField(max_length=400)  # It can be TextField depends on your business
    timestamp = models.DateTimeField(auto_now_add=True)
