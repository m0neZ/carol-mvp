# ShopperGPT - AI Personal Shopper for WhatsApp

## Visão Geral

ShopperGPT é um assistente de compras pessoal baseado em IA que opera via WhatsApp. Ele compreende as necessidades, preferências e contexto do usuário para fornecer recomendações de produtos personalizadas, com potencial de monetização através de links de afiliados.

Este repositório contém o código-fonte da API backend e do dashboard administrativo.

## Arquitetura

A arquitetura do sistema está detalhada no arquivo `arquitetura_shoppergpt.md`.

## Estrutura do Projeto

```
.
├── .env.example        # Exemplo de arquivo de variáveis de ambiente
├── .gitignore          # Arquivos e pastas a serem ignorados pelo Git
├── README.md           # Este arquivo
├── requirements.txt    # Dependências Python
├── render.yaml         # Configuração de implantação para Render.com
├── DEPLOYMENT_GUIDE_RENDER.md # Guia detalhado de implantação no Render
├── arquitetura_shoppergpt.md # Documento de arquitetura
└── src/
    ├── __init__.py
    ├── main.py           # Ponto de entrada da API FastAPI
    ├── config.py         # Carrega configurações e variáveis de ambiente
    ├── models.py         # Modelos SQLAlchemy (DB) e Pydantic (API)
    ├── db_manager.py     # Funções para interação com o banco de dados (CRUD)
    ├── whatsapp_handler.py # Lógica para lidar com webhooks e mensagens do WhatsApp
    ├── ai_service.py     # Integração com o modelo de linguagem (OpenAI)
    ├── recommendation_engine.py # Lógica de recomendação de produtos (Placeholder)
    ├── affiliate_manager.py # Lógica de integração com APIs de afiliados (Placeholder)
    ├── admin_routes.py   # Rotas (API e UI) para o dashboard administrativo
    ├── templates/        # Templates HTML (Jinja2) para o dashboard
    │   ├── base.html
    │   ├── admin_dashboard.html
    │   ├── admin_users.html
    │   └── admin_user_details.html
    └── static/           # Arquivos estáticos (CSS, JS) para o dashboard (se necessário)
```
*Nota: O diretório `venv` (ambiente virtual) e o arquivo `.env` (com credenciais) não devem ser versionados.* 

## Configuração do Ambiente Local

1.  **Clonar o repositório:**
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO_GITHUB>
    cd shoppergpt
    ```
2.  **Criar e ativar ambiente virtual:**
    ```bash
    python3.11 -m venv venv
    source venv/bin/activate  # Linux/macOS
    # ou
    # venv\Scripts\activate  # Windows
    ```
3.  **Instalar dependências:**
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```
4.  **Configurar Variáveis de Ambiente:**
    *   Copie o arquivo `.env.example` para `.env`:
        ```bash
        cp .env.example .env # Linux/macOS
        # ou
        # copy .env.example .env # Windows
        ```
    *   Edite o arquivo `.env` e preencha com suas credenciais reais (OpenAI, WhatsApp, Admin).
    *   Para desenvolvimento local, você pode deixar `DATABASE_URL` vazio para usar o SQLite (`shoppergpt.db`) ou configurar uma string de conexão PostgreSQL se preferir.

## Executando a Aplicação (Desenvolvimento Local)

1.  **Ative o ambiente virtual** (se ainda não estiver ativo).
2.  **(Opcional, apenas na primeira vez ou se o DB não existir):** Inicialize o banco de dados SQLite:
    ```bash
    python src/db_manager.py
    ```
3.  **Inicie o servidor Uvicorn:**
    ```bash
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload --app-dir .
    ```
    *   `--reload`: Reinicia o servidor automaticamente ao detectar mudanças no código.
    *   `--app-dir .`: Define o diretório raiz do projeto para importações corretas.
    *   Acesse a API em `http://localhost:8000` e a documentação interativa em `http://localhost:8000/docs`.
    *   Acesse o dashboard administrativo em `http://localhost:8000/admin/` (login padrão: `admin`/`changeme`).

## Implantação (Deploy)

Este projeto está configurado para implantação fácil na plataforma **Render** usando o arquivo `render.yaml`.

Consulte o guia detalhado **[DEPLOYMENT_GUIDE_RENDER.md](DEPLOYMENT_GUIDE_RENDER.md)** para instruções passo a passo sobre como implantar a aplicação no Render usando o plano gratuito.

## Endpoints da API

*   **`/health` (GET):** Verifica o status da API.
*   **`/whatsapp/webhook` (GET):** Usado pelo WhatsApp para verificar a assinatura do webhook (requer `hub.mode`, `hub.verify_token`, `hub.challenge` como query parameters).
*   **`/whatsapp/webhook` (POST):** Recebe notificações de mensagens e eventos do WhatsApp.
*   **`/docs` (GET):** Interface interativa do Swagger UI para a API.
*   **`/redoc` (GET):** Interface alternativa de documentação ReDoc.

## Dashboard Administrativo

*   **Acesso:** `/admin/` (relativo à URL base da sua implantação ou `http://localhost:8000/admin/` localmente).
*   **Login:** Use as credenciais definidas em `ADMIN_USERNAME` e `ADMIN_PASSWORD` no arquivo `.env`.
*   **Funcionalidades:** Visualização de usuários, detalhes, histórico de conversas e lista de desejos.
*   **Endpoints da API do Admin (requerem autenticação Basic):** `/admin/api/*`

## Notas Importantes

*   **Banco de Dados:** A configuração padrão para desenvolvimento local usa SQLite. A configuração de implantação no `render.yaml` utiliza o serviço PostgreSQL gratuito do Render.
*   **Integração WhatsApp:** Requer configuração prévia no painel Meta for Developers (Webhook URL e Verify Token).
*   **Integração OpenAI:** Requer uma chave de API válida.
*   **Sistema de Recomendação e Afiliados:** As implementações atuais (`src/recommendation_engine.py`, `src/affiliate_manager.py`) são *placeholders* e precisam ser desenvolvidas com lógica real e integração com APIs de terceiros.
*   **Segurança:** A autenticação do admin usa Basic Auth. Para produção, considere um método mais robusto (ex: OAuth2/JWT).

## Próximos Passos / Melhorias

*   Implementar lógica real nos módulos de recomendação e afiliados.
*   Adicionar mais funcionalidades ao LLM (gerenciamento de wishlist, compreensão de imagens).
*   Melhorar a formatação das mensagens do WhatsApp.
*   Implementar migrações de banco de dados (ex: Alembic).
*   Aprimorar a segurança.
*   Adicionar testes unitários e de integração.
*   Configurar logging.
*   Considerar Dockerização para portabilidade.

