# -*- coding: utf-8 -*-
import datetime
import time
import os
import configparser
from PIL import Image
import telebot

PATH_TGCONFIG = 'tgsettings.ini'

#global tgconf
#global bot_result
#global tgbot

def newdir(tpath):
    """
    Создание директории.
    @param tpath: Имя директории.
    """
    try:
        os.mkdir(tpath)
    except OSError:
        print("Директория %s уже существует" % tpath)
    else:
        print("Успешно создана директория %s " % tpath)

def write_txt(name_log, str = ""):
    """
    Записывает текст в файл с логом.
    @param name_log: Имя файла.
    @param str: Строка текста.
    """
    with open(name_log, 'at', encoding='utf-8') as file:
        if(str == ""):
            file.write("\n")
        else:
            file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ") + str + "\n")

def log_write_txt(str = ""):
    """
    Запись логов в конкретный файл.
    @param str: Строка текста.
    """
    global tgconf
    if (str != ""):
        print(str)
    write_txt(tgconf['log_file_name'], str)

def read_tgconfig(filename):
    """
    Чтение конфигурации.
    @param filename: Имя файла.
    @return: (dict) - Конфигурация.
    """
    cfg = configparser.ConfigParser(allow_no_value=True)
    cfg.read(filename, encoding='utf-8')
    conf = {'log_dir': cfg.get('DEFAULT', 'log_dir'),
            'log_file_name': cfg.get('DEFAULT', 'log_file_name'),
            'tglog': cfg.getboolean('DEFAULT', 'tglog'),
            'name_group': cfg.get('DEFAULT', 'name_group'),
            'token': cfg.get('DEFAULT', 'token'),
            'count_exeption': cfg.getint('DEFAULT', 'count_exeption'),
            'sleep_exeption': cfg.getfloat('DEFAULT', 'sleep_exeption')}
    return conf

def send_tgmessage(text="", res=True, tgres=True):
    """
    Отправка сообщения: на экран, в лог, в Telegram.
    @param text: Строка текста.
    @param res: Накопление текста во временной переменной для последующей его отправки. По умолчанию res=True накопления
        не происходит и текст сразу отправляется в лог.
    @param tgres: Накопление текста во временной переменной для Telegram.
    @return: (bool) - Произошла успешная отправка сообщения?
    """
    global tgconf
    global bot_result
    global tgbot

    if res:
        log_write_txt(text.replace("\n", "  "))

    if tgres:
        if bot_result != "":
            text = bot_result + "\n" + text
        if not res:
            log_write_txt(text.replace("\n", "  "))

        bot_result = ""
        if tgbot is not None:
            for _ in range(tgconf['count_exeption']):
                try:
                    tgbot.send_message(tgconf['name_group'], text)
                except OSError:
                    time.sleep(tgconf['sleep_exeption'])
                    continue
                else:
                    return True
            log_write_txt("Error send_tgmessage")
            return False

    else:
        if bot_result != "":
            bot_result = bot_result + "\n" + text
        else:
            bot_result = text[:]
    return True

def send_tgphoto(file_name):
    """
    Отправка фото.
    @param file_name: Имя файла для отправки.
    @return: (bool) - Произошла успешная отправка сообщения?
    """
    global tgconf
    global tgbot

    log_write_txt("Photo: " + file_name)

    if tgbot is not None:
        for _ in range(tgconf['count_exeption']):
            try:
                tgbot.send_photo(tgconf['name_group'], open(file_name, 'rb'))
            except OSError:
                time.sleep(tgconf['sleep_exeption'])
                continue
            else:
                return True
        log_write_txt("Error send_tgphoto")
        return False
    return True


# Telegram
tgconf = read_tgconfig(PATH_TGCONFIG)
bot_result = ""
tgbot = telebot.TeleBot(tgconf['token']) if tgconf['tglog'] else None


if __name__ == "__main__":
    newdir(tgconf['log_dir'])
    send_tgmessage("Первое сообщение", tgres=False, res=True)
    send_tgmessage("Второе сообщение", tgres=True, res=True)
    send_tgphoto('.\{:}\metrics_class.png'.format(tgconf['log_dir']))
