import mysql.connector
db = mysql.connector.connect(host="localhost",user="root",password="root",database='project')
cursor=db.cursor()
cursor.execute("SELECT *FROM general")
row =cursor.fetchall()
for x in row:
    print(x)

"""

#cursor.execute("CREATE DATABASE accounting")

#cursor.execute("CREATE TABLE customer(ID INT AUTO_INCREMENT PRIMARY KEY,NAME VARCHAR(255),AGE INT)")

sql = "INSERT INTO customer(name,age) VALUES(%s,%s)"
val = [("sara",2),
       ("ali",3),
       ("sikandar",4),
       ("aima",1)]
cursor.executemany(sql,val)
db.commit()

cursor.execute("DELETE FROM CUSTOMER WHERE NAME='aima'")
db.commit()

cursor.execute("DELETE FROM CUSTOMER")
cursor.execute("SELECT *FROM CUSTOMER")
row=cursor.fetchall()
for x in row:
    print(x)


cursor.execute("DROP TABLE IF EXISTS CUSTOMER")
cursor.execute("SHOW TABLES")
for x in cursor:
  print(x)

cursor.execute("CREATE TABLE customer(ID INT AUTO_INCREMENT PRIMARY KEY,NAME VARCHAR(255),AGE INT)")
sql = "INSERT INTO customer(name,age) VALUES(%s,%s)"
val = [("sara",2),
       ("ali",3),
       ("sikandar",4),
       ("aima",1)]
cursor.executemany(sql,val)
db.commit()
cursor.execute("UPDATE CUSTOMER SET AGE=0 WHERE AGE=1")
db.commit()
cursor.execute("SELECT *FROM CUSTOMER")
row=cursor.fetchall()
for x in row:
    print(x)

cursor.execute("SELECT *FROM CUSTOMER LIMIT 2 OFFSET 2")
row=cursor.fetchall()
for x in row:
    print(x)

cursor.execute("SELECT *FROM customer")
row=cursor.fetchall()
for x in row:
    print(x)

cursor.execute("CREATE TABLE PRODUCT(ID INT AUTO_INCREMENT PRIMARY KEY,NAME VARCHAR(255),CID INT)")
sql="INSERT INTO PRODUCT(NAME,CID) VALUES(%s,%s)"
val=[("juice",1),
     ("biscuit",1),
     ("snacks",5),
     ("gluco",3)]
cursor.executemany(sql,val)
db.commit()
cursor.execute("SELECT *FROM product")
row=cursor.fetchall()
for x in row:
    print(x)
"""
#inner join
"""
cursor.execute("SELECT* \
  FROM customer \
  INNER JOIN product ON customer.id = product.cid")
row=cursor.fetchall()
for x in row:
    print(x)
"""