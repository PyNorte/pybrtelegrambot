import telebot
import os
import logging

import db
from mensagens import *


API_TOKEN = os.getenv('API_TOKEN')
DB_NAME = os.getenv('BOT_DB', "membros.db")

bot = telebot.TeleBot(API_TOKEN, threaded=True)

db.inicializa(DB_NAME)

db.lista()


def destino(mensagem):
    return mensagem.from_user.id


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


@bot.message_handler(commands=['nomes'])
def send_nomes(message):
    chat_id = destino(message)
    bot.send_message(chat_id, db.lista_users_por_nome())


@bot.message_handler(commands=['membro'])
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


_logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

bot.polling(none_stop=True)


