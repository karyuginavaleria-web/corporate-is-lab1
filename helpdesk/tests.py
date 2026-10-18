from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from .models import Category, Ticket


User = get_user_model()


class TicketTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="ivanov",
            password="test12345",
        )

        self.it_user = User.objects.create_user(
            username="petrov",
            password="test12345",
        )

        permissions = Permission.objects.filter(
            content_type__app_label="helpdesk",
            codename__in=[
                "view_ticket",
                "change_ticket",
            ],
        )

        self.it_user.user_permissions.set(permissions)

        self.category = Category.objects.create(
            name="Оборудование"
        )

    def test_employee_sees_only_own_tickets(self):
        Ticket.objects.create(
            title="Моя заявка",
            description="Описание",
            category=self.category,
            created_by=self.user,
        )

        other_user = User.objects.create_user(
            username="other",
            password="test12345",
        )

        Ticket.objects.create(
            title="Чужая заявка",
            description="Описание",
            category=self.category,
            created_by=other_user,
        )

        self.client.login(
            username="ivanov",
            password="test12345",
        )

        response = self.client.get(
            reverse("ticket_list")
        )

        self.assertContains(response, "Моя заявка")
        self.assertNotContains(response, "Чужая заявка")

    def test_it_user_sees_all_tickets(self):
        Ticket.objects.create(
            title="Заявка 1",
            description="Описание",
            category=self.category,
            created_by=self.user,
        )

        other_user = User.objects.create_user(
            username="other",
            password="test12345",
        )

        Ticket.objects.create(
            title="Заявка 2",
            description="Описание",
            category=self.category,
            created_by=other_user,
        )

        self.client.login(
            username="petrov",
            password="test12345",
        )

        response = self.client.get(
            reverse("ticket_list")
        )

        self.assertContains(response, "Заявка 1")
        self.assertContains(response, "Заявка 2")

    def test_ticket_can_be_edited_by_author_when_new(self):
        ticket = Ticket.objects.create(
            title="Новая заявка",
            description="Описание",
            category=self.category,
            created_by=self.user,
        )

        self.assertTrue(
            ticket.can_be_edited_by(self.user)
        )

    def test_ticket_cannot_be_edited_by_other_employee(self):
        other_user = User.objects.create_user(
            username="other",
            password="test12345",
        )

        ticket = Ticket.objects.create(
            title="Заявка",
            description="Описание",
            category=self.category,
            created_by=self.user,
        )

        self.assertFalse(
            ticket.can_be_edited_by(other_user)
        )

    def test_employee_cannot_change_status_and_assignee(self):
        ticket = Ticket.objects.create(
            title="Заявка сотрудника",
            description="Описание",
            category=self.category,
            created_by=self.user,
        )

        self.client.login(
            username="ivanov",
            password="test12345",
        )

        response = self.client.get(
            reverse("ticket_update", args=[ticket.pk])
        )

        self.assertNotContains(response, "Статус")
        self.assertNotContains(response, "Исполнитель")

    def test_it_user_can_change_status_and_assignee(self):
        ticket = Ticket.objects.create(
            title="Заявка",
            description="Описание",
            category=self.category,
            created_by=self.user,
        )

        self.client.login(
            username="petrov",
            password="test12345",
        )

        response = self.client.get(
            reverse("ticket_update", args=[ticket.pk])
        )

        self.assertContains(response, "Статус")
        self.assertContains(response, "Исполнитель")

    def test_ticket_detail_page(self):
        ticket = Ticket.objects.create(
            title="Проверка страницы",
            description="Описание заявки",
            category=self.category,
            created_by=self.user,
        )

        self.client.login(
            username="ivanov",
            password="test12345",
        )

        response = self.client.get(
            reverse("ticket_detail", args=[ticket.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Проверка страницы")