from django.test import TestCase, Client
from django.urls import reverse


# Create your tests here.
class UserApiTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')

        self.user1_email = "test@gmail.com"
        self.user1_password = "password123"

    def create_user(self, email, password):
        data = {
            'name': 'alireza',
            'email': email,
            'password': password,
        }
        return self.client.post(path=self.signup_url, data=data)

    def test_signup(self):
        response = self.create_user(self.user1_email, self.user1_password)
        self.assertEqual(response.status_code, 200)

        data = {
            'phone': self.user1_email,
            'password': 'wrong password',
        }
        response = self.client.post(path=self.signup_url, data=data)
        self.assertEqual(response.status_code, 400)

    def test_login(self):
        self.create_user(self.user1_email, self.user1_password)

        data = {
            'email': self.user1_email,
            'password': self.user1_password,
        }
        response = self.client.post(path=self.login_url, data=data)
        self.assertEqual(response.status_code, 200)

        data = {
            'email': self.user1_email,
            'password': "wrong password",
        }
        response = self.client.post(path=self.login_url, data=data)
        self.assertEqual(response.status_code, 400)
