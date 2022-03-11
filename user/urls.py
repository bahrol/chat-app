from django.urls import path

from . import views

urlpatterns = [
    path('auth/signup/', views.SignupView.as_view(), name='signup'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('groups/', views.GroupView.as_view(), name='groups'),
    path('groups/my/', views.MyGroupView.as_view(), name='my_group'),
]
