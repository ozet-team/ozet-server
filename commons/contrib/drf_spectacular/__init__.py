from drf_spectacular.extensions import OpenApiAuthenticationExtension


class SwaggerTokenAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = (
        "utils.django.rest_framework.authentications.SwaggerTokenAuthentication"
    )
    name = "SwaggerTokenAuthentication"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "header",
            "name": "ozet-swagger-api-key",
        }


class JSONWebTokenAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = (
        "utils.django.rest_framework.authentications.JSONWebTokenAuthentication"
    )
    name = "JSONWebTokenAuthentication"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "header",
            "name": "authorization",
        }
