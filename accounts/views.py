from rest_framework import generics, permissions, viewsets
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import ClientAddress, ProducerProfile
from .serializers import (
    ClientAddressSerializer,
    CustomTokenObtainPairSerializer,
    ProducerProfileSerializer,
    RegisterSerializer,
    UserSerializer,
)


class RegisterView(generics.CreateAPIView):
    """Cadastro público de cliente ou produtor (não permite criar admin)."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class CustomTokenObtainPairView(TokenObtainPairView):
    """Login por e-mail + senha. Retorna access, refresh e os dados do usuário."""

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    """Dados do usuário autenticado (usado pra tela 'Meu Perfil')."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ProducerProfileView(generics.RetrieveUpdateAPIView):
    """
    Perfil do produtor logado (nome da fazenda, localização, bio etc.)
    usado na tela 'Meu Perfil' do produtor.
    """

    serializer_class = ProducerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = ProducerProfile.objects.get_or_create(user=self.request.user)
        return profile


class ClientAddressViewSet(viewsets.ModelViewSet):
    """Endereços de entrega do cliente autenticado."""

    serializer_class = ClientAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ClientAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        is_first = not ClientAddress.objects.filter(user=self.request.user).exists()
        is_default = serializer.validated_data.get("is_default", False) or is_first

        if is_default:
            ClientAddress.objects.filter(user=self.request.user).update(is_default=False)

        serializer.save(user=self.request.user, is_default=is_default)

    def perform_update(self, serializer):
        if serializer.validated_data.get("is_default"):
            ClientAddress.objects.filter(user=self.request.user).exclude(
                id=serializer.instance.id
            ).update(is_default=False)
        serializer.save()
