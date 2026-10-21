from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import SiteConfiguration

FIELDS = {"site_name": 100, "tagline": 180, "description": 3000, "contact_email": 254, "contact_phone": 30, "address": 255}

@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def site_configuration(request):
    if request.user.user_type != "admin" or not request.user.is_active:
        return Response({"detail": "Acesso restrito ao administrador."}, status=403)
    if request.method == "PUT":
        if not isinstance(request.data, dict):
            return Response({"detail": "Envie um objeto JSON."}, status=400)
        if set(request.data) - set(FIELDS):
            return Response({"detail": "Campos não permitidos."}, status=400)
        cleaned = {}
        for field, maximum in FIELDS.items():
            if field not in request.data:
                continue
            value = request.data[field]
            if not isinstance(value, str) or len(value.strip()) > maximum:
                return Response({"detail": f"Valor inválido para {field}."}, status=400)
            cleaned[field] = value.strip()
        if "site_name" in cleaned and not cleaned["site_name"]:
            return Response({"detail": "O nome do site é obrigatório."}, status=400)
        if cleaned.get("contact_email"):
            try:
                validate_email(cleaned["contact_email"])
            except ValidationError:
                return Response({"detail": "E-mail de contato inválido."}, status=400)
        config, _ = SiteConfiguration.objects.get_or_create(pk=1)
        for key, value in cleaned.items():
            setattr(config, key, value)
        config.save()
    else:
        config, _ = SiteConfiguration.objects.get_or_create(pk=1)
    return Response({key: getattr(config, key) for key in FIELDS} | {"updated_at": config.updated_at})


@api_view(["GET"])
@permission_classes([AllowAny])
def public_site_configuration(request):
    """Expose only public presentation/contact fields; never secrets."""
    config, _ = SiteConfiguration.objects.get_or_create(pk=1)
    return Response({key: getattr(config, key) for key in FIELDS})
