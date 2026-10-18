from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TicketForm, TicketUpdateForm
from .models import Ticket


def visible_tickets(user):
    tickets = Ticket.objects.select_related(
        "category",
        "assignee",
        "created_by",
    )

    if user.has_perm("helpdesk.change_ticket") or user.is_superuser:
        return tickets

    return tickets.filter(created_by=user)


@login_required
def ticket_list(request):
    tickets = visible_tickets(request.user).order_by("-created_at")

    return render(
        request,
        "helpdesk/ticket_list.html",
        {"tickets": tickets},
    )


@login_required
def ticket_create(request):
    if request.method == "POST":
        form = TicketForm(request.POST)

        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()

            return redirect("ticket_list")
    else:
        form = TicketForm()

    return render(
        request,
        "helpdesk/ticket_form.html",
        {"form": form},
    )


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(
        visible_tickets(request.user),
        pk=pk,
    )

    can_edit = ticket.can_be_edited_by(request.user)

    return render(
        request,
        "helpdesk/ticket_detail.html",
        {
            "ticket": ticket,
            "can_edit": can_edit,
        },
    )


@login_required
def ticket_update(request, pk):
    ticket = get_object_or_404(
        Ticket.objects.select_related(
            "category",
            "assignee",
            "created_by",
        ),
        pk=pk,
    )

    if not ticket.can_be_edited_by(request.user):
        raise PermissionDenied

    if request.method == "POST":
        form = TicketUpdateForm(
            request.POST,
            instance=ticket,
            user=request.user,
        )

        if form.is_valid():
            form.save()
            return redirect("ticket_detail", pk=ticket.pk)

    else:
        form = TicketUpdateForm(
            instance=ticket,
            user=request.user,
        )

    return render(
        request,
        "helpdesk/ticket_form.html",
        {
            "form": form,
            "ticket": ticket,
            "is_edit": True,
        },
    )


@login_required
def ticket_queue(request):
    if not request.user.has_perm("helpdesk.view_ticket"):
        return redirect("ticket_list")

    tickets = Ticket.objects.select_related(
        "category",
        "assignee",
        "created_by",
    )

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "")
    priority = request.GET.get("priority", "")
    category = request.GET.get("category", "")

    if search:
        tickets = tickets.filter(
            title__icontains=search
        ) | tickets.filter(
            description__icontains=search
        )

    if status:
        tickets = tickets.filter(status=status)

    if priority:
        tickets = tickets.filter(priority=priority)

    if category:
        tickets = tickets.filter(category_id=category)

    tickets = tickets.order_by("-created_at")

    from .models import Category

    categories = Category.objects.all()

    return render(
        request,
        "helpdesk/ticket_queue.html",
        {
            "tickets": tickets,
            "categories": categories,
            "search": search,
            "selected_status": status,
            "selected_priority": priority,
            "selected_category": category,
        },
    )