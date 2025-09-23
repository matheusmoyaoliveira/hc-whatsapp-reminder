# src/webhook.py
from flask import Flask, request, jsonify
import os, json, requests, logging
from pathlib import Path

# -------------------- logging --------------------
def setup_logger(name: str, file_name: str) -> logging.Logger:
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        fh = logging.FileHandler(logs_dir / file_name, encoding="utf-8")
        sh = logging.StreamHandler()
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        fh.setFormatter(fmt); sh.setFormatter(fmt)
        logger.addHandler(fh); logger.addHandler(sh)
    return logger

logger = setup_logger("webhook", "webhook.log")

# -------------------- env/config --------------------
VERIFY_TOKEN    = os.getenv("WEBHOOK_VERIFY_TOKEN", "token123")
WHATSAPP_TOKEN  = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
API_VERSION     = os.getenv("WHATSAPP_API_VERSION", "v23.0")

BASE_DIR        = Path(__file__).resolve().parent
PACIENTES_PATH  = BASE_DIR / "pacientes.json"

PAUSAR_CMD   = "PAUSAR"
RETORNAR_CMD = "RETORNAR"

app = Flask(__name__)

def load_pacientes():
    if PACIENTES_PATH.exists():
        return json.loads(PACIENTES_PATH.read_text(encoding="utf-8"))
    return []

def save_pacientes(data):
    PACIENTES_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _graph_url(path: str) -> str:
    return f"https://graph.facebook.com/{API_VERSION}/{path}"

def send_text_message(to_number: str, text: str):
    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        logger.error("WHATSAPP_TOKEN/PHONE_NUMBER_ID ausentes; não enviei mensagem.")
        return
    url = _graph_url(f"{PHONE_NUMBER_ID}/messages")
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to_number, "type": "text", "text": {"body": text}}
    r = requests.post(url, headers=headers, json=payload, timeout=15)
    logger.info(f"Resposta envio texto ({to_number}): {r.status_code} {r.text[:200]}")

def send_button_message(to_number: str, text: str, buttons: list):
    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        logger.error("WHATSAPP_TOKEN/PHONE_NUMBER_ID ausentes; não enviei botão.")
        return
    url = _graph_url(f"{PHONE_NUMBER_ID}/messages")
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": text},
            "action": {"buttons": [{"type": "reply", "reply": {"id": b["id"], "title": b["title"]}} for b in buttons]}
        }
    }
    r = requests.post(url, headers=headers, json=payload, timeout=15)
    logger.info(f"Resposta envio botão ({to_number}): {r.status_code} {r.text[:200]}")

# -------------------- routes --------------------
@app.get("/")
def health():
    return "OK - webhook ativo", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # verificação (GET)
    if request.method == "GET":
        token     = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        mode      = request.args.get("hub.mode")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            logger.info("Verificação de webhook OK")
            return challenge, 200
        logger.warning("Verificação de webhook FALHOU")
        return "Erro: token inválido", 403

    # eventos (POST)
    data = request.get_json(silent=True, force=True) or {}
    logger.info(f"Evento recebido: {json.dumps(data, ensure_ascii=False)}")

    try:
        entries = data.get("entry", [])
        for e in entries:
            for ch in e.get("changes", []):
                value = ch.get("value", {})

                # 1) botões (interactive.button_reply)
                messages = value.get("messages", [])
                if messages:
                    msg = messages[0]
                    from_number = msg.get("from")

                    interactive_obj = msg.get("interactive")
                    if interactive_obj and interactive_obj.get("type") == "button_reply":
                        button_reply = interactive_obj.get("button_reply", {})
                        payload = button_reply.get("id")  # "confirmar" | "ativar"
                        logger.info(f"Botão clicado por {from_number}: {payload}")

                        pacientes = load_pacientes()
                        if payload == "confirmar":
                            for p in pacientes:
                                if p.get("responsavel") == from_number:
                                    p["responsavel_ativo"] = False
                            save_pacientes(pacientes)
                            send_text_message(from_number, "✅ Você parou de receber os lembretes.")
                            logger.info(f"{from_number} -> responsavel_ativo=False")

                        elif payload == "ativar":
                            for p in pacientes:
                                if p.get("responsavel") == from_number:
                                    p["responsavel_ativo"] = True
                            save_pacientes(pacientes)
                            send_text_message(from_number, "✅ Você voltou a receber os lembretes.")
                            logger.info(f"{from_number} -> responsavel_ativo=True")
                        return jsonify({"status": "ok"}), 200

                    # 2) textos simples (PAUSAR / RETORNAR)
                    text_obj = msg.get("text")
                    if text_obj:
                        body = (text_obj.get("body") or "").strip().upper()
                        logger.info(f"Texto de {from_number}: {body}")

                        if body == PAUSAR_CMD:
                            send_button_message(
                                from_number,
                                "Você pediu para parar de receber os lembretes. Confirme abaixo:",
                                [{"id": "confirmar", "title": "CONFIRMAR"}]
                            )
                        elif body == RETORNAR_CMD:
                            send_button_message(
                                from_number,
                                "Deseja voltar a receber os lembretes? Clique abaixo:",
                                [{"id": "ativar", "title": "ATIVAR"}]
                            )
                        else:
                            send_text_message(
                                from_number,
                                "Comandos: PAUSAR (parar de receber) • RETORNAR (voltar a receber)"
                            )
                        return jsonify({"status": "ok"}), 200

                # 3) statuses (entregue/lido) – útil para auditoria
                statuses = value.get("statuses", [])
                for st in statuses:
                    logger.info(f"Status recebido: {json.dumps(st, ensure_ascii=False)}")

    except Exception as e:
        logger.exception(f"Erro ao processar webhook: {e}")

    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
