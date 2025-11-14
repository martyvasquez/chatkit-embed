from tortoise import fields, models

from fastapi_admin.models import AbstractAdmin


class AdminUser(AbstractAdmin):
    """FastAPI-Admin authentication model."""

    last_login = fields.DatetimeField(null=True)

    class Meta:
        table = "admin_users"


class ChatAppAdmin(models.Model):
    """Tortoise ORM mirror of the ChatApp SQLAlchemy model for admin use."""

    id = fields.CharField(pk=True, max_length=64)
    name = fields.CharField(max_length=255)
    workflow_id = fields.CharField(max_length=255)
    openai_api_key_encrypted = fields.TextField()
    allowed_domains = fields.TextField()
    options_json = fields.TextField()
    is_active = fields.BooleanField(default=True)

    class Meta:
        table = "chat_apps"
