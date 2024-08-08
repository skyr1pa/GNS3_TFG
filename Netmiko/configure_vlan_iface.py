import argparse
from netmiko import ConnectHandler
import csv

def check_vlanID(value):
    ivalue = int(value)
    if ivalue < 1 or ivalue > 4094:
        raise argparse.ArgumentTypeError(f"VLAN ID must be an integer between 1 and 4094. You provided {value}.")
    return str(ivalue)

parser = argparse.ArgumentParser(description='Create a vlan and associate to one or various interfaces.\nConfigure the switport mode.\nConfigure SVI or Default Gateway\n')
parser.add_argument('vlanID', type=check_vlanID, help='Number of vlan (1-4094)')
parser.add_argument('vlanName', help='Name of the vlan')
args = parser.parse_args()

with open('hosts_ssh.csv',encoding='utf-8-sig', mode='r') as hosts_ssh:   #Read specific csv
    csv_reader = csv.reader(hosts_ssh)
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
        con = ConnectHandler(**valor)
        print("Established SSH conection.")

        command = 'show vlan id ' + args.vlanID
        output = con.send_command(command)
        print(output)

        if "not found" in output:
            print("--> Creating VLAN " + args.vlanID +"...\n")
            conf_set = [
                'conf t',
                'vlan ' + args.vlanName ,
                'vlan ' + args.vlanID ,
                'end'
            ]
            con.send_config_set(conf_set)
            print("VLAN " + args.vlanID + " created succesfuly! :D\n")
        else:
            print("VLAN " + args.vlanID + " is already created\n")

        print("Showing available interfaces:\n ")
        print(con.send_command("show ip interface brief | include up"))

        input_iface = ''

        while(input_iface == '' or input_iface == ' '):
           input_iface = input("Specify wanted Interface separated by ';'. Use '-' for ranges ('s' to skip):\n")
        if(input_iface != 's'):
           parsed_interfaces = input_iface.split(';')

           for iface in parsed_interfaces:
               input_mode = ''
               if '-' in iface:
                  print("--> Configuring VLAN " + args.vlanID + " on interface rangue " + iface +"\n")
               else:
                  print("--> Configuring VLAN " + args.vlanID + " on interface " + iface +"\n")
               while input_mode not in ['a', 't', 's']:
                  input_mode = input("Select the configuration mode 't' for trunk mode or 'a' for access mode. ('s' to skip\n")
               if(input_mode == 'a'):
                  if '-' in iface:
                      print("#Configuring ports in mode access\n")
                      iface_cmd = [
                         'interface range ' + iface,
                         'switchport mode access',
                         'switchport access vlan ' + args.vlanID
                      ]
                      print(con.send_config_set(iface_cmd))
                  else:
                      print("#Configuring port in mode access\n")
                      iface_cmd = [
                          'interface ' + iface,
                          'switchport mode access',
                          'switchport access vlan ' + args.vlanID
                      ]
                      print(con.send_config_set(iface_cmd))
               elif(input_mode == 't'):
                  if '-' in iface:
                      print("#Configuring ports in mode trunk\n")
                      iface_cmd = [
                         'interface range ' + iface,
                         'switchport mode trunk',
                         'switchport trunk allowed vlan ' + args.vlanID
                      ]
                      print(con.send_config_set(iface_cmd))
                  else:
                      print("#Configuring port in mode trunk\n")
                      iface_cmd = [
                          'interface ' + iface,
                          'switchport mode trunk',
                          'switchport trunk allowed vlan ' + args.vlanID
                      ]
                      print(con.send_config_set(iface_cmd))
               else:
                  continue

        print("##############CONFIGURE SVI INTERFACE############## \n")
        svi_cmd = "show interface vlan" + args.vlanID
        svi_output = con.send_command(svi_cmd)
        if "SVI" in svi_output:
           print("SVI is already configured for the VLAN " + args.vlanID +"\n")
        else:
           svi_ip = input("Especify the IP of the interface and its mask (ej. 192.168.45.1 225.255.255.0) (s to skip)")
           if(svi_ip != 's'):
              ip_cmd = [
                 'interface vlan ' + args.vlanID,
                 'ip address ' + svi_ip,
                 'no shutdown'
               ]
              print(con.send_config_set(ip_cmd))

        print("##############CONFIGURE DEFAULT GATEWAY##############")
        gtw_output = con.send_command("sh run | i default-gateway")
        if "gateway" in gtw_output:
           print("Default gateway is already configured\n")
        else:
           gtw_ip = input("Especify the IP of the default gateway (ej. 192.168.45.254) (s to skip)")
           if(gtw_ip != 's'):
              ip_cmd = [
                 'ip routing',
                 'ip default-gateway ' + gtw_ip,
                 'no shutdown'
                 ]
              print(con.send_config_set(ip_cmd))

    except Exception as e:
       print("Error: ",e)