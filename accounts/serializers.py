from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import ClientAddress, ProducerProfile

User = get_user_model()


class ProducerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProducerProfile
        fields = [
            "farm_name",
            "farm_location",
            "farm_size",
            "certification",
            "products_type",
            "bio",
            "whatsapp",
            "address",
        ]
        # Todos editáveis via PATCH /api/accounts/producer-profile/


class RegisterSerializer(serializers.ModelSerializer):
    """
    Cadastro de cliente ou produtor.
    Se user_type == 'produtor', os campos de farm_* (perfil do produtor)
    também podem ser enviados.
    """

    password = serializers.CharField(write_only=True, min_length=6)
    farm_name = serializers.CharField(required=False, allow_blank=True, write_only=True)
    farm_location = serializers.CharField(required=False, allow_blank=True, write_only=True)
    farm_size = serializers.CharField(required=False, allow_blank=True, write_only=True)
    certification = serializers.CharField(required=False, allow_blank=True, write_only=True)
    products_type = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "email",
            "phone",
            "password",
            "user_type",
            "farm_name",
            "farm_location",
            "farm_size",
            "certification",
            "products_type",
        ]

    def validate_user_type(self, value):
        if value == User.UserType.ADMIN:
            raise serializers.ValidationError(
                "Não é permitido se cadastrar como administrador por aqui."
            )
        return value

    def create(self, validated_data):
        farm_fields = {
            "farm_name": validated_data.pop("farm_name", ""),
            "farm_location": validated_data.pop("farm_location", ""),
            "farm_size": validated_data.pop("farm_size", ""),
            "certification": validated_data.pop("certification", ""),
            "products_type": validated_data.pop("products_type", ""),
        }
        password = validated_data.pop("password")
        # username é obrigatório no AbstractUser; usamos o e-mail como username também
        validated_data["username"] = validated_data["email"]

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if user.user_type == User.UserType.PRODUTOR:
            ProducerProfile.objects.create(user=user, **farm_fields)

        return user


class UserSerializer(serializers.ModelSerializer):
    producer_profile = ProducerProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "email",
            "phone",
            "avatar",
            "user_type",
            "producer_profile",
            "date_joined",
        ]
        read_only_fields = ["id", "email", "user_type", "date_joined"]


class ClientAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientAddress
        fields = [
            "id",
            "label",
            "cep",
            "street",
            "number",
            "complement",
            "neighborhood",
            "city",
            "state",
            "is_default",
        ]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Login por e-mail + senha, retornando também os dados do usuário
    (nome, tipo etc.) junto com o token — parecido com o que o
    front-end antigo guardava em sessionStorage.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["user_type"] = user.user_type
        token["name"] = user.first_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user, context=self.context).data
        return data
