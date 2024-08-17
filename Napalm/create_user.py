import napalm, sys, os, csv, argparse

def process_user(router_info, user, passw):
    driver_ios = napalm.get_network_driver("ios")
    ios_router = driver_ios(
        hostname=router_info['hostname'],
        username=router_info['username'],
        password=router_info['password'],
        optional_args={'cmd_verify': False, 'timeout':400}
    )

    print(f"******** Connecting to IOS Router ({router_info['hostname']}) via SSH ******** ")

    print(f"\n### STEP 1/1: CREATE USER {user}  " + "###")
    #ios_router.open()
    #print(ios_router.is_alive())
    #print(f"Host {router_info['hostname']} is alive")
    ios_router.open()
    lista = ios_router.get_users()

    if user in lista:
       print(f"    SKIP! Username {user} already exists! Finish.\n")
    else:
       commands= ['conf t',
                  'username '+ user + ' password '+ passw
                 ]
       print(f"   --> Creating user {user}...")
       ios_router.open()
       ios_router.cli(commands)
       print(f"    OK! User {user} created succesfully! Bye :D")

def main():
   parser = argparse.ArgumentParser(description='Create a new user in a Cisco device')
   parser.add_argument('username', type=str, help='The name of the user.')
   parser.add_argument('password', type=str, help='The password of the user')
   args = parser.parse_args()

   with open('routers.csv', mode='r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
           process_user(row, args.username, args.password)
           print("\n")

if __name__ == "__main__":
    main()
