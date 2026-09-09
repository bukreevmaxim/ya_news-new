# news/tests/test_content.py
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News
from news.forms import CommentForm

User = get_user_model()

NEWS_COUNT_ON_HOME_PAGE = 10


class TestHomePage(TestCase):
    HOME_URL = reverse('news:home')

    @classmethod
    def setUpTestData(cls):
        # Вычисляем текущую дату
        today = datetime.today().date()
        all_news = [
            News(
                title=f'Новость {index}',
                text='Просто текст.',
                # Для каждой новости уменьшаем дату на index дней от today,
                # где index — счётчик цикла
                date=today - timedelta(days=index)

            )
            for index in range(NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
        News.objects.bulk_create(all_news) 

    def test_news_count(self):
        # Загружаем главную страницу
        response = self.client.get(self.HOME_URL)
        # Код ответа не проверяем, так как его уже протестировали в тестах маршрутов.
        # Получаем список объектов из контекста
        object_list = response.context['object_list']
        # Определяем количество записей в списке
        news_count = object_list.count()
        # Проверяем количество новостей на странице
        self.assertEqual(news_count, NEWS_COUNT_ON_HOME_PAGE)

    def test_news_order(self):
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        # Получаем даты новостей в том порядке, как они выведены на странице
        all_dates = [news.date for news in object_list]
        # Сортируем полученный список по убыванию
        sorted_dates = sorted(all_dates, reverse=True)
        # Проверяем, что исходный список был отсортирован правильно
        self.assertEqual(all_dates, sorted_dates) 

class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(
            title='Тестовая новость', text='Просто текст.'
        )

        # Сохраняем в переменную адрес страницы с новостью:
        cls.detail_url = reverse('news:detail', args=(cls.news.pk,))
        cls.author = User.objects.create(username='Комментатор')

        # Запоминаем текущее время:
        now = timezone.now()
        # Создаём комментарии в цикле
        for index in range(10):
            # Создаём объект и записываем его в переменную
            comment = Comment.objects.create(
                news=cls.news,
                author=cls.author,
                text=f'Текст {index}',
            )

            # Сразу после создания меняем время создания комментария
            comment.created = now + timedelta(days=index)

            # Сохраняем эти изменения
            comment.save(update_fields=('created',))

    def test_comments_order(self):
        response = self.client.get(self.detail_url)
        # Проверяем, что объект новости находится в контексте
        # под ожидаемым именем — название модели
        self.assertIn('news', response.context)
        # Получаем объект новости
        news = response.context['news']
        # Получаем все комментарии к новости
        all_comments = news.comment_set.all()
        # Собираем временные метки всех комментариев
        all_timestamps = [comment.created for comment in all_comments]
        # Сортируем временные метки, менять порядок сортировки не надо
        sorted_timestamps = sorted(all_timestamps)
        # Проверяем, что временные метки отсортированы правильно
        self.assertEqual(all_timestamps, sorted_timestamps) 

    def test_anonymous_client_has_no_form(self):
        response = self.client.get(self.detail_url)
        self.assertNotIn('form', response.context)

    def test_authorized_client_has_form(self):
        # Авторизуем клиента с помощью ранее созданного пользователя
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)
        # Проверяем, что объект формы относится к нужному классу
        self.assertIsInstance(response.context['form'], CommentForm)
