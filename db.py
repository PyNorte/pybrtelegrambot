import sqlite3
import os.path
from contextlib import closing

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

__DB_NAME = None


def cria_banco():
    with conecta() as conn:
        with closing(conn.cursor()) as c:
            c.execute('''CREATE TABLE estados
                     (id INTEGER PRIMARY KEY, sigla text, nome text, regiao_id integer)''')
            c.execute('''CREATE TABLE membros
                     (id INTEGER PRIMARY KEY, nome text, estado integer, telegram integer)''')
            c.execute("""CREATE TABLE eventos
                         (id INTEGER PRIMARY KEY, data timestamp, descricao text, link text,
                          telegram integer)""")
            conn.commit()


def atualiza_estados():
    with conecta() as conn:
        with closing(conn.cursor()) as c:
            for sigla, estado in ESTADOS.items():
                nome_estado, regiao = estado
                c.execute("""select id, sigla, nome, regiao_id from estados where sigla = ?""",
                          (sigla,))
                estado = c.fetchone()
                if not estado:
                    c.execute("""insert into estados(sigla, nome, regiao_id) values(?,?,?)""",
                              (sigla, nome_estado, regiao))
                else:
                    c.execute("""update estados
                                 set nome = ?, regiao_id = ? where sigla = ?""",
                              (nome_estado, regiao, sigla))
            conn.commit()


def lista():
    with conecta() as conn:
        with closing(conn.cursor()) as c:
            print("Estados")
            for linha in c.execute("""select id, sigla, nome from estados"""):
                print(linha)
            print("Membros")
            for linha in c.execute("""select id, nome, estado, telegram from membros"""):
                print(linha)


def get_estado(estado):
    with conecta() as conn:
        with closing(conn.cursor()) as c:
            c.execute(u"""select id, sigla, nome from estados where sigla = ? or nome = ?""",
                      (estado.upper(), estado.title()))
            estado = c.fetchone()
            if estado is None:
                return None
            else:
                return estado[0]


def get_stats():
    with conecta() as conn:
        with closing(conn.cursor()) as c:
            c.execute(u"""select e.nome, count(*), e.regiao_id
                          from membros m, estados e
                          where m.estado=e.id
                          group by e.nome, e.regiao_id
                          order by e.regiao_id, e.nome""")
            por_estado = c.fetchall()
            c.execute(u"""select count(*)
                          from membros m""")
            total = c.fetchone()[0]
            return [por_estado, total]


def get_eventos():
    with conecta() as conn:
        with closing(conn.cursor()) as c:
            c.execute(u"""select * from eventos
                          where data >= datetime('now')
                          order by data""")
            eventos = c.fetchall()
            print(eventos)
            return eventos


def update_user(from_user, estado):
    with conecta() as conn:
        with closing(conn.cursor()) as c:
            id = from_user.id
            c.execute("select id, nome, estado, telegram from membros where telegram=?", (id,))
            membro = c.fetchone()
            if membro is None:
                c.execute(u"insert into membros(nome, estado, telegram) values (?,?,?)",
                          ("{0.first_name} {0.last_name}".format(from_user),
                           estado, id))
            else:
                c.execute(u"update membros set nome = ?, estado = ? where telegram = ?",
                          ("{0.first_name} {0.last_name}".format(from_user),
                           estado, id))
            conn.commit()


def lista_users():
    with conecta() as conn:
        with closing(conn.cursor()) as c:
            usuarios = ["Membros por Estado:"]
            for linha in c.execute(u"""select m.nome, e.nome from membros m, estados e
                    where m.estado = e.id
                    order by e.regiao_id, e.nome, m.nome"""):
                usuarios.append("{0[0]}, {0[1]}".format(linha))
            return "\n".join(usuarios)


def lista_users_por_nome():
    with conecta() as conn:
        with closing(conn.cursor()) as c:
            usuarios = ["Membros:"]
            for linha in c.execute(u"""select m.nome, e.nome from membros m, estados e
                    where m.estado = e.id
                    order by m.nome"""):
                usuarios.append("{0[0]}, {0[1]}".format(linha))
            return "\n".join(usuarios)


def conecta():
    return sqlite3.connect(__DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES)


def inicializa(nome="membros.db"):
    global __DB_NAME
    __DB_NAME = nome
    existe = os.path.exists(nome)

    if not existe:
        cria_banco()
        atualiza_estados()

