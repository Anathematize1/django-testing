from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.other = User.objects.create(username='other')

        cls.note = Note.objects.create(
            title='note',
            text='text',
            slug='test-slug',
            author=cls.author,
        )

        cls.home_url = reverse('notes:home')
        cls.login_url = reverse('users:login')
        cls.signup_url = reverse('users:signup')
        cls.logout_url = reverse('users:logout')

        cls.list_url = reverse('notes:list')
        cls.success_url = reverse('notes:success')
        cls.add_url = reverse('notes:add')

        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

        cls.public_urls = (
            cls.home_url,
            cls.login_url,
            cls.signup_url,
        )
        cls.auth_urls = (
            cls.list_url,
            cls.success_url,
            cls.add_url,
        )
        cls.note_urls = (
            cls.detail_url,
            cls.edit_url,
            cls.delete_url,
        )

    @classmethod
    def get_author_client(cls):
        client = Client()
        client.force_login(cls.author)
        return client

    @classmethod
    def get_other_client(cls):
        client = Client()
        client.force_login(cls.other)
        return client

    def test_public_pages_available_for_anonymous(self):
        for url in self.public_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_available_for_all(self):
        clients = (
            self.client,
            self.get_author_client(),
            self.get_other_client(),
        )
        for client in clients:
            with self.subTest(client=client):
                response = client.post(self.logout_url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_user_pages_available(self):
        author_client = self.get_author_client()
        for url in self.auth_urls:
            with self.subTest(url=url):
                response = author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_pages_available_only_for_author(self):
        author_client = self.get_author_client()
        for url in self.note_urls:
            with self.subTest(url=url):
                response = author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        other_client = self.get_other_client()
        for url in self.note_urls:
            with self.subTest(url=url):
                response = other_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_anonymous_redirect_to_login(self):
        urls = self.auth_urls + self.note_urls
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                expected = f'{self.login_url}?next={url}'
                self.assertRedirects(response, expected)
