from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from django.urls import reverse


pytestmark = pytest.mark.django_db


def test_pages_availability_for_anonymous(client, news_item):
    urls = (
        reverse('news:home'),
        reverse('news:detail', args=(news_item.id,)),
        reverse('users:login'),
        reverse('users:signup'),
    )
    for url in urls:
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK


def test_logout_available_for_anonymous(client):
    url = reverse('users:logout')
    response = client.post(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'client_fixture, expected_status',
    (
        ('author_client', HTTPStatus.OK),
        ('reader_client', HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize('route_name', ('news:edit', 'news:delete'))
def test_availability_for_comment_edit_and_delete(
    request,
    client_fixture,
    expected_status,
    route_name,
    comment,
):
    client = request.getfixturevalue(client_fixture)
    url = reverse(route_name, args=(comment.id,))

    response = client.get(url)

    assert response.status_code == expected_status


@pytest.mark.parametrize('route_name', ('news:edit', 'news:delete'))
def test_redirect_for_anonymous_client(client, route_name, comment):
    login_url = reverse('users:login')
    url = reverse(route_name, args=(comment.id,))
    redirect_url = f'{login_url}?next={url}'

    response = client.get(url)

    assertRedirects(response, redirect_url)
