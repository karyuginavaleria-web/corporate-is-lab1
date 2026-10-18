from django import forms

from .models import Ticket


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = "form-control"


class TicketForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            "title",
            "category",
            "priority",
            "description",
        ]

        widgets = {
            "description": forms.Textarea(
                attrs={"rows": 5}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["category"].empty_label = "— не выбрана —"

    def clean_title(self):
        title = self.cleaned_data["title"].strip()

        if len(title) < 5:
            raise forms.ValidationError(
                "Сформулируйте тему хотя бы в 5 символов."
            )

        return title


class TicketUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            "title",
            "category",
            "priority",
            "status",
            "assignee",
            "description",
        ]

        widgets = {
            "description": forms.Textarea(
                attrs={"rows": 5}
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        self.fields["category"].empty_label = "— не выбрана —"
        self.fields["assignee"].empty_label = "— не назначен —"

        if user is not None and not user.has_perm(
            "helpdesk.change_ticket"
        ):
            self.fields.pop("status")
            self.fields.pop("assignee")