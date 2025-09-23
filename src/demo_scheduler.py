# src/demo_scheduler.py
import time, json, locale, logging
from pathlib import Path
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from whatsapp import enviar_template

# ---------------- Logging ----------------
def setup_logger(name: str, file_name: str) -> logging.Logger:
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Arquivo
        fh = logging.FileHandler(logs_dir / file_name, encoding="utf-8")
        fh.setFormatter(logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%d/%m/%Y %H:%M:%S"
        ))

        # Terminal
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%d/%m/%Y %H:%M:%S"
        ))

        logger.addHandler(fh)
        logger.addHandler(sh)

    return logger

logger = setup_logger("demo", "demo.log")

# -------------------- helpers --------------------
def fmt_data_hora_ptbr(dt: datetime):
    """retorna (data_br, dia_semana, hora_br)"""
    try:
        locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
    except Exception:
        for cand in ("pt_BR", "Portuguese_Brazil.1252"):
            try:
                locale.setlocale(locale.LC_TIME, cand)
                break
            except Exception:
                pass

    dias = ["segunda-feira","terça-feira","quarta-feira","quinta-feira","sexta-feira","sábado","domingo"]

    try:
        dia_semana = dt.strftime("%A").lower()
    except Exception:
        dia_semana = dias[dt.weekday()]

    if dia_semana not in dias:
        dia_semana = dias[dt.weekday()]

    data_br = dt.strftime("%d/%m/%Y")
    hora_br = dt.strftime("%H:%M")
    return data_br, dia_semana, hora_br

def enviar_para_paciente_e_responsavel(template, telefone, params, responsavel=None, link=None):
    """envia ao paciente e, se ativo, ao responsável."""
    try:
        with open("src/pacientes.json", "r", encoding="utf-8") as f:
            pacientes = json.load(f)
    except FileNotFoundError:
        logger.error("pacientes.json não encontrado.")
        return

    try:
        enviar_template(template, telefone, params, link)
        print(f"✅ Enviado {template} para paciente {telefone}")
        logger.info(f"Enviado {template} para paciente {telefone} | params={params} | link={link}")
    except Exception as e:
        logger.error(f"Falha ao enviar {template} para paciente {telefone}: {e}")
        return

    if responsavel:
        pac = next((p for p in pacientes if p.get("telefone") == telefone), None)
        ativo = pac.get("responsavel_ativo", True) if pac else True
        if ativo:
            try:
                enviar_template(template, responsavel, params, link)
                print(f"✅ Enviado {template} para responsável {responsavel}")
                logger.info(f"Enviado {template} para responsável {responsavel} | params={params} | link={link}")
            except Exception as e:
                logger.error(f"Falha ao enviar {template} para responsável {responsavel}: {e}")
        else:
            print(f"⏸️ Responsável {responsavel} desativado — lembrete não enviado.")
            logger.warning(f"Responsável {responsavel} desativado — lembrete não enviado.")

# -------------------- demo --------------------
def demo():
    with open("src/pacientes.json", "r", encoding="utf-8") as f:
        pacientes = json.load(f)

    scheduler = BackgroundScheduler()

    for p in pacientes:
        nome        = p["nome"]
        telefone    = p["telefone"]
        responsavel = p.get("responsavel")
        data_str    = p["data"]  # pode estar "15/09/2025" OU "15/09/2025, segunda-feira"
        hora_str    = p["hora"]
        link        = p.get("link")

        # garante parsing mesmo que venha "15/09/2025, segunda-feira"
        data_somente = data_str.split(",")[0].strip()
        consulta_dt  = datetime.strptime(f"{data_somente} {hora_str}", "%d/%m/%Y %H:%M")
        data_br, dia_semana, hora_br = fmt_data_hora_ptbr(consulta_dt)
        data_amigavel = f"{data_br}, {dia_semana}"

        print(f"[DEMO] Lembretes agendados para {nome} ({telefone}) | {data_amigavel} às {hora_br}")
        logger.info(f"[DEMO] Agendando para {nome} | data={data_amigavel} | hora={hora_br} | tel={telefone}")

        start = datetime.now()

        # 48h
        scheduler.add_job(
            enviar_para_paciente_e_responsavel, "date",
            run_date=start + timedelta(seconds=0),
            args=["lembrete_48h", telefone, [nome, data_amigavel, hora_br], responsavel]
        )

        # 24h
        scheduler.add_job(
            enviar_para_paciente_e_responsavel, "date",
            run_date=start + timedelta(seconds=10),
            args=["lembrete_24h", telefone, [nome, data_amigavel, hora_br], responsavel]
        )

        # 1h
        scheduler.add_job(
            enviar_para_paciente_e_responsavel, "date",
            run_date=start + timedelta(seconds=20),
            args=["lembrete__1h", telefone, [nome, hora_br], responsavel]
        )

        # 10 min
        scheduler.add_job(
            enviar_para_paciente_e_responsavel, "date",
            run_date=start + timedelta(seconds=30),
            args=["consulta_comecando", telefone, [nome, hora_br], responsavel, link]
        )

    print("🚀 Demo iniciada — lembretes sairão a cada 10 segundos (0s, 10s, 20s, 30s).")
    scheduler.start()
    try:
        time.sleep(40)
    finally:
        scheduler.shutdown()
        print("✅ Demo finalizada.")
        logger.info("Demo finalizada.")

if __name__ == "__main__":
    demo()
