import argparse
from netmiko import ConnectHandler
import csv
# Configurar el analizador de argumentos
parser = argparse.ArgumentParser(description='Create an user in a Cisco router.')

parser.add_argument('username', help='Username to create')
parser.add_argument('password', help='Password of the nre user')

args = parser.parse_args()
with open('hosts_ssh.csv',encoding='utf-8-sig', mode='r') as host_ssh:   #Read specific csv
    csv_reader = csv.reader(host_ssh)
    iter = 0
    for row in csv_reader:
        if(iter == 0):
            HOST = {1: {'device_type':'','host':'','username':'', 'password':''}}  #Get csv's first line and set it as dict fields
            iter += 1
        else:
            data = [x.strip() for x in row[0].split(';')]
            HOST[iter] = {}
            HOST[iter]['device_type'] = data[0]
            HOST[iter]['host'] = data[1]
            HOST[iter]['username'] = data[2]
            HOST[iter]['password'] = data[3]
            iter += 1


for row, (clave, valor) in enumerate(HOST.items()):
    try:
        print(f'{valor}')
# Conect the device
        net_connect = ConnectHandler(**valor)
        commands = ['conf t',
           'username ' + args.username + ' password ' + args.password
                   ]
# Verify if the user exists
        ou = net_connect.send_command("sh run | i user")
        print(ou)
        if args.username not in ou:
           net_connect.send_config_set(commands)
           print(f"Created user {args.username} !")
        else:
           print(f"User {args.username} already exists!")
# Cierra la conexion
        net_connect.disconnect()

    except Exception as e:
       print("Error trying to create user'{args.username}':", e)
