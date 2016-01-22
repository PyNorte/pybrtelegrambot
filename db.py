import sqlite3
import os.path
from contextlib import closing

ESTADOS = {"AC": "Acre",
           "AP": "Amapá",
           "AM": "Amazonas",
           "PA": "Pará",
           "RO": "Rondônia",
           "RR": "Roraima",
           "TO": "Tocantins"}


__DB_NAME = None


def cria_banco():
    with conecta() as conn:
        with closing(conn.cursor()) as c:
            c.execute('''CREATE TABLE estados
                     (id INTEGER PRIMARY KEY, sigla text, nome text)''')
            c.execute('''CREATE TABLE membros
                     (id INTEGER PRIMARY KEY, nome text, estado integer, telegram integer)''')
            for sigla, estado in ESTADOS.iteritems():
                c.execute("""insert into estados(sigla, nome) values(?,?)""", (sigla, estado))
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
                    order by e.nome, m.nome"""):
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
    return sqlite3.connect(__DB_NAME)


def inicializa(nome="membros.db"):
    global __DB_NAME
    __DB_NAME = nome
    existe = os.path.exists(nome)

    if not existe:
        cria_banco()

