from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        import core.spectacular  # noqa: registers JWT auth scheme with drf-spectacular
