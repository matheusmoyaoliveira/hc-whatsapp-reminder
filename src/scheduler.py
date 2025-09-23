import time, json, locale, logging
from pathlib import Path
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from whatsapp import enviar_template

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

logger = setup_logger("scheduler", "scheduler.log")

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

# -------------------- agendador real --------------------
def run():
    with open("src/pacientes.json", "r", encoding="utf-8") as f:
        pacientes = json.load(f)

    scheduler = BackgroundScheduler()

    now = datetime.now()
    for p in pacientes:
        nome        = p["nome"]
        telefone    = p["telefone"]
        responsavel = p.get("responsavel")
        data_str    = p["data"]  # "15/09/2025" ou "15/09/2025, segunda-feira"
        hora_str    = p["hora"]
        link        = p.get("link")

        # parse seguro
        data_somente = data_str.split(",")[0].strip()
        consulta_dt  = datetime.strptime(f"{data_somente} {hora_str}", "%d/%m/%Y %H:%M")
        data_br, dia_semana, hora_br = fmt_data_hora_ptbr(consulta_dt)
        data_amigavel = f"{data_br}, {dia_semana}"

        print(f"🗓️ {nome} ({telefone}) | {data_amigavel} às {hora_br}")
        logger.info(f"Agendando {nome} | tel={telefone} | data={data_amigavel} | hora={hora_br}")

        def agendar(delta, template, params, with_link=False):
            run_at = consulta_dt - delta
            if run_at <= now:
                logger.warning(f"Ignorando {template} para {telefone} - horário passado ({run_at}).")
                return
            scheduler.add_job(
                enviar_para_paciente_e_responsavel, "date", run_date=run_at,
                args=[template, telefone, params, responsavel, link if with_link else None],
                misfire_grace_time=300, coalesce=True
            )
            logger.info(f"Job {template} agendado para {run_at.isoformat()} | tel={telefone}")

        # 48h, 24h, 1h e 10 min antes
        agendar(timedelta(hours=48), "lembrete_48h", [nome, data_amigavel, hora_br])
        agendar(timedelta(hours=24), "lembrete_24h", [nome, data_amigavel, hora_br])
        agendar(timedelta(hours=1),  "lembrete__1h", [nome, hora_br])
        agendar(timedelta(minutes=10), "consulta_comecando", [nome, hora_br], with_link=True)

    print("🚀 Scheduler iniciado. Aguardando envios...")
    scheduler.start()
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("🛑 Encerrando...")
    finally:
        scheduler.shutdown()
        logger.info("Scheduler finalizado.")

if __name__ == "__main__":
    run()
