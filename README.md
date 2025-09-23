# HC WhatsApp Reminder

Sistema de envio de lembretes automáticos via WhatsApp Cloud API,
integrado ao Meta Developers.

------------------------------------------------------------------------

## 🚀 Funcionalidades

-   Envio de lembretes de consultas para pacientes e responsáveis
-   Possibilidade de **pausar e reativar** lembretes via WhatsApp com
    botões interativos
-   Agendamento de mensagens com **APScheduler**
-   Templates configurados na Cloud API do WhatsApp
-   **Logs automáticos** de execução para auditoria

------------------------------------------------------------------------

## 📂 Estrutura do projeto

    .
    ├── src/
    │   ├── webhook.py          # Webhook Flask para receber mensagens do WhatsApp
    │   ├── scheduler.py        # Agendador real (produção)
    │   ├── demo_scheduler.py   # Versão de testes (lembretes a cada 10s)
    │   ├── whatsapp.py         # Funções auxiliares de envio
    │   └── pacientes.json      # Base de dados simples
    ├── .env                    # Configurações de ambiente
    └── README.md               # Documentação

------------------------------------------------------------------------

## ⚙️ Requisitos

-   Python 3.9+
-   Conta no [Meta Developers](https://developers.facebook.com/)
-   WhatsApp Cloud API configurada
-   Token de acesso e `PHONE_NUMBER_ID`

------------------------------------------------------------------------

## 🔧 Configuração

1.  Clone o repositório:

    ``` bash
    git clone https://github.com/matheusmoyaoliveira/hc-whatsapp-reminder.git
    cd hc-whatsapp-reminder
    ```

2.  Crie e ative o ambiente virtual:

    ``` powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1   # Windows PowerShell
    ```

3.  Instale as dependências:

    ``` bash
    pip install -r requirements.txt
    ```

4.  Configure o arquivo `.env`:

    ``` env
    WEBHOOK_VERIFY_TOKEN=token123
    WHATSAPP_API_VERSION=v23.0
    PHONE_NUMBER_ID=xxxxxxxxxxxx
    WHATSAPP_TOKEN=EAA...
    DEFAULT_LANG=pt_BR
    ```

------------------------------------------------------------------------

## ▶️ Executando

### 1. Subir o Webhook

``` bash
python src/webhook.py
```

-   Use o [ngrok](https://ngrok.com/) para expor:

``` bash
ngrok http 5000
```

-   Configure a URL do ngrok no painel do Meta Developers.

------------------------------------------------------------------------

### 2. Rodar a versão de teste (Demo)

``` bash
python src/demo_scheduler.py
```

-   Os lembretes são enviados **a cada 10 segundos**.
-   Ótimo para apresentações e validação.

------------------------------------------------------------------------

### 3. Rodar a versão real (Produção)

``` bash
python src/scheduler.py
```

-   Os lembretes seguem o agendamento correto (48h, 24h, 1h, etc).
-   Pacientes e responsáveis definidos no `pacientes.json`.

------------------------------------------------------------------------

## 📊 Logs

O sistema gera logs automáticos em `logs/app.log`:

-   Sucesso no envio
-   Falha ao chamar a API
-   Responsável desativado
-   Eventos de webhook

Exemplo:

    2025-09-19 18:45:12 [INFO] Enviado lembrete_24h para paciente 5511999999999
    2025-09-19 18:45:15 [INFO] Responsável 5511988888888 desativado — lembrete não enviado.
    2025-09-19 18:45:20 [ERROR] WhatsApp API retornou erro 400 ao enviar lembrete_48h

------------------------------------------------------------------------

## 📌 Observações

-   `demo_scheduler.py` serve apenas para demonstração

-   `scheduler.py` é o código de produção

-   O `pacientes.json` deve conter os pacientes e responsáveis no
    formato:

    ``` json
    [
      {
        "nome": "Matheus Moya",
        "telefone": "5511912345678",
        "responsavel": "5511998765432",
        "responsavel_ativo": true,
        "data": "15/09/2025",
        "hora": "15:00",
        "link": "https://hcclinicas.org/teleconsulta/demo"
      }
    ]
    ```

------------------------------------------------------------------------

## 👨‍💻 Autor

Matheus Moya Oliveira -- FIAP -- 1TDS-PV
