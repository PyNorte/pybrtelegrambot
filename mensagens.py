
WHOAMI = """
User: {0.username}
ID: {0.id}
Name: {0.first_name} {0.last_name}
"""

AJUDA = """
/start   Mensagem de boas-vindas
/ajuda   Mostra este resumo dos comandos
/links   Mostra os link para participar das atividades do grupo
/estados Lista os estados cobertos pelo grupo
/membro  Adiciona usuário no grupo do estado (/mecadastra)
/lista   Lista membros por estado
/nomes   Lista membros por nome (/membros)
/stat    Número de membros por estado e total
/eventos Próximos eventos
"""

LINKS = """\
Telegram:
https://telegram.me/joinchat/COYq6QM8RkebVUVK1WxRHQ

Web:
http://pynorte.python.org.br/

Lista de email:
https://groups.google.com/d/forum/pynorte

GitHub:
https://github.com/PyNorte/

Facebook:
https://www.facebook.com/pynorte/

"""

START = """\
Olá, eu sou o bot do grupo PyNorte.

Você pode entrar em contato com o grupo de várias formas!

""" + LINKS + """
Digite /ajuda para ver todos os comandos.

"""

LISTA_DE_ESTADOS = """\
Acre, Amapá, Amazonas, Pará, Rondônia, Roraima e Tocantins

Membros de outras regiões também podem participar, basta utilizar a sigla de seu estado.
Utilize EX para exterior.

"""


MEMBRO_RESULTADO = """\
User: {0.username} Name: {0.first_name} {0.last_name}
Estado: {1}
"""

MEMBRO_ESTADO = """\
Erro:
Estado inválido: {1}
"""

MEMBRO_AJUDA = """
Uso:
/membro estado

Exemplo:
/membro amazonas
"""

STAT_CAB = """
Estatísticas:

Total por Estados:
"""
STAT_ESTADO = "{0[0]} - {0[1]}\n"

STAT_ROD = "\nTotal: {0} membros\n"

EVENTOS_CAB = """
Próximos Eventos:
"""

EVENTOS_DESC = """
Evento: {0[2]}
Link: {0[3]}
Data: {0[1]:%d/%m/%y}
Horários:
  Rio Branco: {1:%H:%Mh}
  Manaus, Boa Vista, Porto Velho: {2:%H:%Mh}
  Belém, Palmas, Macapá: {3:%H:%Mh}

"""

EVENTOS_ROD = ""
