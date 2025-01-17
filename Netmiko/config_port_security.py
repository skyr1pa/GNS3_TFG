import argparse
from netmiko import ConnectHandler
import csv
parser = argparse.ArgumentParser(description='Configure port security, arp inspection and port security')

parser.add_argument('interface', help='Interface to configure port security')
parser.add_argument('vlan', help='Vlans for configurating dhcp snooping and arp inspection')

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
        port_sec_enabled = net_connect.send_config_set(['do show port-security interface ' + args.interface])
        port_sec_check = net_connect.send_config_set(['do  show running-config interface  ' + args.interface])

        print(f"\n### STEP 1/3 - CONFIGURE PORT SECURITY " + "###")
        if 'Enabled' in port_sec_enabled.splitlines()[3]:
           print(f"    SKIP! Port security is already enabled on interface {args.interface}!")
        elif 'access' in port_sec_check and 'trunk' not in port_sec_check:
           print("   --> Configuring port security...")
           net_connect.send_config_set(commands)
           print(f"    OK! Port security has been enabled on interface {args.interface}! :)")
        else:
           print("Cannot configure port security on interface " +  args.interface)

        print(f"\n### STEP 2/3 - CONFIGURE DHCP SNOOPING " + "###")
        trust = ""
        dhcp_check = net_connect.send_config_set(['do sh run | i ip dhcp snooping vlan '])
        if args.vlan in dhcp_check:
           print(f"    SKIP! DHCP snooping is already enabled on vlan {args.vlan}!")
        else:
           while(trust not in ['y','n']):
             trust = input("  > Do you want to configure port " + args.interface + " as a trusted port (y/n): ")
           print("   --> Configuring DHCP snooping...")
           net_connect.send_config_set(['ip dhcp snooping', 'ip dhcp snooping vlan ' + args.vlan])
           if(trust == 'y'):
             net_connect.send_config_set(['interface ' +  args.interface, 'ip dhcp snooping trust'])
           print(f"    OK! DHCP snooping has been enabled! :)")


        print(f"\n### STEP 3/3 - CONFIGURE ARP INSPECTION " + "###")
        arp_check = net_connect.send_config_set(['do sh run | i ip arp inspection vlan'])
        if args.vlan in arp_check:
           print(f"    SKIP! ARP inspection is already enabled on vlan {args.vlan}!")
        else:
          print("   --> Configuring ARP inspection...")
          net_connect.send_config_set(['ip arp inspection vlan ' + args.vlan, 'ip arp inspection validate src-mac dst-mac ip'])
          if(trust == 'y'):
             net_connect.send_config_set(['interface ' +  args.interface, 'ip arp inspection trust'])
          print(f"    OK! ARP INSPECETION has been enabled! :)")

    except Exception as e:
       print("Error trying to configure port security':", e)
