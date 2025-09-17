import time
import json
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from whatsapp import enviar_template

def enviar_para_paciente_e_responsavel(template, telefone, params, responsavel=None, link=None):
    enviar_template(template, telefone, params, link)
    print(f"✅ Enviado {template} para paciente {telefone}")
    if responsavel:
        time.sleep(1)
        enviar_template(template, responsavel, params, link)
        print(f"✅ Enviado {template} para responsável {responsavel}")

def demo():
    with open("src/pacientes.json", "r", encoding="utf-8") as f:
        pacientes = json.load(f)

    scheduler = BackgroundScheduler()

    for paciente in pacientes:
        nome = paciente["nome"]
        telefone = paciente["telefone"]
        responsavel = paciente.get("responsavel")
        data = paciente["data"]
        hora = paciente["hora"]
        link = paciente["link"]

        print(f"[DEMO] Lembretes agendados para {nome} ({telefone})")

        start = datetime.now()

        scheduler.add_job(
            enviar_para_paciente_e_responsavel,
            "date",
            run_date=start,
            args=["lembrete_48h", telefone, [nome, data, hora], responsavel],
        )

        scheduler.add_job(
            enviar_para_paciente_e_responsavel,
            "date",
            run_date=start + timedelta(seconds=10),
            args=["lembrete_24h", telefone, [nome, data, hora], responsavel],
        )

        scheduler.add_job(
            enviar_para_paciente_e_responsavel,
            "date",
            run_date=start + timedelta(seconds=20),
            args=["lembrete__1h", telefone, [nome, hora], responsavel],
        )

        scheduler.add_job(
            enviar_para_paciente_e_responsavel,
            "date",
            run_date=start + timedelta(seconds=30),
            args=["consulta_comecando", telefone, [nome, hora], responsavel, link],
        )

    print("🚀 Demo iniciada — lembretes sairão a cada 10 segundos.")
    scheduler.start()

    try:
        time.sleep(40) 
    finally:
        scheduler.shutdown()
        print("✅ Demo finalizada.")

if __name__ == "__main__":
    demo()