from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url',
    (
        lazy_fixture('home_url'),
        lazy_fixture('detail_url'),
        lazy_fixture('login_url'),
        lazy_fixture('signup_url'),
    ),
)
def test_pages_availability_for_anonymous(client, url):
    """Проверяет доступность публичных страниц для анонимного пользователя."""
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_logout_available_for_anonymous(client, logout_url):
    """Проверяет доступность страницы выхода для анонимного пользователя."""
    response = client.post(logout_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'client, url, expected_status',
    (
        (
            lazy_fixture('author_client'),
            lazy_fixture('edit_url'),
            HTTPStatus.OK,
        ),
        (
            lazy_fixture('reader_client'),
            lazy_fixture('edit_url'),
            HTTPStatus.NOT_FOUND,
        ),
        (
            lazy_fixture('author_client'),
            lazy_fixture('delete_url'),
            HTTPStatus.OK,
        ),
        (
            lazy_fixture('reader_client'),
            lazy_fixture('delete_url'),
            HTTPStatus.NOT_FOUND,
        ),
    ),
)
def test_availability_for_comment_edit_and_delete(
    client,
    url,
    expected_status,
):
    """Проверяет доступ к страницам редактирования и удаления комментария."""
    response = client.get(url)

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url, redirect_url',
    (
        (lazy_fixture('edit_url'), lazy_fixture('edit_redirect_url')),
        (lazy_fixture('delete_url'), lazy_fixture('delete_redirect_url')),
    ),
)
def test_redirect_for_anonymous_client(client, url, redirect_url):
    """Проверяет редирект анонимного пользователя на страницу входа."""
    response = client.get(url)

    assertRedirects(response, redirect_url)
