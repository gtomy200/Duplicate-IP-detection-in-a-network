from netmiko import ConnectHandler
from textfsm import *
import threading
import sqlite3
import re

def control(count, records):
    while count <= records:
        if router_info[count][1] == 'cisco':
            device_name = 'cisco_ios'
        elif router_info[count][1] == 'juniper':
            device_name ='juniper'
        else:
            count += 1
            continue
        device = {'device_type' : device_name, 'ip' : router_info[count][0], 'username':u_name, 'password':pwd}
        try:
            net_connect = ConnectHandler(**device)
        except:
            print ('Connection refused to ' + router_info[count][0])
            count += 1
            continue
        if device_name == 'cisco_ios':
            try:
                cmd_output = net_connect.send_command("show ip int br")
                output= file_operation_cisco(cmd_output)
                create_db(output, router_info[count][0])
            except:
                print ('Search Pattern error ' + router_info[count][0])
                count += 1
                continue
        else:
            try:
                cmd_output = net_connect.send_command("show interfaces terse")
                output= file_operation_juniper(cmd_output)
                create_db(output, router_info[count][0])
            except:
                print ('Search Pattern error ' + router_info[count][0])
                count += 1
                continue
        count += 1
    
def router_list():
    fo = open("routers.txt",'r')
    temp_list = []
    str = fo.readline()
    while str:
        temp_list += re.findall("(\S+)\s+(\S+)\s+(\S+)\s+(\S+)",str)
        str = fo.readline()
    fo.close()
    length = len(temp_list)
    return (temp_list, length)

def create_db(output, r_name):
    conn = sqlite3.connect('routing_table.db')
    cur = conn.cursor()
    length = len(output)
    index = 0
    while length > index:
        cur.execute("INSERT INTO rtable (Device, IntorBund, IPaddress) VALUES (?, ?, ?)", (r_name, output[index][0],output[index][1]))
        index += 1
        conn.commit()
    conn.close()
    
def file_operation_cisco(data_parsing):
    re_table = TextFSM(open('cisco_ip','r'))    
    data = re_table.ParseText(data_parsing)
    temp_element = []
            
    for row in data:
        temp_element.append(row)            
    return (temp_element)  

def file_operation_juniper(data_parsing):
    re_table = TextFSM(open('juniper_ip','r'))    
    data = re_table.ParseText(data_parsing)
    temp_element = []
            
    for row in data:
        temp_element.append(row)
    return(temp_element) 

conn = sqlite3.connect('routing_table.db')
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS rtable (Device, IntorBund, IPaddress)")
cur.execute("DELETE FROM rtable")
conn.close()

router_info, records = router_list()
u_name = input('Enter the user name: ')
while u_name == '': 
    print ('Enter a valid username')
    u_name = input("Enter the username: " )
pwd = input("Enter the password: " )
while pwd == '':
    print ('Enter a valid password')
    pwd = input("Enter the password: " )
threadcount = int(round(records**(0.5),0))
no_of_elements = int(round(records/threadcount))
thread_call = 0
start_index = 0
end_index = no_of_elements - 1
obj=[None]*threadcount
while thread_call < threadcount:
    obj[thread_call] = threading.Thread(target = control, args = (start_index, end_index,), daemon=True)
    thread_call += 1
    start_index = end_index + 1
    if thread_call + 1 == threadcount:
        end_index = records-1
    else:
        end_index = start_index + no_of_elements - 1
thread_call = 0
while thread_call < threadcount:
    obj[thread_call].start()
    thread_call += 1
