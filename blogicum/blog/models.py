from core.models import PublishedCreatedModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class TitleModel(models.Model):
    title = models.CharField(
        blank=False,
        max_length=256,
        default='Empty',
        verbose_name='Заголовок',
        null=True
    )

    class Meta:
        abstract = True


class Category(PublishedCreatedModel, TitleModel):
    description = models.TextField(
        blank=False,
        default='Empty',
        verbose_name='Описание'
    )
    slug = models.SlugField(
        blank=False,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
                  'разрешены символы латиницы, цифры, дефис и подчёркивание.',
        unique=True
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title if len(str(self.title)) < 30 \
            else str(self.title)[:30] + '...'


class Location(PublishedCreatedModel):
    name = models.CharField(
        blank=False,
        default='Empty',
        verbose_name='Название места',
        max_length=256
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name if len(str(self.name)) < 30 \
            else str(self.name)[:30] + '...'


class Post(PublishedCreatedModel, TitleModel):
    text = models.TextField(
        blank=False,
        default='Empty',
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        blank=False,
        auto_now_add=False,
        auto_now=False,
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
                  'можно делать отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Категория'
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title if len(str(self.title)) < 30 \
            else str(self.title)[:30] + '...'
