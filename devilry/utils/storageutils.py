from django.core.files.storage import storages, Storage
from django.conf import settings


def get_delivery_storage() -> Storage:
    storage_name = getattr(settings, "DELIVERY_STORAGE_BACKEND", "default")
    return storages[storage_name]


def get_temporary_storage() -> Storage:
    storage_name = getattr(settings, "DELIVERY_TEMPORARY_STORAGE_BACKEND", "default")
    return storages[storage_name]
