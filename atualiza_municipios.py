import os
import json
from db import Estado, Municipio, inicializa, db_session, sem_acentos


DB_NAME = os.getenv('BOT_DB', "membros.db")


inicializa(DB_NAME)

# Tabela com o id de cada estado
db_estados = {}

with db_session:
    for estado in Estado.select():
        print(estado.id, estado.sigla, estado.nome)
        db_estados[estado.sigla] = estado.id

# Carrega os dados do ibge
with open("brasil.json", "r") as brasil:
    ibge_data = json.load(brasil)

# Tabela para converter os ids do ibge pros ids dos banco de membros (estados)
ibge_estados_id = {}

for estado in ibge_data["estados"]:
    print(estado)
    ibge_estados_id[estado["id"]] = db_estados[estado["sigla"]]

# Carrega os municipios do Brasil
with db_session:
    for municipio in ibge_data["municipios"]:
        ibge_id, nome, uf_id = (municipio["id"], municipio["nome"],
                                municipio["microrregiao"]["mesorregiao"]["UF"]["id"])
        m = Municipio.get(id=ibge_id)
        if m is None:
            Municipio(
                id=ibge_id, nome=nome, estado=ibge_estados_id[uf_id],
                nome_sem_acentos=sem_acentos(nome).lower(),
                codigo=str(ibge_id))
