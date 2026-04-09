from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

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
        cls.other_note = Note.objects.create(
            title='other_note',
            text='other_text',
            slug='other-slug',
            author=cls.other,
        )

        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

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

    def test_author_note_in_object_list(self):
        author_client = self.get_author_client()
        response = author_client.get(self.list_url)
        self.assertIn(self.note, response.context['object_list'])

    def test_only_user_notes_in_list(self):
        author_client = self.get_author_client()
        response = author_client.get(self.list_url)
        self.assertNotIn(self.other_note, response.context['object_list'])

        other_client = self.get_other_client()
        response = other_client.get(self.list_url)
        self.assertIn(self.other_note, response.context['object_list'])
        self.assertNotIn(self.note, response.context['object_list'])

    def test_author_has_form_on_add_and_edit_pages(self):
        author_client = self.get_author_client()
        urls = (
            self.add_url,
            self.edit_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
