import os

import pymysql
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv('HOST')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
DATABASE = os.getenv('DATABASE')

connection = pymysql.connect(
  host='monorail.proxy.rlwy.net',
  user='root',
  password='YUfxAVyNzhYDfmdRdnOzrhUfYhLpZfOf',
  database='railway',
  port=38412
)

cursor = connection.cursor()