from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.serializers import JSONWebTokenSerializer

from .models import User, Group, GroupMember
from .serializers import UserSerializer, GroupSerializer


# Create your views here.
class SignupView(APIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    query_set = User.objects.all()

    def post(self, request):
        ser = self.serializer_class(data=request.data)
        if ser.is_valid():
            user = ser.save()
            password = self.request.data.get("password")
            token_serializer = JSONWebTokenSerializer(data={"email": user.email, "userId": user.id, "password": password})
            token_serializer.is_valid(raise_exception=True)
            response_data = ser.data
            response_data.update({"token": token_serializer.validated_data.get("token"), "message": "successful"})
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    serializer_class = UserSerializer
    query_set = User.objects.all()
    permission_classes = [AllowAny]

    def post(self, request):
        token_serializer = JSONWebTokenSerializer(data=request.data)

        if token_serializer.is_valid():
            user = self.query_set.get(email=request.data.get("email"))
            ser = self.serializer_class(user)
            response_data = ser.data
            response_data.update({"token": token_serializer.validated_data.get("token"), "message": "successful"})
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class GroupView(APIView):
    serializer_class = GroupSerializer
    query_set = Group.objects.all()

    def get(self, request):
        ser = self.serializer_class(data=self.query_set, many=True)
        response_data = {"groups": ser.data}
        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request):    # Create a group
        ser = self.serializer_class(data=request.data)
        if not ser.is_valid():
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        response_data = {"group": {"id": ser.data.get('id')}, "message": "successful"}
        GroupMember.objects.create(group=ser.data.get('id'), user=request.user, role=GroupMember.OWNER)
        return Response(response_data, status=status.HTTP_200_OK)


class MyGroupView(APIView):
    serializer_class = GroupSerializer

    def get(self, request):
        user = request.user

        try:
            gm = GroupMember.objects.get(user=user)
        except GroupMember.DoesNotExist:    # User is not in any group
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        group = gm.group
        group_member_queryset = GroupMember.objects.filter(group=group)
        members = []
        for group_member in group_member_queryset:
            member = {
                "id": group_member.user.id,
                "name": group_member.user.name,
                "email": group_member.user.email,
                "rule": group_member.role,
            }
            members.append(member)

        response_data = {
            "name": group.name,
            "description": group.description,
            "members": members
        }
        return Response(response_data, status=status.HTTP_200_OK)
