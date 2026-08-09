# OpalaVerde — Backend (Django + PostgreSQL)

API do marketplace de orgânicos OpalaVerde (Pedro II - PI), com 3 tipos de
usuário: **Cliente**, **Produtor** e **Admin**.

Testado de ponta a ponta: cadastro, login (JWT), catálogo, favoritos,
checkout com cálculo de preço no servidor, pedidos por perfil e avaliações.

## Stack

- Python 3.12 + Django 6
- Django REST Framework + SimpleJWT (autenticação por token)
- PostgreSQL (produção) / SQLite (fallback automático em desenvolvimento)
- django-cors-headers, django-filter, whitenoise, Pillow

## Estrutura

```
config/       -> configurações do projeto (settings, urls)
accounts/     -> usuários (cliente/produtor/admin), perfil de produtor, endereços
catalog/      -> categorias, produtos, imagens, favoritos
orders/       -> pedidos, itens do pedido, checkout
reviews/      -> avaliações de produtos
```

## Rodando localmente

1. Crie e ative um ambiente virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Copie o arquivo de variáveis de ambiente:
   ```bash
   cp .env.example .env
   ```
   Sem preencher `DATABASE_URL`, o projeto usa **SQLite automaticamente** —
   ótimo pra testar rápido sem instalar Postgres. Se quiser usar Postgres
   localmente, preencha `DATABASE_URL` no `.env`.

4. Rode as migrações e crie um superusuário (pra acessar `/admin/`):
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. Suba o servidor:
   ```bash
   python manage.py runserver
   ```
   A API fica em `http://127.0.0.1:8000/api/...` e o admin em
   `http://127.0.0.1:8000/admin/`.

## Publicando no Render (PostgreSQL)

**Opção A — usando o `render.yaml` (Blueprint, recomendado):**

1. Suba este projeto para um repositório no GitHub.
2. No Render, clique em **New > Blueprint** e aponte para o repositório.
3. O Render lê o `render.yaml` e cria sozinho o banco PostgreSQL e o serviço
   web, já conectando o `DATABASE_URL` automaticamente.
4. Depois do primeiro deploy, crie o superusuário direto no shell do Render
   (aba **Shell** do serviço):
   ```bash
   python manage.py createsuperuser
   ```

**Opção B — configurando manualmente:**

1. Crie um banco **PostgreSQL** no Render.
2. Crie um **Web Service** apontando para este repositório:
   - Build Command: `./build.sh`
   - Start Command: `gunicorn config.wsgi:application`
3. Em **Environment**, adicione as variáveis:
   - `SECRET_KEY` (gere uma aleatória)
   - `DEBUG` = `False`
   - `ALLOWED_HOSTS` = `.onrender.com`
   - `DATABASE_URL` = a "Internal Database URL" do banco Postgres criado
   - `CORS_ALLOW_ALL_ORIGINS` = `True` (ajuste depois para o domínio real do
     frontend, usando `CORS_ALLOWED_ORIGINS`)
4. Deploy. O `build.sh` já roda `migrate` e `collectstatic` automaticamente
   a cada deploy.

> ⚠️ **Sobre imagens de produto**: o disco do Render é efêmero (os arquivos
> enviados via `/media/` somem a cada novo deploy). Para produção de verdade,
> configure um storage externo (Cloudinary, AWS S3 etc.) mais adiante. Por
> enquanto, upload de imagem funciona bem para testar/apresentar o projeto.

## Principais endpoints da API

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/api/accounts/register/` | Cadastro de cliente ou produtor |
| POST | `/api/auth/token/` | Login (retorna `access` + `refresh` JWT) |
| POST | `/api/auth/token/refresh/` | Renova o `access` token |
| GET/PATCH | `/api/accounts/me/` | Dados do usuário logado |
| GET/POST | `/api/accounts/addresses/` | Endereços do cliente |
| GET/POST | `/api/catalog/categories/` | Categorias (criar/editar só admin) |
| GET/POST | `/api/catalog/products/` | Produtos (`?category=&search=&producer=`) |
| GET | `/api/catalog/products/mine/` | Produtos do produtor logado |
| GET/POST/DELETE | `/api/catalog/favorites/` | Favoritos do cliente logado |
| GET | `/api/orders/orders/` | Pedidos (cliente vê os seus, produtor vê os que tem itens dele, admin vê todos) |
| POST | `/api/orders/orders/checkout/` | Finaliza o pedido a partir do carrinho |
| PATCH | `/api/orders/orders/{id}/update_status/` | Produtor/admin atualiza status do pedido |
| GET/POST | `/api/reviews/reviews/?product={id}` | Avaliações de um produto |
| PATCH | `/api/reviews/reviews/{id}/reply/` | Produtor responde a uma avaliação |

Todas as rotas que exigem login usam o cabeçalho:
```
Authorization: Bearer <access_token>
```

## Regras de negócio já implementadas

- Login é feito por **e-mail**, não por username.
- Senhas nunca ficam em texto puro — usam o hashing padrão do Django.
- O **preço no checkout é sempre lido do banco de dados**, nunca do que o
  front-end envia — evita alguém adulterar o preço no navegador.
- O **estoque é descontado automaticamentente** ao finalizar um pedido, e o
  checkout barra a compra se não houver estoque suficiente.
- Só o **admin** pode criar/editar/apagar categorias.
- Só o **produtor dono do produto** (ou admin) pode editar/apagar aquele
  produto.
- Um pedido pode ter produtos de **vários produtores**; cada produtor só
  enxerga, nos pedidos, os itens que ele mesmo vendeu.

## Próximo passo

Este backend ainda não está conectado ao front-end (os 23 arquivos HTML
originais, que hoje usam `localStorage`). Essa é a próxima etapa: trocar as
chamadas de `localStorage`/dados fixos por chamadas `fetch()` para esta API.
