FROM python:3.4

RUN apt-get update
RUN apt-get install -y git
RUN useradd bot -m
WORKDIR /bot
RUN git clone https://github.com/PyNorte/pybrtelegrambot.git
RUN pip install -r requirements.txt
WORKDIR /bot/pyTelegramBotAPI


