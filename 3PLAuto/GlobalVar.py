import sqlite3

conn = sqlite3.connect('/Users/mac/Documents/GitHub/Jason-3PL/3PLAuto/3PL.db')
cur = conn.cursor()

TestEnv = 'dev'
MMSAccount = 'cindy.yeh@shoalter.com'
MMSPasword = 'Aa123456'
