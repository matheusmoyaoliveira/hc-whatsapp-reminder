import json
import time
from datetime import datetime, timedelta
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from whatsapp import enviar_template

BASE_DIR = Path(__file__).resolve().parent
PACIENTES_PATH = BASE_DIR / "pacientes.json"

with open(PACIENTES_PATH, "r", encoding="utf-8") as f:
    pacientes = json.load(f)

scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")

def agendar_lembretes_teste(paciente: dict):
    nome = paciente["nome"]
    telefone = paciente["telefone"]
    hora = paciente["hora"]
    link = paciente["link"]

    now = datetime.now()

    scheduler.add_job(
        enviar_template,
        trigger="date",
        run_date=now + timedelta(seconds=20),
        args=["lembrete_48h", telefone, [nome, "TESTE-DATA", hora]],
        id=f"{telefone}_48h"
    )

    scheduler.add_job(
        enviar_template,
        trigger="date",
        run_date=now + timedelta(seconds=40),
        args=["lembrete_24h", telefone, [nome, "TESTE-DATA", hora]],
        id=f"{telefone}_24h"
    )

    scheduler.add_job(
        enviar_template,
        trigger="date",
        run_date=now + timedelta(seconds=60),
        args=["lembrete__1h", telefone, [nome, hora]],
        id=f"{telefone}_1h"
    )

    scheduler.add_job(
        enviar_template,
        trigger="date",
        run_date=now + timedelta(seconds=80),
        args=["consulta_comecando", telefone, [nome, hora], link],
        id=f"{telefone}_10min"
    )

    print(f"[TESTE] Lembretes agendados para {nome} ({telefone})")

for paciente in pacientes:
    agendar_lembretes_teste(paciente)

scheduler.start()

print("Scheduler de TESTE iniciado. Aguardando envios...")
try:
    while True:
        time.sleep(5)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
