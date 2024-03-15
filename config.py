import telebot
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('TOKEN')

bot = telebot.TeleBot('7115902347:AAHySCZD3POPYg5kYJwMB58bSHp1sVPfL0g')