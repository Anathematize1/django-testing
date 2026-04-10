from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):

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

        cls.form_data = {
            'title': 'new_note',
            'text': 'new_text',
            'slug': 'new-slug',
        }

        cls.login_url = reverse('users:login')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')
        cls.login_redirect_url = f'{cls.login_url}?next={cls.add_url}'

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.other_client = Client()
        self.other_client.force_login(self.other)
        self.form_data = {
            'title': 'new_note',
            'text': 'new_text',
            'slug': 'new-note',
        }

    def test_user_can_create_note(self):
        """Проверяет, что авторизованный пользователь может создать заметку."""
        Note.objects.all().delete()
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)

        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Проверяет, что анонимный пользователь не может создать заметку."""
        notes_count = Note.objects.count()
        response = self.client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.login_redirect_url)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_not_unique_slug(self):
        """Проверяет, что нельзя создать заметку с занятым slug."""
        notes_count = Note.objects.count()
        self.form_data['slug'] = self.note.slug

        response = self.author_client.post(self.add_url, data=self.form_data)

        self.assertFormError(
            response.context['form'],
            'slug',
            errors=(self.form_data['slug'] + WARNING),
        )
        self.assertEqual(Note.objects.count(), notes_count)

    def test_empty_slug(self):
        """Проверяет, что пустой slug формируется автоматически."""
        Note.objects.all().delete()
        self.form_data.pop('slug')

        response = self.author_client.post(self.add_url, data=self.form_data)

        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)

        expected_slug = slugify(self.form_data['title'])
        new_note = Note.objects.get()
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Проверяет, что автор может редактировать свою заметку."""
        response = self.author_client.post(self.edit_url, data=self.form_data)

        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        """Проверяет, что другой"""
        """пользователь не может редактировать чужую заметку."""
        response = self.other_client.post(self.edit_url, data=self.form_data)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        """Проверяет, что автор может удалить свою заметку."""
        notes_count = Note.objects.count()
        response = self.author_client.post(self.delete_url)

        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), notes_count - 1)

    def test_other_user_cant_delete_note(self):
        """Проверяет, что другой пользователь"""
        """не может удалить чужую заметку."""
        notes_count = Note.objects.count()
        response = self.other_client.post(self.delete_url)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count)
