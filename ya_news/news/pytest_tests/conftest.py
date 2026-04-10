from datetime import timedelta

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def author(db, django_user_model):
    return django_user_model.objects.create(username='author')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader(db, django_user_model):
    return django_user_model.objects.create(username='reader')


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news_batch(db):
    today = timezone.now().date()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def news_item(db):
    return News.objects.create(
        title='Отдельная новость',
        text='Текст отдельной новости.',
        date=timezone.now().date(),
    )


@pytest.fixture
def detail_url(news_item):
    return reverse('news:detail', args=(news_item.pk,))


@pytest.fixture
def comments_url(detail_url):
    return f'{detail_url}#comments'


@pytest.fixture
def comments(news_item, author):
    start_time = timezone.now() - timedelta(days=1)
    for index in range(3):
        comment = Comment.objects.create(
            news=news_item,
            author=author,
            text=f'Комментарий {index}',
        )
        created = start_time + timedelta(minutes=index)
        Comment.objects.filter(pk=comment.pk).update(created=created)
        comment.created = created


@pytest.fixture
def form_data():
    return {'text': 'Текст комментария'}


@pytest.fixture
def comment(news_item, author):
    return Comment.objects.create(
        news=news_item,
        author=author,
        text='Текст комментария',
    )


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def edit_redirect_url(login_url, edit_url):
    return f'{login_url}?next={edit_url}'


@pytest.fixture
def delete_redirect_url(login_url, delete_url):
    return f'{login_url}?next={delete_url}'
