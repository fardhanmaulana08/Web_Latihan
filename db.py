import pymysql
from pymysql.cursors import DictCursor

def get_db():
    return pymysql.connect(
        host="localhost",
        user="root",          # sesuaikan dengan XAMPP Anda
        password="",          # sesuaikan jika pakai password
        database="pelaporan_security",
        cursorclass=DictCursor  # supaya hasil cursor berupa dict
    )
