from django.conf import settings
from django.db import models
from django.db.models import Q
from rest_framework import serializers, permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.models import User
from .models import Order


class Conversation(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_conversations")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_conversations")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(max_length=3000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "sender", "content", "created_at"]
        read_only_fields = ["id", "sender", "created_at"]


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.first_name", read_only=True)
    recipient_name = serializers.CharField(source="recipient.first_name", read_only=True)

    class Meta:
        model = Conversation
        fields = ["id", "customer", "customer_name", "recipient", "recipient_name", "order", "created_at", "messages"]


class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        u = self.request.user
        return Conversation.objects.filter(Q(customer=u) | Q(recipient=u)).distinct().select_related("customer", "recipient").prefetch_related("messages")

    @action(detail=False, methods=["post"], url_path="start-support")
    def start_support(self, request):
        if request.user.user_type not in ("cliente", "produtor"):
            return Response({"detail": "Conta sem permissão para iniciar atendimento."}, status=403)

        admin = (
            User.objects.filter(user_type="admin", is_active=True)
            .exclude(pk=request.user.pk)
            .order_by("id")
            .first()
        )
        if admin is None:
            return Response({"detail": "Nenhum administrador disponível para atendimento."}, status=404)

        conv, created = Conversation.objects.get_or_create(
            customer=request.user,
            recipient=admin,
            order=None,
        )
        return Response(
            ConversationSerializer(conv).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"])
    def start(self, request):
        try:
            recipient = User.objects.get(pk=request.data.get("recipient"), user_type__in=["produtor", "admin"])
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"detail": "Destinatário inválido."}, status=400)
        if recipient.pk == request.user.pk:
            return Response({"detail": "Não é possível conversar consigo mesmo."}, status=400)
        order_id = request.data.get("order")
        order = None
        if order_id:
            try:
                order = Order.objects.get(pk=order_id)
            except (Order.DoesNotExist, ValueError, TypeError):
                return Response({"detail": "Pedido não encontrado."}, status=404)
            if order.customer_id != request.user.pk or (recipient.user_type != "admin" and not order.items.filter(producer=recipient).exists()):
                return Response({"detail": "Pedido não pertence a esta conversa."}, status=403)
        if request.user.user_type not in ("cliente", "produtor", "admin"):
            return Response({"detail": "Conta sem permissão."}, status=403)
        if request.user.user_type == "produtor" and recipient.user_type == "produtor":
            return Response({"detail": "Conversa não permitida."}, status=403)
        conv, _ = Conversation.objects.get_or_create(customer=request.user, recipient=recipient, order=order)
        return Response(ConversationSerializer(conv).data, status=201)

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        conv = self.get_object()
        content = str(request.data.get("content", "")).strip()
        if not content or len(content) > 3000:
            return Response({"detail": "Mensagem deve ter entre 1 e 3000 caracteres."}, status=400)
        msg = Message.objects.create(conversation=conv, sender=request.user, content=content)
        return Response(MessageSerializer(msg).data, status=201)
