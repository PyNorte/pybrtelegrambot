FROM python:3.4

RUN apt-get update
RUN apt-get install -y git
RUN useradd bot -m
RUN mkdir /bot
WORKDIR /bot
RUN git clone https://github.com/PyNorte/pybrtelegrambot.git
WORKDIR /bot/pybrtelegrambot
RUN pip install -r requirements.txt
USER bot

