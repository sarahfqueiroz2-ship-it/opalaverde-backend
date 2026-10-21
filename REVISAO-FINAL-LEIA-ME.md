# Revisão de segurança e dados reais

## Ajustes desta versão
- Retiradas funções de geração de pedidos e vendas demonstrativas.
- Relatório financeiro simulado bloqueado para não exibir receitas fictícias.
- Pedido cancelado não pode ser reaberto e pedido entregue não pode ser cancelado pelo fluxo simples.
- Pagamento confirmado não pode retroceder para combinado; validação reexecutada sob bloqueio de banco.

## Limitações que impedem chamar esta versão de pronta para produção
- Relatórios financeiros e demais painéis legados precisam ser reconstruídos sobre dados reais.
- É necessário testar o fluxo de mensagens e o checkout com três contas e um banco de testes.
- O estoque ainda não é reservado no checkout, portanto pode esgotar antes da confirmação do pagamento.
- O armazenamento persistente de imagens precisa ser configurado no ambiente de hospedagem.
- Não foram executados testes de integração Django.

## Implantação segura
Faça backup do banco, configure variáveis de ambiente, instale requirements.txt, execute `python manage.py migrate` e teste em homologação antes de publicar.
