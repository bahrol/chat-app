from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.serializers import JSONWebTokenSerializer

from .models import User, Group, GroupMember, GroupJoinRequest, GroupConnectionRequest
from .serializers import UserSerializer, GroupSerializer, GroupJoinRequestSerializer, GroupConnectionRequestSerializer


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
        ser.save()
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
        group_member_queryset = GroupMember.objects.filter(group=group).order_by('-timestamp')
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


class JoinRequestView(APIView):
    join_request_serializer = GroupJoinRequestSerializer

    def get(self, request):
        user = request.user
        join_requests_queryset = GroupJoinRequest.objects.filter(user=user).order_by('-timestamp')

        join_requests = []
        for req in join_requests_queryset:
            join_req = {
                "id": req.id,
                "groupId": req.group.id,
                "userId": req.user.id,
                "data": req.timestamp.timestamp()
            }
            join_requests.append(join_req)

        response_data = {
            "joinRequests": join_requests
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        if GroupMember.objects.filter(user=user).exists():
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            group_id = request.data['groupId']
        except KeyError:
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "group": group_id,
            "user": user.id,
        }
        ser = self.join_request_serializer(data=data)
        if not ser.is_valid():
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        ser.save()
        response_data = {
            "message": "successful"
        }
        return Response(response_data, status=status.HTTP_200_OK)


class JoinRequestGroupView(APIView):
    def get(self, request):
        user = request.user
        try:
            gm = GroupMember.objects.get(user=user)
        except GroupMember.DoesNotExist:    # User is not in any groups
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        if gm.role != GroupMember.OWNER:   # User is not admin
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        join_requests_queryset = GroupJoinRequest.objects.filter(group=gm.group).order_by('-timestamp')

        join_requests = []
        for req in join_requests_queryset:
            join_req = {
                "id": req.id,
                "groupId": req.group.id,
                "userId": req.user.id,
                "data": req.timestamp.timestamp()
            }
            join_requests.append(join_req)

        response_data = {
            "joinRequests": join_requests
        }
        return Response(response_data, status=status.HTTP_200_OK)


class AcceptJoinRequestView(APIView):
    def post(self, request):
        user = request.user
        try:
            join_request_id = request.data['joinRequestId']
        except KeyError:
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            gm = GroupMember.objects.get(user=user)
        except GroupMember.DoesNotExist:    # User is not in any groups
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        if gm.role != GroupMember.OWNER:   # User is not admin
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            join_request = GroupJoinRequest.objects.get(id=join_request_id, group=gm.group)
        except GroupJoinRequest.DoesNotExist:
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        join_request.is_accepted = True
        join_request.save()

        response_data = {
            "message": "successful"
        }
        return Response(response_data, status=status.HTTP_200_OK)


class ConnectionRequestView(APIView):
    serializer_class = GroupConnectionRequestSerializer

    def get(self, request):
        user = request.user
        try:
            gm = GroupMember.objects.get(user=user)
        except GroupMember.DoesNotExist:    # User is not in any groups
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        if gm.role != GroupMember.OWNER:   # User is not admin
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        connection_requests = GroupConnectionRequest.objects.filter(receiver_group=gm.group).order_by('-timestamp')
        requests = []
        for req in connection_requests:
            connection_request = {
              "connectionRequestId": req.id,
              "groupId": req.applicant_group.id,
              "sent": req.timestamp.timestamp(),
            }
            requests.append(connection_request)
        response_data = {
            "requests": requests
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user

        try:
            group_id = request.data['groupId']
        except KeyError:
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            gm = GroupMember.objects.get(user=user)
        except GroupMember.DoesNotExist:    # User is not in any groups
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        if gm.role != GroupMember.OWNER:   # User is not admin
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "applicant_group": gm.group.id,
            "receiver_group": group_id,
        }
        ser = self.serializer_class(data=data)
        if not ser.is_valid():
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        ser.save()
        response_data = {"message": "successful"}
        return Response(response_data, status=status.HTTP_200_OK)


class AcceptConnectionRequestView(APIView):
    def post(self, request):
        user = request.user

        try:
            group_id = request.data['groupId']
        except KeyError:
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            gm = GroupMember.objects.get(user=user)
        except GroupMember.DoesNotExist:  # User is not in any groups
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        if gm.role != GroupMember.OWNER:  # User is not admin
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            gp_connection_req = GroupConnectionRequest.objects.get(applicant_group_id=group_id, receiver_group=gm.group)
        except GroupConnectionRequest.DoesNotExist:
            response_data = {"error": {"enMessage": "Bad request!"}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        gp_connection_req.is_accepted = True
        gp_connection_req.save()
        response_data = {"message": "successful"}
        return Response(response_data, status=status.HTTP_200_OK)
