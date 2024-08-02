from napalm.ios.ios import IOSDriver
import time
class CustomIOSDriver(IOSDriver):
    """Custom NAPALM Cisco IOS Handler."""

    def config_ssh(self):
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
             print(f"SSH is already enabled on the IOS Router")
        else:
             print(f"Enabling SSH on the IOS Router...")
             self.open()
             self.cli(commands)
             print(f"SSH has been enabled succesfuly! :)")
             self.close()

    def get_users(self):
       self.open()
       command = 'sh run | i user'
       output = self._send_command(command)
       data = []
       for line in output.splitlines():
           parts = line.split()
           data.append(parts[1])

       print("Users")
       print("-----------")
       for item in data:
           print(item)

       return data
