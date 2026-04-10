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

        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.other_client = Client()
        self.other_client.force_login(self.other)

    def test_author_note_in_object_list(self):
        """Проверяет наличие заметки автора в списке только у автора."""
        test_cases = (
            (self.author_client, True),
            (self.other_client, False),
        )
        for client, expected in test_cases:
            with self.subTest(client=client, expected=expected):
                response = client.get(self.list_url)
                object_list = response.context['object_list']
                self.assertIs(self.note in object_list, expected)

    def test_author_has_form_on_add_and_edit_pages(self):
        """Проверяет наличие формы на страницах создания и редактирования."""
        urls = (
            self.add_url,
            self.edit_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
