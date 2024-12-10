import re

from django.conf import settings
from django.core.files.storage import Storage, storages
from storages.backends.s3 import S3Storage
from storages.base import BaseStorage


def get_delivery_storage() -> Storage:
    storage_name = getattr(settings, "DELIVERY_STORAGE_BACKEND", "default")
    return storages[storage_name]


def get_delivery_storage_generate_urls() -> Storage:
    storage_name = getattr(settings, "DELIVERY_STORAGE_BACKEND_GENERATE_URLS", None)
    if storage_name:
        return storages[storage_name]
    return get_delivery_storage()


def get_temporary_storage() -> Storage:
    storage_name = getattr(settings, "DELIVERY_TEMPORARY_STORAGE_BACKEND", "default")
    return storages[storage_name]


def get_temporary_storage_generate_urls() -> Storage:
    storage_name = getattr(settings, "DELIVERY_TEMPORARY_STORAGE_BACKEND_GENERATE_URLS", None)
    if storage_name:
        return storages[storage_name]
    return get_temporary_storage()


def make_storage_url(storage: BaseStorage, stored_name: str, preferred_filename: str):
    escaped_filename = re.subn(r"\s+", "_", re.subn(r"[^a-zA-Z0-9 _.-]", "", preferred_filename)[0])[0]
    escaped_filename = escaped_filename.encode("ascii", errors="ignore").decode("utf-8")
    extra_kwargs = {}
    if isinstance(storage, S3Storage):
        extra_kwargs = {"parameters": {"ResponseContentDisposition": f'attachment; filename="{escaped_filename}"'}}
    return storage.url(stored_name, **extra_kwargs)
