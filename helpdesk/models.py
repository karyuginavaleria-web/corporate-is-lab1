from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(
        "Название",
        max_length=100,
        unique=True,
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Ticket(models.Model):
    STATUS_CHOICES = [
        ("new", "Новая"),
        ("in_progress", "В работе"),
        ("done", "Выполнена"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Низкий"),
        ("medium", "Средний"),
        ("high", "Высокий"),
    ]

    title = models.CharField("Тема", max_length=200)

    description = models.TextField(
        "Описание",
    )

    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="tickets",
    )

    priority = models.CharField(
        "Приоритет",
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="medium",
    )

    status = models.CharField(
        "Статус",
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickets",
        verbose_name="Автор",
    )

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Исполнитель",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )

    created_at = models.DateTimeField(
        "Создана",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "Изменена",
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def __str__(self):
        return self.title

    def can_be_edited_by(self, user):
        if user.has_perm("helpdesk.change_ticket"):
            return True

        return (
            self.created_by == user
            and self.status == "new"
        )