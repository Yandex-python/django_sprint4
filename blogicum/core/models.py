from django.db import models


class PublishedCreatedModel(models.Model):
    is_published = models.BooleanField(
        blank=False,
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        blank=False,
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True
