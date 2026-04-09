from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, detail_url, form_data):
    login_url = reverse('users:login')
    response = client.post(detail_url, data=form_data)

    assertRedirects(response, f'{login_url}?next={detail_url}')
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    author_client,
    author,
    news_item,
    detail_url,
    comments_url,
    form_data,
):
    response = author_client.post(detail_url, data=form_data)

    assertRedirects(response, comments_url)
    assert Comment.objects.count() == 1

    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news_item
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, detail_url, bad_words_data):
    response = author_client.post(detail_url, data=bad_words_data)

    assertFormError(
        response.context['form'],
        'text',
        errors=WARNING,
    )
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
    author_client,
    comment,
    edit_url,
    comments_url,
    new_comment_data,
):
    response = author_client.post(edit_url, data=new_comment_data)

    assertRedirects(response, comments_url)
    comment.refresh_from_db()
    assert comment.text == new_comment_data['text']


def test_user_cant_edit_comment_of_another_user(
    reader_client,
    comment,
    edit_url,
    new_comment_data,
    form_data,
):
    response = reader_client.post(edit_url, data=new_comment_data)

    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_author_can_delete_comment(author_client, delete_url, comments_url):
    response = author_client.delete(delete_url)

    assertRedirects(response, comments_url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(reader_client, delete_url):
    response = reader_client.delete(delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
