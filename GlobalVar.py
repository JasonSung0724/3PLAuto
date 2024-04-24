import sqlite3

conn = sqlite3.connect(r'.\3PL.db')
cur = conn.cursor()
TestEnv = 'staging'
MMSAccount = 'cindy.yeh@shoalter.com'
MMSPasword = 'Aa123456'

NewRegisterToteList = []