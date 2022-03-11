from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.serializers import JSONWebTokenSerializer

from .models import User
from .serializers import UserSerializer


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
            token_serializer = JSONWebTokenSerializer(data={"email": user.email, "password": password})
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
