from rest_framework import serializers

from .models import User, Group, GroupJoinRequest, GroupConnectionRequest


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
            "password",
        ]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class GroupJoinRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupJoinRequest
        fields = '__all__'


class GroupConnectionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupConnectionRequest
        fields = '__all__'
