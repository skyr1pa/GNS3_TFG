from napalm.ios.ios import IOSDriver
import time
class CustomIOSDriver(IOSDriver):
    """Custom NAPALM Cisco IOS Handler."""

    def config_ssh(self):
        print("\n### STEP 1/1: CONFIGURE SSH " + "###")
        commands = [
            'conf t',
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

        command = 'show ip ssh'
        self.open()
        output = self._send_command(command)

        if 'SSH Enabled' in output:
             print(f"     SKIP! SSH is already enabled on the IOS Router")
        else:
             print(f"   --> Enabling SSH on the IOS Router...")
             self.open()
             self.cli(commands)
             print(f"    OK! SSH has been enabled succesfuly! :)")
             self.close()

    def config_interfaces(self, vid):
        print("### STEP 2: CONFIGURE INTERFACES " + "###")
        input_iface = ''

        while(input_iface == '' or input_iface == ' '):
           input_iface = input("  > Specify wanted Interface separated by ';'. Use '-' for ranges (s skip):\n")
        if(input_iface != 's'):
           parsed_interfaces = input_iface.split(';')

           for iface in parsed_interfaces:
               input_mode = ''
               if '-' in iface:
                  print(" --> Configuring VLAN " + vid + " on interface range " + iface +" <--\n")
               else:
                  print(" --> Configuring VLAN " + vid + " on interface " + iface +" <--\n")
               while input_mode not in ['a', 't', 's']:
                  input_mode = input("  > Select the configuration mode 't' for trunk mode or 'a' for access mode (s skip):\n")
               if(input_mode == 'a'):
                  if '-' in iface:
                      print("   --> Configuring ports in mode access...\n")
                      iface_cmd = [
                         'conf t',
                         'interface range ' + iface,
                         'switchport mode access',
                         'switchport access vlan ' + vid
                      ]
                      self.open()
                      print(self.cli(iface_cmd))
                      print(f"    OK! Ports in range {iface} configured succesfully!")
                  else:
                      print("   --> Configuring port in mode access\n")
                      iface_cmd = [
                          'conf t',
                          'interface ' + iface,
                          'switchport mode access',
                          'switchport access vlan ' + vid
                      ]
                      self.open()
                      print(self.cli(iface_cmd))
                      print(f"    OK! Port {iface} configured succesfully!")

               elif(input_mode == 't'):
                  if '-' in iface:
                      print("   --> Configuring ports in mode trunk\n")
                      iface_cmd = [
                         'conf t',
                         'interface range ' + iface,
                         'switchport mode trunk',
                         'switchport trunk allowed vlan add ' + vid
                      ]
                      self.open()
                      print(self.cli(iface_cmd))
                      print(f"    OK! Ports in range {iface} configured succesfully!")
                  else:
                      print("   --> Configuring port in mode trunk\n")
                      iface_cmd = [
                          'conf t',
                          'interface ' + iface,
                          'switchport mode trunk',
                          'switchport trunk allowed vlan add' + vid
                      ]
                      self.open()
                      print(self.cli(iface_cmd))
                      print(f"    OK! Port {iface} configured succesfully!")

               else:
                  continue
