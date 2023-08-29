import mysql.connector
from dotenv import load_dotenv
import os
load_dotenv()
dataBase = mysql.connector.connect(
    host = os.getenv("DB_HOST"),
    user = os.getenv("DB_USER"),
    passwd = os.getenv("DB_PASSWD"),
)

#cursorObject = dataBase.cursor()

#cursorObject.execute("CREATE DATABASE korkidb")

print("ALL DONE")