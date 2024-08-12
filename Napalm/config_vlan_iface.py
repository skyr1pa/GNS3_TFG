import napalm, sys, os, csv, argparse

def process_user(router_info, vid, vname):
    driver_ios = napalm.get_network_driver("ios")

    hostname=router_info['hostname']
    username=router_info['username']
    password=strrouter_info['password']

    ios_router = driver_ios(hostname, username, password, optional_args={'cmd_verify': False} )

    print(f"******** Connecting to IOS Router ({router_info['hostname']}) via Telnet ******** ")
    ios_router.open()
    print("Step 1: Checking IOS Router Connection Status")
    print(ios_router.is_alive())
    print(f"Host {router_info['hostname']} is alive")
    ios_router.open()
    show_vlan = 'show vlan brief'
    lista = ios_router.cli([show_vlan])
    #list(lista.values())[0]
    if vid in lista[show_vlan]:
       print(f"VLAN {vid} already exists!")
       check = True
    else:
       commands= ['conf t',
                  'vlan '+ vid,
                  'name ' + vname
                 ]
       print(f"Creating vlan {vname}...")
       print(commands)
       ios_router.open()
       ios_router.cli(commands)
       print(f"VLAN {vname} created succesfully! Bye :D")


    ios_router.open()
    ios_router.config_interfaces(vid)

    print("\n##############CONFIGURE SVI INTERFACE############## \n")

    ios_router.open()
    svi_ip = ''

    if check and vname in ios_router.get_interfaces_ip():
      print("SVI is already configured for the VLAN " + vid)
    else:
      while(svi_ip == '' or svi_ip == ' '):
         svi_ip = input("Especify the IP of the interface and its mask (ej. 192.168.45.1 225.255.255.0) (s to skip)\n")
      if(svi_ip != 's'):
        svi_cmd = [
          'conf t',
          'interface vlan ' + vid,
          'ip address ' + svi_ip,
          'no shutdown'
            ]
        ios_router.open()
        print(ios_router.cli(svi_cmd))

    print("\n##############CONFIGURE DEFAULT GATEWAY##############\n")

    ios_router.open()
    config = ios_router.get_config()
    ios_router.open()
    gtw_input = ''

    if 'default-gateway' in config['running']:
      print("Default gateway is already configured\n")
    else:
      while(gtw_input == '' or gtw_input == ' '):
         gtw_input = input("Especify the IP of the default gateway (ej. 192.168.45.254) (s to skip)\n")
      if(gtw_input != 's'):
        gtw_cmd = [
          'ip routing',
          'ip default-gateway ' + gtw_input,
           ]
        print(ios_router.cli(gtw_cmd))

def main():
   parser = argparse.ArgumentParser(description='Create a vlan and associate to one or various interfaces.\nConfigure the switport mode.\nConfigure SVI or Default Gateway\n')
   parser.add_argument('vlanID', type=check_vlanID, help='Number of vlan (1-4094)')
   parser.add_argument('vlanName', help='Name of the vlan')
   args = parser.parse_args()

   with open('routers.csv', mode='r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
           print(row)
           process_user(row, args.vlanID, args.vlanName)

def check_vlanID(value):
    ivalue = int(value)
    if ivalue < 1 or ivalue > 4094:
        raise argparse.ArgumentTypeError(f"VLAN ID must be an integer between 1 and 4094. You provided {value}.")
    return str(ivalue)

if __name__ == "__main__":
    main()
