from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from user.models import User, GroupMember, GroupConnectionRequest
from .models import Message, ChatBox


# Create your views here.
class ChatListView(APIView):
    def get(self, request):
        user = request.user
        chat_boxes = ChatBox.objects.filter(Q(user1=user) | Q(user2=user))
        chat_boxes = sorted(chat_boxes, key=lambda cb: cb.last_message.timestamp)
        # TODO check sorting

        chats = []
        for chat_box in chat_boxes:
            other_user = chat_box.user2 if chat_box.user1.id == user.id else chat_box.user1
            chat = {
                "userId": other_user.id,
                "name": other_user.name,
            }
            chats.append(chat)

        response_data = {"chats": chats}
        return Response(response_data, status=status.HTTP_200_OK)


class ChatView(APIView):
    def are_in_same_group(self, user1, user2):
        gp_member1 = GroupMember.objects.get(user=user1)
        gp_member2 = GroupMember.objects.get(user=user2)
        return gp_member1.group == gp_member2.group

    def are_in_connected_groups(self, user1, user2):
        gp_member1 = GroupMember.objects.get(user=user1)
        gp_member2 = GroupMember.objects.get(user=user2)
        gp1 = gp_member1.group
        gp2 = gp_member2.group
        return GroupConnectionRequest.objects.filter(Q(applicant_group=gp1, receiver_group=gp2) | Q(applicant_group=gp2, receiver_group=gp1)).exists()

    def can_chat(self, user1, user2):
        """did not use or for return value to optimize code. if the first condition is True we dont
        need to check the second condition"""
        in_connected_groups = self.are_in_connected_groups(user1, user2)
        if in_connected_groups is True:
            return True
        in_same_group = self.are_in_same_group(user1, user2)
        return in_same_group

    def get(self, request, user_id):
        user = request.user

        try:
            chat_box = ChatBox.objects.get(Q(user1=user, user2_id=user_id) | Q(user1_id=user_id, user2=user))
        except ChatBox.DoesNotExist:
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        messages = []
        for msg in chat_box.messages:
            sender_user = chat_box.user1 if msg.sender == 1 else chat_box.user2
            message = {
                "message": msg.text,
                "date": msg.timestamp.timestamp(),
                "sentby": sender_user.id,
            }
            messages.append(message)

        response_data = {"messages": messages}
        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request, user_id):
        user = request.user
        try:
            second_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            text_message = request.data['message']
        except KeyError:
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            can_chat = self.can_chat(user, second_user)
        except GroupMember.DoesNotExist:
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        if not can_chat:
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        chat_box = ChatBox(user1=user, user2=second_user)
        chat_box.save()

        msg = Message(sender=1, chat=chat_box, text=text_message)
        msg.save()

        response_data = {"message": "successful"}
        return Response(response_data, status=status.HTTP_200_OK)

