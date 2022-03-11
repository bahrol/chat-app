from django.urls import path

from . import views

urlpatterns = [
    path('auth/signup/', views.SignupView.as_view(), name='signup'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('groups/', views.GroupView.as_view(), name='groups'),
    path('groups/my/', views.MyGroupView.as_view(), name='my_group'),
    path('join-requests/', views.JoinRequestView.as_view(), name='join_request'),
    path('join-requests/group/', views.JoinRequestGroupView.as_view(), name='group_join_requests'),
    path('join-requests/accept/', views.AcceptJoinRequestView.as_view(), name='accept_join_requests'),
]
