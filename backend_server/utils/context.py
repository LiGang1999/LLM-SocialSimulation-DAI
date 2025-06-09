from threading import local
from typing import Dict, Optional

# from backend_server.server import 'User'

# from reverie import 'LLMConfig', 'Reverie'

_thread_local = local()


def get_reverie() -> Optional["Reverie"]:
    return getattr(_thread_local, "reverie", None)


def set_reverie(reverie: "Reverie"):
    _thread_local.reverie = reverie


def get_instance() -> Optional["ReverieInstance"]:
    return getattr(_thread_local, "instance", None)


def set_instance(instance: "ReverieInstance"):
    _thread_local.instance = instance


def get_user() -> Optional["User"]:
    return getattr(_thread_local, "user", None)


def set_user(user: "User"):
    _thread_local.user = user


def get_providers() -> Optional[Dict[str, "LLMConfig"]]:
    return getattr(_thread_local, "providers", None)


def set_providers(providers: Dict[str, "LLMConfig"]):
    _thread_local.providers = providers


class ThreadContext:
    @property
    def reverie(self) -> Optional["Reverie"]:
        return get_reverie()

    @reverie.setter
    def reverie(self, value: "Reverie"):
        set_reverie(value)

    @property
    def instance(self) -> Optional["ReverieInstance"]:
        return get_instance()

    @instance.setter
    def instance(self, value: "ReverieInstance"):
        set_instance(value)

    @property
    def user(self) -> Optional["User"]:
        return get_user()

    @user.setter
    def user(self, value: "User"):
        set_user(value)

    @property
    def providers(self) -> Optional[Dict[str, "LLMConfig"]]:
        return get_providers()

    @providers.setter
    def providers(self, value: Dict[str, "LLMConfig"]):
        set_providers(value)


ctx = ThreadContext()
