import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from whatsapp import enviar_template

DESTINO = "5511919941208"
nome, data, hora = "Matheus", "2025-09-15", "18:00"
link = "https://hcclinicas.org/teleconsulta/demo"

scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")
now = datetime.now()

scheduler.add_job(
    enviar_template, 
    "date",
    run_date = now + timedelta(seconds=0),
    args=["lembrete_48h", DESTINO, [nome, data, hora]]
    )

scheduler.add_job(
    enviar_template, 
    "date",
    run_date = now + timedelta(seconds=5),
    args=["lembrete_24h", DESTINO, [nome, data, hora]]
    )

scheduler.add_job(
    enviar_template, 
    "date",
    run_date = now + timedelta(seconds=10),
    args=["lembrete__1h", DESTINO, [nome, hora]]
    )

scheduler.add_job(
    enviar_template, 
    "date",
    run_date = now + timedelta(seconds=15),
    args=["consulta_comecando", DESTINO, [nome, hora], link]
    )

scheduler.start()
print("🚀 Demo (APScheduler) iniciada — mensagens irão sair a cada 5s.")

try:
    time.sleep(25)
finally:
    scheduler.shutdown()
    print("✅ Demo finalizada.")