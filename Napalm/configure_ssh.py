import napalm
import sys
import os
import csv

def process_router(router_info):
    driver_ios = napalm.get_network_driver("ios")
    ios_router = driver_ios(
        hostname=router_info['hostname'],
        username=router_info['username'],
        password=router_info['password'],
        optional_args={'port': 23, 'transport': 'telnet', 'timeout': 400, 'dest_file_system': 'flash:', 'cmd_verify': False, 'read_timeout': 60}
    )

    print(f"******** Connecting to IOS Router ({router_info['hostname']}) via Telnet ******** ")
    ios_router.open()

   # print("Step 1: Checking IOS Router Connection Status")
   # if True in ios_router.is_alive():
   #    print(f"Host {router_info['hostname']} is alive")

    ios_router.config_ssh()

def main():
    with open('routers.csv', mode='r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            process_router(row)
            print("\n")
if __name__ == "__main__":
    main()
