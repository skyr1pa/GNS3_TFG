from asyncore import read
from netmiko import ConnectHandler
import csv

ssh_commands = [
    'ip domain-name cisco.udc.es',
    'crypto key generate rsa modulus 2048',
    'ip ssh version 2',
    'ip ssh time-out 60',
    'ip ssh authentication-retries 3',
    'line vty 5 15',
    'transport input ssh',
    'login local',
    'username skyripa privilege 15 password s3cr3t',
    'enable secret s3cr3t',
    'service password-encryption',
    'exit'
]

with open('hosts_telnet.csv',encoding='utf-8-sig', mode='r') as hosts_telnet:   #Read specific csv
    csv_reader = csv.reader(hosts_telnet)
    iter = 0
    for row in csv_reader:
        if(iter == 0):
            HOST = {1: {'device_type':'','host':'','port':''}}  #Get csv's first line and set it as dict fields
            iter += 1
        else:
            data = [x.strip() for x in row[0].split(';')]
            HOST[iter] = {}
            HOST[iter]['device_type'] = data[0]
            HOST[iter]['host'] = data[1]
            HOST[iter]['port'] = data[2]
            iter += 1

for row, (clave, valor) in enumerate(HOST.items()):
    try:
        print(f"{valor['host']}")
        telnet_session = ConnectHandler(**valor)

        print(f"***** Connected to device {valor['host']} *****\n")
        output = telnet_session.send_command('show ip ssh')
        lines = output.splitlines()
        print("### STEP 1/1 - CONFIGURE SSH " + "###\n")

        for line in lines:
            if line.startswith('SSH Disabled'):
                #print(line)
                print("   --> Configuring SSH v2...")
                telnet_session.send_config_set(ssh_commands)
                print("    OK! SSH has been Enabled! :)")
                break
            elif line.startswith('SSH Enabled'):
                #print(line)
                print("    SKIP! SSH is already enabled on device! Finish :D")
                break

        telnet_session.disconnect()

    except Exception as e:
        print("Error al intentar configurar SSH:", e)
