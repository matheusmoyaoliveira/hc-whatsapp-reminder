from whatsapp import enviar_templates, WhatsAppError

DESTINO = "5511919941208"

def teste_lembrete():
    print("Enviando 'lembrete_consulta_v2'...")
    resp = enviar_templates(
        "lembrete_consulta_v2",
        DESTINO,
        ["Matheus Moya de Oliveira", "12/09/2025", "18:00"],
        "https://hcclinicas.org/teleconsulta/demo",
    )
    print("OK:", resp)

def teste_comecando():
    print("Enviando 'consulta_comecando'...")
    resp = enviar_templates(
        "consulta_comecando",
        DESTINO,
        ["Matheus Moya de Oliveira", "18:00"],
        "https://hcclinicas.org/teleconsulta/demo",
    )
    print("OK:", resp)

if __name__ == "__main__":
    try:
        teste_lembrete()
        teste_comecando()
    except WhatsAppError as e:
        print("ERRO: ", e)