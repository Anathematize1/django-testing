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

        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.form_data = {
            'title': 'new_note',
            'text': 'new_text',
            'slug': 'new-note',
        }

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

    def create_note(self):
        return Note.objects.create(
            title='note',
            text='text',
            slug='test-slug',
            author=self.author,
        )

    def test_user_can_create_note(self):
        author_client = self.get_author_client()
        response = author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)

        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.add_url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_not_unique_slug(self):
        note = self.create_note()
        form_data = self.form_data.copy()
        form_data['slug'] = note.slug

        author_client = self.get_author_client()
        response = author_client.post(self.add_url, data=form_data)

        self.assertFormError(
            response.context['form'],
            'slug',
            errors=(note.slug + WARNING),
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        form_data = self.form_data.copy()
        form_data.pop('slug')

        author_client = self.get_author_client()
        response = author_client.post(self.add_url, data=form_data)

        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)

        new_note = Note.objects.get()
        expected_slug = slugify(form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        note = self.create_note()
        url = reverse('notes:edit', args=(note.slug,))

        author_client = self.get_author_client()
        response = author_client.post(url, data=self.form_data)

        self.assertRedirects(response, self.success_url)
        note.refresh_from_db()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        note = self.create_note()
        url = reverse('notes:edit', args=(note.slug,))

        other_client = self.get_other_client()
        response = other_client.post(url, data=self.form_data)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=note.id)
        self.assertEqual(note.title, note_from_db.title)
        self.assertEqual(note.text, note_from_db.text)
        self.assertEqual(note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        note = self.create_note()
        url = reverse('notes:delete', args=(note.slug,))

        author_client = self.get_author_client()
        response = author_client.post(url)

        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        note = self.create_note()
        url = reverse('notes:delete', args=(note.slug,))

        other_client = self.get_other_client()
        response = other_client.post(url)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
