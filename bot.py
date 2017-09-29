import telebot
import os
import logging
import pytz

from datetime import datetime, timedelta

import db
from mensagens import *

API_TOKEN = os.getenv('API_TOKEN')
DB_NAME = os.getenv('BOT_DB', "membros.db")

assert API_TOKEN is not None

bot = telebot.TeleBot(API_TOKEN, threaded=True)

db.inicializa(DB_NAME)

db.lista()

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


def bot_responda(mensagem, resposta):
    """Telegram nao aceita mensagens com mais de 5000 caracteres"""
    chat_id = destino(mensagem)
    for r in quebra_mensagem(resposta):
        bot.send_message(chat_id, r)


def nome(mensagem):
    """Retorna o nome do usuario (first_name) ou o username caso este nao tenha sido entrado"""
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

@bot.message_handler(content_types=['new_chat_participant'])
def send_novo(message):
    """Mensagem enviada para novos integrantes do grupo"""
    nome_u = nome(message)
    if not protecao_spam_do_grupo(message, "novo"):
        bot_responda(message, START.format(nome_u))
    else:
        bot_responda(message, START_REPETIDO.format(nome_u))



@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Mensagem de boas vindas"""
    if protecao_spam_do_grupo(message, "start"):
        return
    bot_responda(message, START.format(nome(message)))



@bot.message_handler(commands=['help', 'ajuda'])
def send_help(message):
    """Mensagem com ajuda sobre os comandos do bot"""
    if protecao_spam_do_grupo(message, "help"):
        return
    bot_responda(message, AJUDA)


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
    bot_responda(message, mensagem)


@bot.message_handler(commands=['eventos'])
def send_eventos(message):
    """Envia a lista dos eventos atuais"""
    if protecao_spam_do_grupo(message, "eventos"):
        return
    eventos = db.get_eventos()
    mensagem = EVENTOS_CAB
    for evento in eventos:
        base = pytz.utc.localize(evento[1])
        m = manaus.normalize(base)
        b = belem.normalize(base)
        r = rio_branco.normalize(base)
        mensagem += EVENTOS_DESC.format(evento, r, m, b)
    mensagem += EVENTOS_ROD
    bot_responda(message, mensagem)


@bot.message_handler(commands=['membro', 'mecadastra', 'novo'])
def send_membro(message):
    """Permite ao usuario se cadastrar e informar seu estado"""
    params = message.text.split()
    if len(params) < 2:
        bot_responda(message, MEMBRO_AJUDA)
        return
    estado = params[1].lower().strip()

    db_estado = db.get_estado(estado)
    if db_estado:
        db.update_user(message.from_user, db_estado)
        bot_responda(message, MEMBRO_RESULTADO.format(message.from_user, estado.title()))
    else:
        bot_responda(message, MEMBRO_ESTADO.format(message.chat, estado))

    if not message.from_user.last_name:
        bot_responda(message, TELEGRAM_ULTIMO_NOME_AJUDA)

    if not message.from_user.username:
        bot_responda(message, TELEGRAM_NOME_USUARIO_AJUDA)

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


# Principal
_logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

# Inicia o pooling da api
bot.polling(none_stop=True)


