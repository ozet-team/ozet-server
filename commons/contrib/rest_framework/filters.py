from django.utils.encoding import force_str
from rest_framework.filters import OrderingFilter
from rest_framework.compat import coreapi, coreschema


class OrderingFilter(OrderingFilter):
    """Swagger description 에 정렬 옵션을 표시하기 위한 OrderingFilter"""
    def _get_description(self, view) -> str:
        try:
            view_ordering_fields = getattr(view, "ordering_fields", [])
            description = (
                f"정렬 필드 옵션 (-가 앞에 오는 경우가 Descending)\n"
                f'사용할 수 있는 값: {", ".join(view_ordering_fields)}'
            )
        except Exception:
            description = self.ordering_description
        return description

    def get_schema_fields(self, view):
        assert (
            coreapi is not None
        ), "coreapi must be installed to use `get_schema_fields()`"
        assert (
            coreschema is not None
        ), "coreschema must be installed to use `get_schema_fields()`"

        return [
            coreapi.Field(
                name=self.ordering_param,
                required=False,
                location="query",
                schema=coreschema.String(
                    title=force_str(self.ordering_title),
                    description=force_str(self._get_description(view)),
                ),
            )
        ]

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": self.ordering_param,
                "required": False,
                "in": "query",
                "description": force_str(self._get_description(view)),
                "schema": {
                    "type": "string",
                },
            },
        ]