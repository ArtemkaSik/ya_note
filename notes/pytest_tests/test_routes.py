from http import HTTPStatus
import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


# Указываем в фикстурах встроенный клиент.
def test_home_availability_for_anonymous_user(client):
    """Проверим, что анонимному пользователю доступна главная страница проекта."""
    # Адрес страницы получаем через reverse():
    url = reverse("notes:home")
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    "name",  # Имя параметра функции.
    # Значения, которые будут передаваться в name.
    ("notes:home", "users:login", "users:logout", "users:signup"),
)
# Указываем имя изменяемого параметра в сигнатуре теста.
def test_pages_availability_for_anonymous_user(client, name):
    """Все адреса, доступные для анонимных пользователей"""
    url = reverse(name)  # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize("name", ("notes:list", "notes:add", "notes:success"))
def test_pages_availability_for_auth_user(not_author_client, name):
    """Тестирование доступности страниц для авторизованного пользователя"""
    url = reverse(name)
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.OK


# Добавляем к тесту ещё один декоратор parametrize; в его параметры
# нужно передать фикстуры-клиенты и ожидаемый код ответа для каждого клиента.
@pytest.mark.parametrize(
    "parametrized_client, expected_status",
    # Предварительно оборачиваем имена фикстур
    # в вызов функции pytest.lazy_fixture().
    (
        (pytest.lazy_fixture("not_author_client"), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture("author_client"), HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize(
    "name",
    ("notes:detail", "notes:edit", "notes:delete"),
)
def test_pages_availability_for_different_users(
    parametrized_client, name, slug_for_args, expected_status
):
    """Проверим, что автору заметки доступны страницы отдельной заметки, её редактирования и удаления (статус 200). А не автору не доступно (статус 404)."""
    url = reverse(name, args=(slug_for_args))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "name, args",
    (
        ("notes:detail", pytest.lazy_fixture("slug_for_args")),
        ("notes:edit", pytest.lazy_fixture("slug_for_args")),
        ("notes:delete", pytest.lazy_fixture("slug_for_args")),
        ("notes:add", None),
        ("notes:success", None),
        ("notes:list", None),
    ),
)
# Передаём в тест анонимный клиент, name проверяемых страниц и args:
def test_redirects(client, name, args):
    login_url = reverse("users:login")
    # Теперь не надо писать никаких if и можно обойтись одним выражением.
    url = reverse(name, args=args)
    expected_url = f"{login_url}?next={url}"
    response = client.get(url)
    assertRedirects(response, expected_url)
