
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

"""

START = """\
Olá, eu sou o bot do grupo PyNorte.

Você pode entrar em contato com o grupo de várias formas!

""" + LINKS + """
Digite /ajuda para ver todos os comandos.

"""

LISTA_DE_ESTADOS = """\
Acre, Amapá, Amazonas, Pará, Rondônia, Roraima e Tocantins
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
