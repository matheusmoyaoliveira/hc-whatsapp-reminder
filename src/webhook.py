from flask import Flask, request, jsonify
import os, json, requests
from pathlib import Path

# Variáveis de ambiente
VERIFY_TOKEN       = os.getenv("WEBHOOK_VERIFY_TOKEN", "token123")
WHATSAPP_TOKEN     = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID    = os.getenv("PHONE_NUMBER_ID")
API_VERSION        = os.getenv("WHATSAPP_API_VERSION", "v23.0")

BASE_DIR           = Path(__file__).resolve().parent
PACIENTES_PATH     = BASE_DIR / "pacientes.json"

# Comandos de texto
PAUSAR_CMD         = "PAUSAR"
RETORNAR_CMD       = "RETORNAR"

app = Flask(__name__)

# -------- Funções utilitárias --------
def load_pacientes():
    if PACIENTES_PATH.exists():
        return json.loads(PACIENTES_PATH.read_text(encoding="utf-8"))
    return []

def save_pacientes(data):
    PACIENTES_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def _graph_url(path: str) -> str:
    return f"https://graph.facebook.com/{API_VERSION}/{path}"

def send_text_message(to_number: str, text: str):
    """ Envia texto simples via Cloud API """
    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        print("⚠️ WABA_TOKEN/PHONE_NUMBER_ID ausentes; não enviei mensagem.")
        return {"error": "missing_env"}

    url = _graph_url(f"{PHONE_NUMBER_ID}/messages")
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }
    r = requests.post(url, headers=headers, json=payload, timeout=15)
    print("➡️ Resposta envio texto:", r.status_code, r.text)
    return r.json()

def send_button_message(to_number: str, text: str, buttons: list):
    """ Envia mensagem com botões do tipo 'reply' """
    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        print("⚠️ WABA_TOKEN/PHONE_NUMBER_ID ausentes; não enviei mensagem.")
        return {"error": "missing_env"}

    url = _graph_url(f"{PHONE_NUMBER_ID}/messages")
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": text},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": b["id"], "title": b["title"]}}
                    for b in buttons
                ]
            }
        }
    }
    r = requests.post(url, headers=headers, json=payload, timeout=15)
    print("➡️ Resposta envio botão:", r.status_code, r.text)
    return r.json()

# -------- Rotas --------
@app.get("/")
def health():
    return "OK - webhook ativo", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    # Validação inicial do webhook
    if request.method == "GET":
        token     = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        mode      = request.args.get("hub.mode")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Erro: token inválido", 403

    # Tratamento de mensagens recebidas
    data = request.get_json(silent=True, force=True)
    print("📩 Evento recebido:", json.dumps(data, ensure_ascii=False, indent=2))

    try:
        entries = data.get("entry", [])
        for e in entries:
            changes = e.get("changes", [])
            for ch in changes:
                value    = ch.get("value", {})
                messages = value.get("messages", [])
                if not messages:
                    continue

                msg         = messages[0]
                from_number = msg.get("from")
                text_obj    = msg.get("text")
                button_obj  = msg.get("button")

                pacientes = load_pacientes()

                # ------ TEXTO ------
                if text_obj:
                    text = (text_obj.get("body") or "").strip().upper()
                    print(f"✉️ Texto de {from_number}: {text}")

                    if text == PAUSAR_CMD:
                        send_button_message(
                            from_number,
                            "Você pediu para parar de receber os lembretes. Confirme abaixo:",
                            [{"id": "confirmar", "title": "CONFIRMAR"}]
                        )

                    elif text == RETORNAR_CMD:
                        send_button_message(
                            from_number,
                            "Deseja voltar a receber os lembretes? Clique abaixo:",
                            [{"id": "ativar", "title": "ATIVAR"}]
                        )

                    else:
                        send_text_message(
                            from_number,
                            "Comandos disponíveis:\n- PAUSAR (para parar de receber)\n- RETORNAR (para voltar a receber)"
                        )

                # ------ BOTÕES ------
                interactive_obj = msg.get("interactive")
                if interactive_obj and interactive_obj.get("type") == "button_reply":
                    button_reply = interactive_obj.get("button_reply", {})
                    payload = button_reply.get("id")
                    print(f"🟢 Botão clicado por {from_number}: {payload}")

                if payload == "confirmar":
                    for p in pacientes:
                        if p.get("responsavel") == from_number:
                            p["responsavel_ativo"] = False
                    save_pacientes(pacientes)
                    send_text_message(from_number, "✅ Você parou de receber os lembretes.")

                elif payload == "ativar":
                    for p in pacientes:
                        if p.get("responsavel") == from_number:
                            p["responsavel_ativo"] = True
                    save_pacientes(pacientes)
                    send_text_message(from_number, "✅ Você voltou a receber os lembretes.")

    except Exception as e:
        print("⚠️ Erro ao processar:", e)

    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
