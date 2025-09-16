import json
import time
from datetime import datetime, timedelta
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from whatsapp import enviar_template, WhatsAppError

BASE_DIR = Path(__file__).resolve().parent
PACIENTES_PATH = BASE_DIR / "pacientes.json"

with open(PACIENTES_PATH, "r", encoding="utf-8") as f:
    pacientes = json.load(f)

scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")

def enviar_para_paciente_e_responsavel(template, telefone, params, responsavel=None, link=None):

    enviar_template(template, telefone, params, link)
    print(f"✅ Enviado {template} para paciente {telefone}")

    if responsavel:
        enviar_template(template, responsavel, params, link)
        print(f"✅ Enviado {template} para responsável {responsavel}")

def agendar_lembretes(paciente: dict):
    nome = paciente["nome"]
    telefone = paciente["telefone"]
    responsavel = paciente.get("responsavel")
    data = paciente["data"]
    hora = paciente["hora"]
    link = paciente["link"]

    consulta_dt = datetime.strptime(f"{data} {hora}", "%Y-%m-%d %H:%M")

    base_id = f"{telefone}_{data}_{hora}".replace(":", "-")

    t1 = consulta_dt - timedelta(hours=48)
    scheduler.add_job(
        enviar_para_paciente_e_responsavel,
        trigger="date",
        run_date=t1,
        args=["lembrete_48h", telefone, [nome, data, hora], responsavel],
        id=f"{base_id}_48h",
        misfire_grace_time=3600,
    )

    t2 = consulta_dt - timedelta(hours=24)
    scheduler.add_job(
        enviar_para_paciente_e_responsavel,
        trigger="date",
        run_date=t2,
        args=["lembrete_24h", telefone, [nome, data, hora], responsavel],
        id=f"{base_id}_24h",
        misfire_grace_time=3600,
    )

    t3 = consulta_dt - timedelta(hours=1)
    scheduler.add_job(
        enviar_para_paciente_e_responsavel,
        trigger="date",
        run_date=t3,
        args=["lembrete__1h", telefone, [nome, hora], responsavel],
        id=f"{base_id}_1h",
        misfire_grace_time=1800
    )

    t4 = consulta_dt - timedelta(minutes=10)
    scheduler.add_job(
        enviar_para_paciente_e_responsavel,
        trigger="date",
        run_date=t4,
        args=["consulta_comecando", telefone, [nome, hora], responsavel, link],
        id=f"{base_id}_10min",
        misfire_grace_time=900
    )

    print(f"📅 Lembretes agendados para {nome} ({telefone}) em {data} {hora}")

for paciente in pacientes:
    agendar_lembretes(paciente)

scheduler.start()
print("Scheduler iniciado. Aguardando envios...")

try:
    while True:
        time.sleep(5)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()