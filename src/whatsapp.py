from __future__ import annotations
import os, json
from typing import Iterable, Optional, List, Dict, Any
import requests
from dotenv import load_dotenv

load_dotenv()

API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v22.0")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "").strip()
TOKEN = os.getenv("WHATSAPP_TOKEN", "").strip()
DEFAULT_LANG = os.getenv("DEFAULT_LANG", "pt_BR").strip()

BASE_URL = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/messages"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

class WhatsAppError(Exception):
    """Erro específico para respostas da API do WhatsApp Cloud."""

def _make_body_parameters(values: Iterable[str]) -> List[Dict[str, Any]]:
    return [{"type": "text", "text": str(v)} for v in values]

def enviar_template(
        template_name: str,
        to_e164: str,
        body_params: Iterable[str],
        button_url_param: Optional[str] = None,
        lang_code: str = DEFAULT_LANG,
) -> Dict[str, Any]:
    """
    Envia um template aprovado via WhatsApp Cloud API.
    - template_name: 'lembrete_consulta_v2' ou 'consulta_comecando'
    - to_e164: número no formato E.164 sem '+', ex: '5511919941208'
    - body_params: parâmetros do corpo, na ordem do template
    - button_url_param: URL para o botão (se o template tiver botão dinâmico)
    """
    if not PHONE_NUMBER_ID or not TOKEN:
        raise RuntimeError("Configure PHONE_NUMBER_ID e WHATSAPP_TOKEN no .env.")
    
    components: List[Dict[str, Any]] = [{
        "type": "body",
        "parameters": _make_body_parameters(body_params),
    }]

    if button_url_param:
        components.append({
            "type": "button",
            "sub_type": "url",
            "index": "0",
            "parameters": [{"type": "text", "text": str(button_url_param)}],
        })

    payload = {
        "messaging_product": "whatsapp",
        "to": to_e164,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": lang_code},
            "components": components,
        },
    }

    resp = requests.post(BASE_URL, headers=HEADERS, data=json.dumps(payload), timeout=30)
    try:
        data= resp.json()
    except Exception:
        data = {"raw_text": resp.text}

    if resp.status_code >= 400:
        e = data.get("error", {})
        msg = f"HTTP {resp.status_code} ao enviar '{template_name}'. (code={e.get('code')}, subcode={e.get('error_subcode')}) {e.get('message')}"
        raise WhatsAppError(msg)
    
    return data