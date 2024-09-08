import napalm, sys, os, csv, argparse, re, ipaddress

def check_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def check_ip_with_mask(ip_with_mask):
    pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\s(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'

    match = re.match(pattern, ip_with_mask)

    if not match:
        return False

    parts = [int(match.group(i)) for i in range(1, 9)]

    for part in parts:
        if part < 0 or part > 255:
            return False

    return True

def process_user(router_info, vid, vname):
    driver_ios = napalm.get_network_driver("ios")

    hostname=router_info['hostname']
    username=router_info['username']
    password=router_info['password']

    ios_router = driver_ios(hostname, username, password, optional_args={'cmd_verify': False} )

    print(f"******** Connecting to IOS Device ({router_info['hostname']}) via SSH ******** ")
    #ios_router.open()
    #print("Step 1: Checking IOS Router Connection Status")
    #print(ios_router.is_alive())

    ios_router.open()
    show_vlan = 'show vlan brief'
    lista = ios_router.cli([show_vlan])
    print(f"\n### STEP 1/4: CREATE VLAN {vid} {vname} " + "###")
    #list(lista.values())[0]
    if vid in lista[show_vlan]:
       print(f"    SKIP! VLAN {vid} already exists! Omiting...\n")
       exist = True
    else:
       commands= ['conf t',
                  'vlan '+ vid,
                  'name ' + vname
                 ]
       print(f"   --> Creating vlan {vname}...")
       ios_router.open()
       ios_router.cli(commands)
       print(f"    OK! VLAN {vname} created succesfully! :D\n")
       exist = False

    ios_router.open()
    ios_router.config_interfaces(vid)

    print("\n### STEP 3/4: CONFIGURE SVI INTERFACE " +"###")

    ios_router.open()
    svi_ip = ''
    iname = "Vlan" + vid
    if exist and iname in ios_router.get_interfaces_ip():
      print("    SKIP! SVI is already configured for the VLAN " + vid + ". Omiting...")
    else:
      svi_ip = ""
      while not check_ip_with_mask(svi_ip) and svi_ip != "s":
         svi_ip = input("  > Especify the IP of the interface and its mask (ej. 192.168.45.1 225.255.255.0) (s skip)\n")
      if(svi_ip != 's'):
        svi_cmd = [
          'conf t',
          'interface vlan ' + vid,
          'ip address ' + svi_ip,
          'no shutdown'
            ]
        print(f"   --> Configuring interface {vid}...")
        ios_router.open()
        ios_router.cli(svi_cmd)
        print(f"    OK! Interface {vid} configured succesfully! :D")

    print("\n### STEP 4/4: CONFIGURE DEFAULT GATEWAY " + "###")

    ios_router.open()
    config = ios_router.get_config()
    ios_router.open()
    gtw_input = ''

    if 'default-gateway' in config['running']:
      print("    SKIP! Default gateway is already configured! Bye! :D\n")
    else:
       gtw_input = ""
       while not check_ip(gtw_input) and gtw_input != "s":
         gtw_input = input("  > Especify the IP of the default gateway (ej. 192.168.45.254) (s skip)\n")
       if(gtw_input != 's'):
        gtw_cmd = [
          'conf t',
          'ip routing',
          'ip default-gateway ' + gtw_input,
           ]
        print("   --> Configuring default gateway...")
        ios_router.cli(gtw_cmd)
        print(f"    OK! Default gateway configured succesfully! Bye! :D")

def main():
   parser = argparse.ArgumentParser(description='Create a vlan and associate to one or various interfaces.\nConfigure the switport mode.\nConfigure SVI or Default Gateway\n')
   parser.add_argument('vlanID', type=check_vlanID, help='Number of vlan (1-4094)')
   parser.add_argument('vlanName', help='Name of the vlan')
   args = parser.parse_args()

   with open('routers.csv', mode='r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
           #print(row)
           process_user(row, args.vlanID, args.vlanName)

def check_vlanID(value):
    ivalue = int(value)
    if ivalue < 1 or ivalue > 4094:
        raise argparse.ArgumentTypeError(f"VLAN ID must be an integer between 1 and 4094. You provided {value}.")
    return str(ivalue)

if __name__ == "__main__":
    main()
