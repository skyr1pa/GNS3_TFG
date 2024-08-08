import napalm, sys, os, csv, argparse

def process_user(router_info, user, passw):
    driver_ios = napalm.get_network_driver("ios")
    ios_router = driver_ios(
        hostname=router_info['hostname'],
        username=router_info['username'],
        password=router_info['password'],
    )

    print(f"******** Connecting to IOS Router ({router_info['hostname']}) via Telnet ******** ")
    ios_router.open()

    print("Step 1: Checking IOS Router Connection Status")
    print(ios_router.is_alive())
    print(f"Host {router_info['hostname']} is alive")
    ios_router.open()
    lista = ios_router.get_users()

    if user in lista:
       print(f"Username {user} already exists! Aborting...")
    else:
       commands= ['conf t',
                  'username '+ user + ' password '+ passw
                 ]
       print(f"Creating user {user}...")
       print(commands)
       ios_router.open()
       ios_router.cli(commands)
       print(f"User {user} created succesfully! Bye :D")
def main():
   parser = argparse.ArgumentParser(description='Create a new user in a Cisco Router')

# un argumento posicional para el nombre de usuario
   parser.add_argument('username', type=str, help='The name of the user.')
   parser.add_argument('password', type=str, help='The password of the user')
# Analizar los argumentos
   args = parser.parse_args()

   with open('routers.csv', mode='r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
           process_user(row, args.username, args.password)
           print("\n")

if __name__ == "__main__":
    main()