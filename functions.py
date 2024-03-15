import telebot
from telebot import types
from config import bot
import time

def typing(cht):
    bot.send_chat_action(cht, 'typing')
    time.sleep(1)

def start_buttons():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    search = types.KeyboardButton('🔍')
    new_post = types.KeyboardButton('➕')
    profile = types.KeyboardButton('Профіль 👤')
    friends = types.KeyboardButton('Друзі 🤝')
    markup.add(search, new_post, profile, friends)
    return markup

def friends_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    friends_list = types.KeyboardButton('Мої друзі 👥')
    search_friends = types.KeyboardButton('Додати друзів 🔍')
    home = types.KeyboardButton('Головна 🏠')
    markup.add(search_friends, friends_list, home)
    return markup

def profile_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    settings = types.KeyboardButton('Налаштування ⚙️')
    home = types.KeyboardButton('Головна 🏠')
    markup.add(home, settings)
    return markup

def accept_friend():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    agree = types.KeyboardButton('Стежити ✅')
    decline = types.KeyboardButton('Не стежити ❌')
    markup.add(agree, decline)
    return markup