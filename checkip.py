import sqlite3 
    
conn = sqlite3.connect('routing_table.db')
cur = conn.cursor()

ip = input('enter the ip address: ')

chck_integer = all (element in '0123456789.' for element in ip)
if chck_integer:
    cur.execute("Select * from rtable where IPaddress = (?)", (ip, ))
    output = cur.fetchall()
    conn.close()
    if len(output) == 0:
        print ('IP address not found')
    else:
        print ('duplicate IP address found in the router ' + str(output[0][0]) +' for the interface '+ str(output[0][1]))
else:
    print ('Invalid ip address')
    conn.close()
