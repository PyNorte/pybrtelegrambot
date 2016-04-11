import telebot
import os
import logging
import pytz


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


def destino(mensagem):
    #if mensagem.from_user:
    #    return mensagem.from_user.id
    return mensagem.chat.id


@bot.message_handler(content_types=['new_chat_participant'])
def send_novo(message):
    send_welcome(message)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = destino(message)
    bot.send_message(chat_id, START)


@bot.message_handler(commands=['help', 'ajuda'])
def send_help(message):
    chat_id = destino(message)
    bot.send_message(chat_id, AJUDA)


@bot.message_handler(commands=['link', 'links'])
def send_link(message):
    chat_id = destino(message)
    bot.send_message(chat_id, LINKS)


@bot.message_handler(commands=['estados'])
def send_estados(message):
    chat_id = destino(message)
    bot.send_message(chat_id, LISTA_DE_ESTADOS)


@bot.message_handler(commands=['whoami'])
def send_whoami(message):
    chat_id = destino(message)
    bot.send_message(chat_id, WHOAMI.format(message.from_user))


@bot.message_handler(commands=['lista'])
def send_lista(message):
    chat_id = destino(message)
    bot.send_message(chat_id, db.lista_users())


@bot.message_handler(commands=['nomes', 'membros'])
def send_nomes(message):
    chat_id = destino(message)
    bot.send_message(chat_id, db.lista_users_por_nome())


@bot.message_handler(commands=['estatistica', 'contador', 'total', 'stat', 'stats'])
def send_stats(message):
    chat_id = destino(message)
    stats = db.get_stats()
    mensagem = STAT_CAB
    for estado in stats[0]:
        mensagem += STAT_ESTADO.format(estado)
    mensagem += STAT_ROD.format(stats[1])
    bot.send_message(chat_id, mensagem)


@bot.message_handler(commands=['eventos'])
def send_eventos(message):
    chat_id = destino(message)
    eventos = db.get_eventos()
    mensagem = EVENTOS_CAB
    for evento in eventos:
        base = pytz.utc.localize(evento[1])
        m = manaus.normalize(base)
        b = belem.normalize(base)
        r = rio_branco.normalize(base)
        mensagem += EVENTOS_DESC.format(evento, r, m, b)
    mensagem += EVENTOS_ROD
    bot.send_message(chat_id, mensagem)


@bot.message_handler(commands=['membro', 'mecadastra', 'novo'])
def send_membro(message):
    chat_id = destino(message)
    params = message.text.split()
    if len(params) < 2:
        bot.send_message(chat_id, MEMBRO_AJUDA)
        return
    estado = params[1].lower().strip()

    db_estado = db.get_estado(estado)
    if db_estado:
        db.update_user(message.from_user, db_estado)
        bot.send_message(chat_id, MEMBRO_RESULTADO.format(message.from_user, estado.title()))
    else:
        bot.send_message(chat_id, MEMBRO_ESTADO.format(message.chat, estado))

    if not message.from_user.last_name:
        bot.send_message(chat_id, TELEGRAM_ULTIMO_NOME_AJUDA)

    if not message.from_user.username:
        bot.send_message(chat_id, TELEGRAM_NOME_USUARIO_AJUDA)



_logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

bot.polling(none_stop=True)


