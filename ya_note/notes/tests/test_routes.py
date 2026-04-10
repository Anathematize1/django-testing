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

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.other_client = Client()
        self.other_client.force_login(self.other)

    def test_public_pages_available_for_anonymous(self):
        """Проверяет доступность публичных страниц"""
        """для анонимного пользователя."""
        urls = (
            self.home_url,
            self.login_url,
            self.signup_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_available_for_anonymous(self):
        """Проверяет доступность страницы выхода для всех пользователей."""
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_user_pages_available(self):
        """Проверяет доступность служебных страниц для автора."""
        urls = (
            self.list_url,
            self.success_url,
            self.add_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_pages_available_only_for_author(self):
        """Проверяет доступ к страницам заметки только для автора."""
        urls = (
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )
        clients_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.other_client, HTTPStatus.NOT_FOUND),
        )
        for client, status in clients_statuses:
            for url in urls:
                with self.subTest(client=client, url=url, status=status):
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_anonymous_redirect_to_login(self):
        """Проверяет редирект анонимного пользователя на страницу входа."""
        urls = (
            self.list_url,
            self.success_url,
            self.add_url,
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                expected = f'{self.login_url}?next={url}'
                self.assertRedirects(response, expected)
