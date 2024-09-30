from django.conf import settings
from django.core.files.storage import Storage, storages


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
