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
ultimo_aviso = None
ultimo_novo = None


def em_grupo(mensagem):
    return mensagem.chat.type in ["group", "supergroup"]

def destino(mensagem):
    #if mensagem.from_user:
    #    return mensagem.from_user.id
    return mensagem.chat.id

def bot_responda(mensagem, resposta):
    chat_id = destino(mensagem)
    bot.send_message(chat_id, resposta)

def nome(mensagem):
    if hasattr(mensagem, "new_chat_member") and mensagem.new_chat_member: 
        nome = mensagem.new_chat_member.first_name
        if not nome:
            return mensagem.new_chat_member.username
    else:
        nome = mensagem.from_user.first_name
        if not nome:
            return mensagem.from_user.username
    return nome


def protecao_spam_do_grupo(mensagem):
    global ultimo_aviso
    if em_grupo(mensagem):
        if not ultimo_aviso or datetime.now() - ultimo_aviso > timedelta(minutes=15):            
            bot_responda(mensagem, BOT_PRIVADO)
            ultimo_aviso = datetime.now()
        return True
    else:
        return False    

@bot.message_handler(content_types=['new_chat_participant'])
def send_novo(message):
    nome_u = nome(message)
    if not ultimo_novo or datetime.now() - ultimo_novo > timedelta(minutes=5):        
        bot_responda(message, START.format(nome_u))
    else:
        bot_responda(message, START_REPETIDO.format(nome_u))
    ultimo_novo = datetime.now()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if protecao_spam_do_grupo(message):
        return            
    bot_responda(message, START.format(nome(message)))    
    


@bot.message_handler(commands=['help', 'ajuda'])
def send_help(message):
    if protecao_spam_do_grupo(message):
        return    
    bot_responda(message, AJUDA)


@bot.message_handler(commands=['link', 'links'])
def send_link(message):
    if protecao_spam_do_grupo(message):
        return     
    bot_responda(message, LINKS)


@bot.message_handler(commands=['estados'])
def send_estados(message):
    if protecao_spam_do_grupo(message):
        return     
    bot_responda(message, LISTA_DE_ESTADOS)


@bot.message_handler(commands=['whoami'])
def send_whoami(message): 
    if protecao_spam_do_grupo(message):
        return    
    bot_responda(message, WHOAMI.format(message.from_user))


@bot.message_handler(commands=['lista'])
def send_lista(message):    
    bot_responda(message, db.lista_users())


@bot.message_handler(commands=['nomes', 'membros'])
def send_nomes(message):
    if protecao_spam_do_grupo(message):
        return     
    bot_responda(message, db.lista_users_por_nome())


@bot.message_handler(commands=['estatistica', 'contador', 'total', 'stat', 'stats'])
def send_stats(message):
    if protecao_spam_do_grupo(message):
        return     
    stats = db.get_stats()
    mensagem = STAT_CAB
    for estado in stats[0]:
        mensagem += STAT_ESTADO.format(estado)
    mensagem += STAT_ROD.format(stats[1])
    bot_responda(message, mensagem)


@bot.message_handler(commands=['eventos'])
def send_eventos(message):
    if protecao_spam_do_grupo(message):
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
    if protecao_spam_do_grupo(message):
        return     
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
    if protecao_spam_do_grupo(message):
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


_logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

bot.polling(none_stop=True)


