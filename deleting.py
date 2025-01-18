import pymysql
import pandas as pd


conn = pymysql.connect(user='root', password='mileshka', host='localhost')
cursor = conn.cursor()

cursor.execute("DROP DATABASE IF EXISTS biography_db")
