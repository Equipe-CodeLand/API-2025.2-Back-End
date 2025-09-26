import os
import json
from datetime import datetime
from db import get_connection

def salvar_relatorio(dados, tipo="geral", como_json=False, chat_id=1, usuario_id=1, titulo="Relatório"):
    pasta = "relatorios_salvos"
    os.makedirs(pasta, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"{tipo}_{timestamp}.{'json' if como_json else 'txt'}"
    caminho_completo = os.path.join(pasta, nome_arquivo)

    # Salvar no disco
    with open(caminho_completo, "w", encoding="utf-8") as f:
        if como_json:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        else:
            f.write(str(dados))

    print(f"Relatório salvo em: {caminho_completo}")

    # Inserir no banco
    conn = get_connection()
    cursor = conn.cursor()
    
        # Garantir que existe um chat para FK
    cursor.execute("SELECT id FROM chat LIMIT 1")
    chat_existente = cursor.fetchone()
    if chat_existente:
        chat_id = chat_existente[0]
    else:
        cursor.execute(
            "INSERT INTO chat (titulo, criado_em) VALUES (%s, NOW())",
            ("Chat de teste",)
        )
        conn.commit()
        chat_id = cursor.lastrowid


    sql = """
        INSERT INTO relatorio (chat_id, usuario_id, titulo, caminho_arquivo)
        VALUES (%s, %s, %s, %s)
    """
    valores = (chat_id, usuario_id, titulo, caminho_completo)

    cursor.execute(sql, valores)
    conn.commit()

    cursor.close()
    conn.close()

    return caminho_completo
