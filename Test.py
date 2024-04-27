import sqlite3

# 连接数据库
conn = sqlite3.connect('/Users/mac/Documents/GitHub/Jason-3PL/3PLAuto/3PL.db')
cursor = conn.cursor()

# 执行查询数据库中所有表的 SQL 查询语句
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in the database:")
for table in tables:
    print(table[0])

# 关闭连接
conn.close()
