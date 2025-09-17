from flask import Flask, request, jsonify
import json, os

VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "token123")
app = Flask(__name__)

@app.get("/")
def health():
    return "OK - webhook no ar", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return challenge, 200
        return "Erro: token inválido", 403

    
    data = request.get_json()
    print("📩 Evento recebido:", json.dumps(data, ensure_ascii=False, indent=2))

    try:
        change = data["entry"][0]["change"][0]["value"]
        msgs = change.get("messages", [])
        if msgs:
            msg = msgs[0]
            from_number = msg["from"]

            if msg.get("text"):
                text = msg["text"]["body"].strip().lower()
                print(f"✉️ Texto de {from_number}: {text}")

            if msg.get("button"):
                payload = msg["button"]["payload"]
                print(f"🟢 Botão clicado por {from_number}: {payload}")
    except Exception as e:
        print("⚠️ Erro ao processar:", e)

    return jsonify({"status": "received"}), 200
    
if __name__ == "__main__":
    app.run(port=5000, debug=True)