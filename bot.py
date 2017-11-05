import telebot
import os
import logging
import pytz
import shlex
import subprocess
import db

from datetime import datetime, timedelta, time
from mensagens import *

API_TOKEN = os.getenv('API_TOKEN')
DB_NAME = os.getenv('BOT_DB', "membros.db")
ADMINS = [int(id) for id in os.getenv('BOT_ADMINS').split(",")] or []

assert API_TOKEN is not None

bot = telebot.TeleBot(API_TOKEN, threaded=True)

db.inicializa(DB_NAME)

db.lista()

# Fusos da Região Norte
manaus = pytz.timezone("America/Manaus")
belem = pytz.timezone("America/Belem")
rio_branco = pytz.timezone("America/Rio_Branco")
bruxelas = pytz.timezone("Europe/Brussels")
palmas = pytz.timezone("America/Araguaina")

# Hora em que o último aviso foi postado no grupo
# Usado para evitar que usuários abusem do espaço do grupo para comandos
ultima_mensagem = {}

# Tempo para desativar a protecao de spam/flood em minutos
TEMPO_ENTRE_MENSAGENS = 15

# Tamanho maximo do texto a enviaer em uma unica mensagem
TAMANHO_MAXIMO = 4000


def get_git_revision_short_hash():
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip().decode("utf-8")


def em_grupo(mensagem):
    """Retorna True se a mensagem foi passada no grupo"""
    return mensagem.chat.type in ["group", "supergroup"]


def destino(mensagem):
    """Extrai o id de destino a partir de mensagem"""
    return mensagem.chat.id


def quebra_mensagem(mensagem):
    """Quebra mensagens grandes para serem enviadas pela API.
       Como o Telegram define um maximo de caracteres,
       quebra uma mensagem em varias pequenas."""
    linhas = mensagem.splitlines()
    texto = []
    tamanho = 0
    for linha in linhas:
        if tamanho + len(linha) < TAMANHO_MAXIMO:
            texto.append(linha)
            tamanho += len(linha) + 1
        else:
            if texto:
                yield "\n".join(texto)
            while len(linha) > TAMANHO_MAXIMO:
                yield linha[:TAMANHO_MAXIMO]
                linha = linha[TAMANHO_MAXIMO:]
            texto = [linha]
            tamanho = len(linha) + 1
    if texto:
        yield "\n".join(texto)


def bot_responda(mensagem, resposta, parse_mode=None):
    """Telegram não aceita mensagens com mais de 5000 caracteres"""
    chat_id = destino(mensagem)
    for r in quebra_mensagem(resposta):
        bot.send_message(chat_id, r, parse_mode=parse_mode)


def nome(mensagem):
    """Retorna o nome do usuário (first_name) ou o username caso este nao tenha sido entrado"""
    nome = mensagem.from_user.first_name
    if not nome:
        return mensagem.from_user.username
    return nome


def protecao_spam_do_grupo(mensagem, tipo):
    """Verifica se o mesmo comando foi repedito no grupo. Usado para evitar que o chat do
       grupo seja dominado pelas respostas do bot."""
    global ultima_mensagem
    if em_grupo(mensagem):
        ultimo = ultima_mensagem.get(tipo)
        if ultimo and datetime.now() - ultimo < timedelta(minutes=TEMPO_ENTRE_MENSAGENS):
            bot_responda(mensagem, BOT_PRIVADO)
            return True
        ultima_mensagem[tipo] = datetime.now()
    return False


def markdown_escape(texto):
    texto = texto.replace("*", "\*")
    texto = texto.replace("_", "\_")
    texto = texto.replace("`", "\`")
    return texto


@bot.message_handler(content_types=['new_chat_participant'])
def send_novo(message):
    """Mensagem enviada para novos integrantes do grupo"""
    nome_u = markdown_escape(nome(message))
    if not protecao_spam_do_grupo(message, "novo"):
        bot_responda(message, START.format(nome_u), parse_mode="Markdown")
    else:
        bot_responda(message, START_REPETIDO.format(nome_u), parse_mode="Markdown")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Mensagem de boas vindas"""
    if protecao_spam_do_grupo(message, "start"):
        return
    bot_responda(message, START.format(markdown_escape(nome(message))), parse_mode="Markdown")


@bot.message_handler(commands=['help', 'ajuda'])
def send_help(message):
    """Mensagem com ajuda sobre os comandos do bot"""
    if protecao_spam_do_grupo(message, "help"):
        return
    bot_responda(message, AJUDA, parse_mode="Markdown")


@bot.message_handler(commands=['link', 'links'])
def send_link(message):
    if protecao_spam_do_grupo(message, "links"):
        return
    bot_responda(message, LINKS)


@bot.message_handler(commands=['estados'])
def send_estados(message):
    """Lista de estados"""
    if protecao_spam_do_grupo(message, "estados"):
        return
    bot_responda(message, LISTA_DE_ESTADOS)


@bot.message_handler(commands=['whoami'])
def send_whoami(message):
    """Informacors sobre o usuario atual"""
    if protecao_spam_do_grupo(message, "whoami"):
        return
    bot_responda(message, WHOAMI.format(message.from_user))


@bot.message_handler(commands=['lista'])
def send_lista(message):
    """Envia a lista de usuarios cadastrados"""
    if protecao_spam_do_grupo(message, "lista"):
        return
    bot_responda(message, db.lista_users())


@bot.message_handler(commands=['nomes', 'membros'])
def send_nomes(message):
    """Envia os nomes do cadastro"""
    if protecao_spam_do_grupo(message, "membros"):
        return
    bot_responda(message, db.lista_users_por_nome())


@bot.message_handler(commands=['estatistica', 'contador', 'total', 'stat', 'stats'])
def send_stats(message):
    """Estatisticas do cadastro por estadp"""
    if protecao_spam_do_grupo(message, "stats"):
        return
    stats = db.get_stats()
    mensagem = STAT_CAB
    for estado in stats[0]:
        mensagem += STAT_ESTADO.format(estado)
    mensagem += STAT_ROD.format(stats[1])
    bot_responda(message, mensagem, parse_mode="Markdown")


@bot.message_handler(commands=['eventos'])
def send_eventos(message):
    """Envia a lista dos eventos atuais"""
    if protecao_spam_do_grupo(message, "eventos"):
        return
    eventos = db.get_eventos()
    mensagem = EVENTOS_CAB
    if eventos:
        for evento in eventos:
            base = pytz.utc.localize(evento.data)
            m = manaus.normalize(base)
            b = belem.normalize(base)
            r = rio_branco.normalize(base)
            mensagem += EVENTOS_DESC.format(evento, r, m, b)
    else:
        mensagem += "Não há eventos futuros cadastrados."
    mensagem += EVENTOS_ROD
    bot_responda(message, mensagem, parse_mode="Markdown")


@bot.message_handler(commands=['membro', 'mecadastra', 'novo'])
def send_membro(message):
    """Permite ao usuario se cadastrar e informar seu estado"""
    params = message.text.split()
    if len(params) < 2:
        bot_responda(message, MEMBRO_AJUDA)
        return
    estado = params[1].strip()

    db_estado = db.get_estado(estado)

    if db_estado:
        db.update_user(message.from_user, db_estado.nome)
        bot_responda(message, MEMBRO_RESULTADO.format(message.from_user, db_estado.nome))
    else:
        bot_responda(message, MEMBRO_ESTADO.format(message.chat, estado))

    if not message.from_user.last_name:
        bot_responda(message, TELEGRAM_ULTIMO_NOME_AJUDA)

    if not message.from_user.username:
        bot_responda(message, TELEGRAM_NOME_USUARIO_AJUDA)


def verifica_se_admin(message):
    if message.from_user.id not in ADMINS:
        bot_responda(message, "Não é admin.")
        return False
    return True


def eventos_ajuda(message):
    bot_responda(message, AJUDA_EVENTOS_AJUDA, parse_mode="Markdown")


def traduza_hora(evento):
    base = pytz.utc.localize(evento.data)
    m = manaus.normalize(base)
    b = belem.normalize(base)
    r = rio_branco.normalize(base)
    return (m, b, r)


def envia_evento(message, evento):
    m, b, r = traduza_hora(evento)
    bot_responda(message, EVENTOS_DESC_ADMIN.format(evento, r, m, b))


def eventos_gera_lista(message):
    eventos = db.get_eventos_admin()
    if eventos:
        mensagem = []
        for evento in eventos:
            m, b, r  = traduza_hora(evento)
            mensagem.append(EVENTOS_LISTA_ADMIN.format(evento, r, m, b))
        mensagem = "\n".join(mensagem)
    else:
        mensagem = SEM_EVENTOS_FUTUROS
    bot_responda(message, mensagem)


def eventos_mostra(message, comandos):
    if len(comandos) != 3:
        bot_responda(mensage, AJUDA_EVENTO_MOSTRA)
        return
    id = int(comandos[2])
    evento = db.get_evento_admin(id)
    if not evento:
        bot_responda(mensage, "Evento com id {} não encontrado.".format(id))
        return
    envia_evento(message, evento)


def eventos_edita(message, comandos):
    if len(comandos) != 5:
        bot_responda(message, AJUDA_EVENTO_EDITA)
        return
    subcomando = db.sem_acentos(comandos[3].lower())
    if subcomando not in ["descricao", "link", "data", "hora"]:
        bot_responda(message, "Subcomando inválido: {} [descricao|link|data|hora".format(subcomando))
        return
    id = int(comandos[2])
    evento = db.get_evento_admin(id)
    if not evento:
        bot_responda(message, "Evento com id {} não encontrado.".format(id))
        return
    if subcomando in ["data", "hora"]:
        base = evento.data
        if subcomando == "data":
            data = datetime.strptime(comandos[4], "%Y-%m-%d" )
            base = datetime.combine(data.date(), base.time())
        if subcomando == "hora":
            horas, minutos = [int(x) for x in comandos[4].split(":")]
            base = datetime.combine(base.date(), time(hour=horas, minute=minutos))
            subcomando = "data"
        comandos[4] = base

    db.edita_evento(id, **{subcomando: comandos[4], "telegram": message.from_user.id})
    envia_evento(message, db.get_evento_admin(id))

def eventos_apaga(message, comandos):
    if len(comandos) != 3:
        bot_responda(mensage, AJUDA_EVENTO_APAGA)
        return
    id = int(comandos[2])
    evento = db.get_evento_admin(id)
    if not evento:
        bot_responda(mensage, "Evento com id {} não encontrado.".format(id))
        return
    envia_evento(message, evento)
    db.apaga_evento(id)


def eventos_cria(message, comandos):
    if len(comandos) != 6:
        bot_responda(message, AJUDA_EVENTO_NOVO)
        return
    dia = comandos[2]
    hora = comandos[3]
    data = datetime.strptime("{} {}".format(dia, hora), "%Y-%m-%d %H:%M" )
    descricao = comandos[4]
    link = comandos[5]

    evento = db.cria_evento(data=data, descricao=descricao, link=link, telegram=message.from_user.id)
    envia_evento(message, db.get_evento_admin(evento.id))


@bot.message_handler(commands=['evento_admin'])
def evento(message):
    """/evento_admin ajuda
       /evento_admin lista
       /evento_admin mostra id
       /evento_admin apaga id
       /evento_admin edita id [descricao|link|telegram|data|hora] valor
       /evento_admin novo YYYY-MM-DD HH:MM DESCRICAO LINK
    """
    if not verifica_se_admin(message):
        return
    comandos = shlex.split(message.text)
    try:
        if len(comandos) == 1:
            eventos_ajuda(message)
        elif comandos[1] in ["help", "ajuda"]:
            eventos_ajuda(message)
        elif comandos[1] in ["lista"]:
            eventos_gera_lista(message)
        elif comandos[1] in ["mostra", "mostre", "show"]:
            eventos_mostra(message, comandos)
        elif comandos[1] in ["edita"]:
            eventos_edita(message, comandos)
        elif comandos[1] in ["apaga"]:
            eventos_apaga(message, comandos)
        elif comandos[1] in ["cria", "novo"]:
            eventos_cria(message, comandos)
        else:
            eventos_ajuda(message)
    except Exception as e:
        bot_responda(message, "Erro: {}".format(e))


@bot.message_handler(commands=['hora', 'horas', 'agora', 'now'])
def send_hora(message):
    """Envia a hora local em varias cidades do norte"""
    if protecao_spam_do_grupo(message, "hora"):
        return
    agora = datetime.utcnow().replace(tzinfo=pytz.utc)
    horarios = {
        "manaus": manaus.normalize(agora),
        "belem": belem.normalize(agora),
        "riobranco": rio_branco.normalize(agora),
        "palmas": palmas.normalize(agora),
        "bruxelas": bruxelas.normalize(agora)
    }
    bot_responda(message, HORA.format(**horarios))

@bot.message_handler(commands=['versão', 'versao'])
def versao(message):
    if protecao_spam_do_grupo(message, "versao"):
        return
    bot_responda(message, "Versão: {}".format(VERSAO))

# Principal
_logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)
VERSAO = get_git_revision_short_hash()
# Inicia o pooling da api
bot.polling(none_stop=True)
