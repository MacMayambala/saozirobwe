# staff_management/base_models.py
from django.db import models
from datetime import date
from django.core.exceptions import ValidationError
from .models import is_backdate_allowed


class BaseModel(models.Model):
    """
    Abstract base model that enforces backdate restrictions
    on all DateField fields unless backdating is allowed.
    """
    class Meta:
        abstract = True

    def clean(self):
        super().clean()

        if not is_backdate_allowed():
            for field in self._meta.fields:
                if isinstance(field, models.DateField):
                    value = getattr(self, field.name)
                    if value and value < date.today():
                        raise ValidationError({
                            field.name: f"Backdating is not allowed for {field.verbose_name}."
                        })
