import json
import requests
import datetime

"""
Usando a API do IBGE, baixa a lista dos estados e municípios do Brasil
Site: https://servicodados.ibge.gov.br/api/docs/localidades?versao=1#api-_
"""

URL_BASE = "https://servicodados.ibge.gov.br/api/v1/localidades"
ESTADOS = "/estados"
MUNICIPIOS = "/estados/{UF}/municipios"


def baixa_json(url: str):
    req = requests.get(url)
    if req.status_code != 200:
        raise Exception(f"Erro baixando {url}: {req.status_code}")
    return req.json()


estados = baixa_json(f"{URL_BASE}{ESTADOS}")
municipios = []
for estado in estados:
    print(estado)
    municipios_do_estado = baixa_json(f"{URL_BASE}{MUNICIPIOS}".format(UF=estado["id"]))
    municipios.extend(municipios_do_estado)

with open("brasil.json", "w") as br:
    brasil = {"estados": estados,
              "municipios": municipios,
              "atualizado": datetime.datetime.now().isoformat()}
    br.write(json.dumps(brasil, indent=4))
