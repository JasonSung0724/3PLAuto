import sqlite3

conn = sqlite3.connect('/Users/jason/3PLAuto/3PL.db')
cur = conn.cursor()

TestEnv = 'dev'
MMSAccount = 'cindy.yeh@shoalter.com'
MMSPasword = 'Aa123456'
