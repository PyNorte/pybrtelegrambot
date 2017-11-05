
WHOAMI = """
User: @{0.username}
ID: {0.id}
Name: {0.first_name} {0.last_name}
"""

AJUDA = """
`/start`    Mensagem de boas-vindas
`/ajuda`   Mostra este resumo dos comandos
`/links`   Mostra os link para participar das atividades do grupo
`/estados` Lista os estados cobertos pelo grupo
`/membro`  Adiciona ou atualiza usuário no grupo do estado (`/mecadastra`)
`/lista`   Lista membros por estado
`/nomes`   Lista membros por nome (`/membros`)
`/stat`    Número de membros por estado e total
`/eventos` Próximos eventos
`/hora`    Mostra a hora em vários estados do Norte
`/evento_admin`  Administração de eventos (_somente administradores do bot_)
"""

LINKS = """\
Telegram: http://bit.ly/pynorte
Web: http://pynorte.python.org.br/
Lista de email: https://groups.google.com/d/forum/pynorte
GitHub: https://github.com/PyNorte/
Facebook: https://www.facebook.com/pynorte/
"""

START = """
Olá {0}, eu sou o bot do grupo PyNorte.

Você pode entrar em contato com o grupo de várias formas!
Eu só respondo aos comandos em privado (você deve conversar diretamente comigo).

Clique em: @PyNorteBot para conversar comigo em privado, e depois para mais instruções envie:

`/ajuda`

Não se esqueça de se cadastrar, digitando:
`/mecadastra SIGLA_DO_SEU_ESTADO`
Na mesma linha! Exemplo:
`/mecadastra am`

""" + LINKS + """

Digite `/ajuda` para ver todos os comandos.
"""

START_REPETIDO = """
Bem-vindo {0}!
"""

LISTA_DE_ESTADOS = """
Acre, Amapá, Amazonas, Pará, Rondônia, Roraima e Tocantins

Membros de outras regiões também podem participar, basta utilizar a sigla de seu estado.
Utilize EX para exterior.

"""


MEMBRO_RESULTADO = """
User: {0.username} Name: {0.first_name} {0.last_name}
Estado: {1}
"""

MEMBRO_ESTADO = """
Erro:
Estado inválido: {1}
"""

MEMBRO_AJUDA = """
*Uso*:
```/membro estado```

Você precisa escrever /membro E_A_SIGLA_DO_SEU_ESTADO na mesma linha.

Exemplo:
```/membro amazonas
/membro am
/membro para```
"""

STAT_CAB = """
*Estatísticas*:

Total por Estados:
"""
STAT_ESTADO = "{0[0]} - {0[1]}\n"

STAT_ROD = "\nTotal: {0} membros\n"

EVENTOS_CAB = """*Próximos Eventos:* """

EVENTOS_DESC = """
Evento: {0.descricao}
Link: \U0001F517 {0.link}
Data: \U0001F4c5 {0.data:%d/%m/%y}
Horários:
  Rio Branco: \U0001F55c {1:%H:%Mh}
  Manaus, Boa Vista, Porto Velho: \U0001F55c {2:%H:%Mh}
  Belém, Palmas, Macapá: \U0001F55c {3:%H:%Mh}

"""

EVENTOS_LISTA_ADMIN = """Id: {0.id} Evento: {0.descricao} """

EVENTOS_DESC_ADMIN = """
Id: {0.id} Evento: {0.descricao}
Link: \U0001F517 {0.link}
Data: \U0001F4c5 {0.data:%d/%m/%y}
Horários:
  Rio Branco: \U0001F55c {1:%H:%Mh}
  Manaus, Boa Vista, Porto Velho: \U0001F55c {2:%H:%Mh}
  Belém, Palmas, Macapá: \U0001F55c {3:%H:%Mh}

"""

EVENTOS_ROD = ""

AJUDA_EVENTOS_AJUDA = """
`/evento_admin ajuda` Exibe esta mensagem.
`/evento_admin lista` Lista todos os eventos.
`/evento_admin mostra id` Mostra o evento por id
`/evento_admin apaga id` Apaga o evento com a id
`/evento_admin edita id [descricao|link|telegram|data|hora] valor` Edita um campo por vez.
`/evento_admin novo id YYYY-MM-DD HH:MM DESCRICAO LINK` Cria um novo evento.
"""

SEM_EVENTOS_FUTUROS = "Não há eventos futuros cadastrados."

AJUDA_EVENTO_MOSTRA = "Formato: `/evento_admin mostra id-do-evento`"

AJUDA_EVENTO_EDITA = "Formato: `/evento_admin edita id [descricao|link|data|hora] valor`"

AJUDA_EVENTO_APAGA = "Formato: `/evento_admin apaga id-do-evento`"

AJUDA_EVENTO_NOVO = ("Formato: `/evento_admin novo YYYY-MM-DD HH:MM DESCRICAO LINK`\n"
                     "Utilize aspas ou apostrófes para passar valores com espaços.\n"
                     "Horário GMT!")

TELEGRAM_NOME_USUARIO_AJUDA = """

Você ainda não definiu o seu nome de usuário no Telegram.
Para defini-lo, vá na opção "Configurações" que fica no menu inicial do Telegram e modifique "Nome de usuário".

"""
TELEGRAM_ULTIMO_NOME_AJUDA = """

Você ainda não definiu o seu sobrenome no Telegram.
Para defini-lo, vá na opção "Configurações" que fica no menu inicial do Telegram, e modifique "sobrenome".

"""

HORA = """
{riobranco:%H:%M:%S (%d/%m)} Rio Branco
{manaus:%H:%M:%S (%d/%m)} Manaus e Boa Vista
{belem:%H:%M:%S (%d/%m)} Belém e Macapá
{palmas:%H:%M:%S (%d/%m)} Palmas
{bruxelas:%H:%M:%S (%d/%m)} Bruxelas (Bélgica)
"""

BOT_PRIVADO = "Converse comigo enviando mensagens em privado. "\
              "Clique em @PyNorteBot e depois para mais instruções, envie: /ajuda"

