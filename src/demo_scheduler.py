import time
import json
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from whatsapp import enviar_template

def enviar_para_paciente_e_responsavel(template, telefone, params, responsavel=None, link=None):

    with open("src/pacientes.json", "r", encoding="utf-8") as f:
        pacientes = json.load(f)

    enviar_template(template, telefone, params, link)
    print(f"✅ Enviado {template} para paciente {telefone}")

    if responsavel:
        paciente = next((p for p in pacientes if p["telefone"] == telefone), None)
        if paciente and paciente.get("responsavel_ativo", True):
            enviar_template(template, responsavel, params, link)
            print(f"✅ Enviado {template} para responsável {responsavel}")
        else:
            print(f"⏸️ Responsável {responsavel} desativado — lembrete não enviado.")

def demo():
    with open("src/pacientes.json", "r", encoding="utf-8") as f:
        pacientes = json.load(f)

    scheduler = BackgroundScheduler()

    for paciente in pacientes:
        nome = paciente["nome"]
        telefone = paciente["telefone"]
        responsavel = paciente.get("responsavel")
        responsavel_ativo = paciente.get("responsavel_ativo")
        data = paciente["data"]
        hora = paciente["hora"]
        link = paciente["link"]

        print(f"[DEMO] Lembretes agendados para {nome} ({telefone})")

        start = datetime.now()

        scheduler.add_job(
            enviar_para_paciente_e_responsavel,
            "date",
            run_date=start,
            args=["lembrete_48h", telefone, [nome, data, hora], responsavel, None, responsavel_ativo],
        )

        scheduler.add_job(
            enviar_para_paciente_e_responsavel,
            "date",
            run_date=start + timedelta(seconds=10),
            args=["lembrete_24h", telefone, [nome, data, hora], responsavel, None, responsavel_ativo],
        )

        scheduler.add_job(
            enviar_para_paciente_e_responsavel,
            "date",
            run_date=start + timedelta(seconds=20),
            args=["lembrete__1h", telefone, [nome, hora], responsavel, None, responsavel_ativo],
        )

        scheduler.add_job(
            enviar_para_paciente_e_responsavel,
            "date",
            run_date=start + timedelta(seconds=30),
            args=["consulta_comecando", telefone, [nome, hora], responsavel, link, responsavel_ativo],
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