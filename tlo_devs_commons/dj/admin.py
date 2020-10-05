from abc import ABC

from django.contrib import admin
from django.contrib.auth.admin import csrf_protect_m
from django.views.decorators.csrf import csrf_exempt

from .uploads import GCPStreamingFileUploadHandler


class GCPStreamingModelAdminMixin(admin.ModelAdmin):
    @csrf_exempt
    def add_view(self, request, form_url='', extra_context=None):
        request.upload_handlers = [GCPStreamingFileUploadHandler(
            request, "tlo-devs-uploadhandler"
        )]
        return self._add_view(request, form_url, extra_context)

    @csrf_protect_m
    def _add_view(self, *args, **kwargs):
        return super(GCPStreamingModelAdminMixin, self).add_view(*args, **kwargs)


class SortableAdminMixin(ABC):
    admin_app_ordering: dict

    @staticmethod
    def get_app_index(app_list: list, app_label: str) -> int:
        for i, app in enumerate(app_list):
            if app.get("app_label") == app_label:
                return i

    @staticmethod
    def _merge_apps(toplevel_app: dict,
                    mergees: list) -> dict:
        new_app = toplevel_app
        for app in mergees:
            new_app["models"] += app.get("models")
        return new_app

    def _assemble_app_dict(self,
                           app_list: list,
                           app_label: str) -> dict:
        original_app = app_list[
            self.get_app_index(app_list, app_label)
        ]
        additional_app_labels = self.admin_app_ordering.get(app_label, tuple())
        if additional_app_labels:
            additional_app_labels = tuple(
                i for i in additional_app_labels if not i == app_label
            )
        apps_to_merge = [
            app_list[
                self.get_app_index(app_list, a)
            ] for a in additional_app_labels
        ]
        return self._merge_apps(original_app, apps_to_merge)

    def get_app_list(self, request):
        """ Overrides the app_list based on the admin_app_ordering parameter """
        app_list = super().get_app_list(request)  # noqa
        # Do not process if the attribute has not been set
        if not self.admin_app_ordering:
            return app_list
        # If we are at the login site
        if request.user.id is None:
            return app_list

        new_app_list = []
        for original_app_label, additional_app_labels in self.admin_app_ordering.items():
            # This means we need to make changes to the app_dict
            if len(additional_app_labels) > 1:
                new_app_list.append(
                    self._assemble_app_dict(
                        app_list, original_app_label
                    )
                )

            # In this case the app_dict is fine as it is
            else:
                new_app_list.append(
                    app_list[self.get_app_index(app_list, original_app_label)]
                )

        return new_app_list
