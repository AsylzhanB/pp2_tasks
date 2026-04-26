from connect import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute("SELECT 'Python connected!'")
print(cur.fetchone())

conn.close()