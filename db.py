import sqlite3
import os.path
from contextlib import closing
from pony.orm import Database, Required, Optional, Set, show, \
                     db_session, OperationalError, sql_debug, count
from datetime import datetime
from unicodedata import normalize


db = Database()

#
# Entidades
#


class Regiao(db.Entity):
    """Regiões do Brasil"""
    nome = Required(str)
    estados = Set('Estado')


class Estado(db.Entity):
    """Estado da federação"""
    _table_ = "estados"
    sigla = Required(str)
    nome = Required(str)
    nome_sem_acentos = Optional(str)
    regiao = Required(Regiao, column="regiao_id")
    membros = Set('Membro')


class Membro(db.Entity):
    """Membro do grupo"""
    _table_ = "membros"
    nome = Required(str)
    estado = Required(Estado)
    telegram = Optional(int)
    username = Required(str)


class Evento(db.Entity):
    """Evento organizado pelo grupo ou interessante para o mesmo"""
    _table_ = "eventos"
    data = Required(datetime)
    descricao = Required(str)
    link = Required(str)
    telegram = Optional(int)

#
# Constantes
#

REGIOES = {1: "Norte",
           2: "Nordeste",
           3: "Centro-oeste",
           4: "Sudeste",
           5: "Sul",
           6: "Exterior"}


ESTADOS = {"AC": ["Acre", 1],
           "AP": ["Amapá", 1],
           "AM": ["Amazonas", 1],
           "PA": ["Pará", 1],
           "RO": ["Rondônia", 1],
           "RR": ["Roraima", 1],
           "TO": ["Tocantins", 1],
           "PE": ["Pernambuco", 2],
           "CE": ["Ceará", 2],
           "MA": ["Maranhão", 2],
           "BA": ["Bahia", 2],
           "PB": ["Paraíba", 2],
           "RN": ["Rio Grande do Norte", 2],
           "AL": ["Alagoas", 2],
           "PI": ["Piauí", 2],
           "SE": ["Sergipe", 2],
           "GO": ["Goiás", 3],
           "MT": ["Mato Grosso", 3],
           "DF": ["Distrito Federal", 3],
           "MS": ["Mato Grosso do Sul", 3],
           "SP": ["São Paulo", 4],
           "MG": ["Minas Gerais", 4],
           "RJ": ["Rio de Janeiro", 4],
           "ES": ["Espírito Santo", 4],
           "RS": ["Rio Grande do Sul", 5],
           "PR": ["Paraná", 5],
           "SC": ["Santa Catarina", 5],
           "EX": ["Exterior", 6]
           }


def sem_acentos(texto):
    """Tira acentos de texto"""
    return normalize("NFKD", texto).encode('ASCII','ignore').decode('ASCII')


@db_session
def atualiza_regioes():
    for id, nome in REGIOES.items():
        regiao = Regiao.select().filter(id=id).first()
        if regiao:
            if regiao.nome != nome:
                regiao.nome = nome
        else:
            Regiao(nome=nome, id=id)


@db_session
def atualiza_estados():
    for sigla, nome_regiao in ESTADOS.items():
        nome_estado, regiao = nome_regiao
        estado = Estado.select().filter(sigla=sigla).first()
        if estado:
            nome_sem_acentos = sem_acentos(nome_estado).lower()
            if estado.nome_sem_acentos != nome_sem_acentos:
                estado.nome_sem_acentos = nome_sem_acentos
            if estado.nome != nome_estado:
                estado.nome = nome_estado
            if estado.regiao.get_pk() != regiao:
                print("Regiao diferente", estado.regiao.get_pk(), regiao)


@db_session
def lista():
    """Usada no início do bot para mostrar a situação atual do banco"""
    print("Regiões")
    for regiao in Regiao.select().order_by(Regiao.id):
        print(regiao.nome)
    print("Estados")
    for estado in Estado.select().order_by(Estado.id):
        print(estado.id, estado.sigla, estado.nome)
    print("Membros")
    for membro in Membro.select().order_by(Membro.nome):
        print("{0:5} {1:50} {2}".format(
            membro.id, membro.nome, membro.estado.nome, membro.telegram))


@db_session
def get_estado(estado):
    """Tenta pesquisar o estado por sigla ou por nome"""
    nome = sem_acentos(estado).lower()
    sigla = estado.upper()
    print("***", nome, sigla)
    return Estado.select(lambda e: e.nome_sem_acentos == nome or e.sigla == sigla).first()


@db_session
def get_stats():
    """Estatísticas por estado. Retorna uma tupla:
       Primeiro elemento: uma lista com a quantidade de membros por estado
       Segundo elemento: o total de membros"""
    por_estado = db.execute(
        """select e.nome, count(*), e.regiao_id
                from membros m, estados e
                where m.estado=e.id
                group by e.nome, e.regiao_id
                order by e.regiao_id, e.nome""").fetchall()

    total = Membro.select().count()
    return (por_estado, total)


@db_session
def get_eventos():
    """Retorna lista de eventos futuros"""
    return Evento.select(lambda e: e.data >= datetime.now()).order_by(Evento.data)[:]

@db_session
def get_eventos_admin():
    """Retorna lista de eventos"""
    return Evento.select().order_by(Evento.data)[:]


@db_session
def get_evento_admin(id):
    """Retorna um evento"""
    return Evento.select().filter(id=id).first()


@db_session
def edita_evento(id, **kwargs):
    evento = get_evento_admin(id)
    for k, v in kwargs.items():
        setattr(evento, k, v)


@db_session
def cria_evento(**kwargs):
    return Evento(**kwargs)


@db_session
def apaga_evento(id):
    evento = get_evento_admin(id)
    evento.delete()

def pega_nome(user):
    """Função para formatar o nome do usuário"""
    if user.last_name:
        return "{0.first_name} {0.last_name}".format(user)
    else:
        return "{0.first_name}".format(user)


def pega_nome_com_estado(nome, estado, username):
    if username:
        nome = "{0} (@{1})".format(nome, username)
    return "{0}, {1}".format(nome, estado)


@db_session
def update_user(from_user, estado):
    id = from_user.id
    estado = get_estado(estado)
    membro = Membro.select(lambda m: m.telegram == id).first()
    if membro is None:
        Membro(nome=pega_nome(from_user), estado=estado,
               telegram=id, username=from_user.username)
    else:
        membro.nome = pega_nome(from_user)
        membro.estado = estado
        membro.username = from_user.username
        membro.telegram = id


@db_session
def lista_users():
    usuarios = ["Membros por Estado:"]
    for membro in  db.Membro.select().order_by(
            lambda m: (m.estado.regiao.nome, m.estado.nome, m.nome)):
        usuarios.append(pega_nome_com_estado(membro.nome, membro.estado.nome, membro.username))
    return "\n".join(usuarios)


@db_session
def lista_users_por_nome():
    usuarios = ["Membros:"]
    for membro in db.Membro.select().order_by(Membro.nome):
        usuarios.append(
            pega_nome_com_estado(membro.nome, membro.estado.nome, membro.username))
    return "\n".join(usuarios)


def inicializa(nome="membros.db"):
    db.bind(provider='sqlite', filename=nome, create_db=True)
    while True:
        try:
            db.generate_mapping(create_tables=True)
            break
        except OperationalError as oe:
            """ORM do homem pobre"""
            menssagem = str(oe)
            if menssagem == "no such column: estados.nome_sem_acentos":
                with db_session:
                    db.execute("alter table estados add nome_sem_acentos")
    atualiza_regioes()
    atualiza_estados()

