# HC WhatsApp Reminder 📱💬

Sistema de lembretes automáticos via WhatsApp para consultas de **telemedicina** no Hospital das Clínicas.  
O objetivo é **reduzir o absenteísmo** (faltas em consultas) enviando mensagens de aviso tanto para os **pacientes** quanto para seus **responsáveis/cuidadores**.

---

## 🚀 Funcionalidades
- Envio automático de **4 lembretes** antes da consulta:
  - 48 horas antes
  - 24 horas antes
  - 1 hora antes
  - 10 minutos antes (com link direto para a teleconsulta)
- Cada lembrete possui **template personalizado**.
- **Responsável pode pausar/reativar** o recebimento de mensagens a qualquer momento:
  - Digita `PAUSAR` → botão `CONFIRMAR` → para de receber.
  - Digita `RETORNAR` → botão `ATIVAR` → volta a receber.
- Arquivo `pacientes.json` guarda todos os pacientes, números de telefone e status do responsável (`responsavel_ativo`).
- Integração com a **WhatsApp Cloud API (Meta)** + **Flask webhook** + **ngrok**.

---

## 📂 Estrutura do Projeto

```
hc-whatsapp-reminder/
│── src/
│   ├── webhook.py          # Servidor Flask que recebe mensagens e trata comandos PAUSAR/RETORNAR
│   ├── scheduler.py        # Scheduler real (com horários em horas/dias)
│   ├── demo_scheduler.py   # Scheduler de demonstração (envios a cada 5s, usado na apresentação)
│   ├── scheduler_test.py   # Scheduler de testes
│   ├── whatsapp.py         # Funções de envio via API do WhatsApp
│   ├── pacientes.json      # Base local de pacientes + responsáveis
│   ├── generate_qr.py      # Geração de QR Code (extra para demonstração)
│   ├── main_test.py        # Testes iniciais
│
│── .env                    # Variáveis de ambiente (token, phone_id, versão da API, verify token)
│── requirements.txt        # Dependências do Python
│── README.md               # Este documento
```

---

## ⚙️ Pré-requisitos

- Python 3.10+
- Conta configurada no [Meta for Developers](https://developers.facebook.com/)
  - **WhatsApp Business Cloud API** habilitada
  - **Phone Number ID** configurado
  - **Access Token** (temporário ou de longa duração)
  - **Webhook** validado (com VERIFY_TOKEN)
- [ngrok](https://ngrok.com/) para expor o servidor local

---

## 🔧 Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/matheusmoyaoliveira/hc-whatsapp-reminder.git
   cd hc-whatsapp-reminder
   ```

2. Crie e ative um ambiente virtual:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   ```

   ⚠️ Se o PowerShell bloquear:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure o arquivo **.env** com os dados da sua aplicação no Meta:

   ```ini
   WEBHOOK_VERIFY_TOKEN=token123
   WHATSAPP_API_VERSION=v23.0
   PHONE_NUMBER_ID=seu_phone_number_id
   WHATSAPP_TOKEN=seu_access_token
   DEFAULT_LANG=pt_BR
   ```

---

## ▶️ Como rodar

### 1. Inicie o webhook (Flask)
```powershell
python src/webhook.py
```

### 2. Exponha o servidor com ngrok
```powershell
ngrok http 5000
```
- Copie a URL HTTPS gerada e cole no **Meta Developers → Webhooks → Callback URL**.  
- Use o mesmo `WEBHOOK_VERIFY_TOKEN` definido no `.env`.

### 3. Execute o demo scheduler
```powershell
python src/demo_scheduler.py
```

➡️ Este modo de demonstração envia **todos os lembretes em 5 segundos de intervalo**.  
Ideal para a **apresentação**.

---

## 🎬 Fluxo de Demonstração (apresentação)

1. **Paciente e responsável** recebem os 4 lembretes normalmente.  
2. No celular do **responsável**, enviar `PAUSAR`.  
   - O bot responde com botão **CONFIRMAR**.  
   - Ao clicar, recebe: `✅ Você parou de receber os lembretes.`  
   - O campo `"responsavel_ativo": false` é salvo no `pacientes.json`.  
3. Rodar o `demo_scheduler.py` novamente → **somente o paciente recebe**.  
4. No celular do responsável, enviar `RETORNAR`.  
   - O bot responde com botão **ATIVAR**.  
   - Ao clicar, recebe: `✅ Você voltou a receber os lembretes.`  
   - O campo `"responsavel_ativo": true` é restaurado.  
5. Rodar de novo o `demo_scheduler.py` → **paciente e responsável recebem**.

---

## 📖 Tecnologias usadas
- Python 3.10
- Flask (webhook)
- APScheduler (agendamento)
- Requests (requisições à API da Meta)
- ngrok (exposição local)
- WhatsApp Cloud API (Meta)

---

## 👨‍💻 Autores
Projeto desenvolvido como parte do **Challenge FIAP** (2025)  
Grupo: **HC Absenteísmo – Lembretes via WhatsApp**  
Integrantes:
- Matheus Moya Oliveira  
- [Demais colegas do grupo, adicionar aqui]

---

## 📌 Observações
- Em produção real, recomenda-se rodar o `scheduler.py` (com horários em horas/dias) em servidor (Heroku, Render, AWS etc.).  
- O `demo_scheduler.py` foi feito apenas para **apresentações e testes rápidos**.  
- Tokens de acesso expiram → usar tokens de longa duração ou renovação automática no Meta Developers.
