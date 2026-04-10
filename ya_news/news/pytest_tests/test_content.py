from django.conf import settings
import pytest

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_news_count(client, home_url, news_batch):
    """Проверяет, что на главной странице не больше 10 новостей."""
    response = client.get(home_url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, home_url, news_batch):
    """Проверяет, что новости отсортированы от новых к старым."""
    response = client.get(home_url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, detail_url, comments):
    """Проверяет, что комментарии отсортированы от старых к новым."""
    response = client.get(detail_url)
    assert 'news' in response.context

    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, detail_url):
    """Проверяет, что анонимный пользователь не видит форму."""
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, detail_url):
    """Проверяет, что авторизованный пользователь видит форму."""
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
