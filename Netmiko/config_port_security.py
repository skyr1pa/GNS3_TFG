import argparse
from netmiko import ConnectHandler
import csv
parser = argparse.ArgumentParser(description='Configure port security')

parser.add_argument('interface', help='Interface to configure port security')
# parser.add_argument('password', help='Password of the nre user')

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
        net_connect = ConnectHandler(**valor)
        print(f"***** Connected to device {valor['host']} *****\n")

        commands = ['interface ' + args.interface ,
           'switchport port-security',
           'switchport port-security maximum 1',
           'switchport port-security violation shutdown',
           'switchport port-security mac-address sticky'
                   ]
        ou = net_connect.send_config_set(['do show port-security interface ' + args.interface])
        check = net_connect.send_config_set(['do  show running-config interface  ' + args.interface])
        print(f"### STEP 1/3 - CONFIGURE PORT SECURITY " + "###\n")
        if 'Enabled' in ou.splitlines()[3]: #Line contains  "Port Security              : Enabled/Disabled"
           print(f"    SKIP! Port security is already enabled on interface {args.interface}!")
        elif 'access' in check and 'trunk' not in check:
           print("   --> Configuring port security...")
           print(net_connect.send_config_set(commands))
           print(f"    OK! Port security has been enabled on interface {args.interface}! :)")
        else:
           print("Cannot configure port security on interface " +  args.interface)

    except Exception as e:
       print("Error trying to configure port security':", e)
