import napalm, sys, os, csv, argparse

def process_user(router_info, interface, vlan):
    driver_ios = napalm.get_network_driver("ios")
    ios_router = driver_ios(
        hostname=router_info['hostname'],
        username=router_info['username'],
        password=router_info['password'],
        optional_args={'cmd_verify': False, 'timeout':400}
    )

    print(f"******** Connecting to IOS Router ({router_info['hostname']}) via SSH ******** ")
    #ios_router.open()
    #print(ios_router.is_alive())
    #print(f"Host {router_info['hostname']} is alive")

    print(f"### STEP 1/3 - CONFIGURE PORT SECURITY " + "###\n")

    commands = ['conf t',
           'interface ' + interface ,
           'switchport port-security',
           'switchport port-security maximum 1',
           'switchport port-security violation shutdown',
           'switchport port-security mac-address sticky'
                   ]

    ios_router.open()
    ou = ios_router.cli(['show port-security interface ' + interface])

    ios_router.open()
    port_sec_check = ios_router.cli(['show running-config interface  ' + interface])

    if 'Enabled' in ou:
        print(f"    SKIP! Port security is already enabled on interface {interface}!")
    elif 'access' in port_sec_check and 'trunk' not in port_sec_check:
        print("   --> Configuring port security...")
        ios_router.open()
        ios_router.cli(commands)
        print(f"    OK! Port security has been enabled on interface {interface}! :)")
    else:
        print("Cannot configure port security on interface " + interface)

    print(f"### STEP 2/3 - CONFIGURE DHCP SNOOPING " + "###\n")
    trust = ""
    ios_router.open()
    run_config = ios_router.get_config()['running']
    check_vlan = 'ip dhcp snooping vlan ' + vlan
    if check_vlan in run_config:
        print(f"    SKIP! DHCP snooping is already enabled on vlan {vlan}!")
    else:
        while(trust not in ['y','n']):
            trust = input("  > Do you want to configure port " + interface + " as a trusted port (y/n): ")
        print("   --> Configuring DHCP snooping...")
        ios_router.open()
        ios_router.cli(['conf t', 'ip dhcp snooping', 'ip dhcp snooping vlan ' + vlan])
        if(trust == 'y'):
            ios_router.open()
            ios_router.cli(['interface ' +  interface, 'ip dhcp snooping trust'])
        print(f"    OK! DHCP snooping has been enabled! :)")

    print(f"### STEP 3/3 - CONFIGURE ARP INSPECTION " + "###\n")
    check_vlan_arp = 'ip arp inspection vlan ' + vlan
    if check_vlan_arp in run_config:
        print(f"    SKIP! ARP inspection is already enabled on vlan {vlan}!")
    else:
        print("   --> Configuring ARP inspection...")
        ios_router.open()
        ios_router.cli(['conf t', 'ip arp inspection vlan ' + vlan, 'ip arp inspection validate src-mac dst-mac ip'])
        if(trust == 'y'):
            ios_router.open()
            ios_router.cli(['interface ' + interface, 'ip arp inspection trust'])
        print(f"    OK! ARP inspection has been enabled! :)")

def main():
   parser = argparse.ArgumentParser(description='Configure port security, dhcp snooping y arp inspection')
   parser.add_argument('interface', help='Interface to configure port security')
   parser.add_argument('vlan', help='Vlans for configurating dhcp snooping and arp inspection')
   args = parser.parse_args()

   with open('routers.csv', mode='r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
           process_user(row, args.interface, args.vlan)
           print("\n")

if __name__ == "__main__":
    main()
