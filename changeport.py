import paramiko
import time

# Configuration
switch_username = "username"
switch_password = "password"
target_switch = "192.168.206.246"
desc_string = "DOT1X"
access_vlans = [200, 300, 500]

# New Configuration Variables
new_description = "ExtUsers"
new_access_vlan = 320

# SSH Connection Function
def ssh_connect(host, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password)
    #client.invoke_shell().send("terminal length 0\n")
    #time.sleep(1)
    #client.invoke_shell().send("terminal length 0\n")
    return client.invoke_shell()
    #return client

# SSH Command Function
def ssh_command(ssh, command):
    #while not ssh.recv_ready():
    # time.sleep(0.1)
    #ssh.flush()
#    ssh.send("terminal length 0\n")
    #junk = ssh.recv(65535).decode("utf-8")
    ssh.send(command + "\n")
    #junk = stdout.readlines()
    #stdin, stdout, stderr = ssh.exec_command(command + "\n")
    time.sleep(1)
    #output = stdout.readlines()
    #output  = ' '.join(map(str, output))
    #print(output)
    output = ssh.recv(65535).decode("utf-8")
    print(output)
    #print(stdout.readlines())
    return output

# Reset Interface Function
def reset_interface(ssh, interface):
    print(f"Resetting Interface {interface} to Default Configuration...")
    command = f"default interface {interface}"
    output = ssh_command(ssh, command)
    print(output)

def conftenter(ssh):
    print(f"Entering conft")
    command = f"conf t"
    output = ssh_command(ssh, command)
    print(output)

def conftexit(ssh):
    print(f"Exiting conft")
    command = f"end"
    output = ssh_command(ssh, command)
    print(output)

# Apply New Configuration Function
def apply_new_config(ssh, interface, description, vlan):
    print(f"Applying New Configuration to Interface {interface}...")
    command = (f"interface {interface}\n"
               f"description {description}\n"
               f"switchport access vlan {vlan}\n"
               f"switchport mode access\n"
               f"no cdp enable\n"
               f"spanning-tree portfast edge\n"
               f"spanning-tree bpduguard enable\n")

    output = ssh_command(ssh, command)
    print(output)

# Save Configuration Function
def save_config(ssh):
    print("Saving Configuration...")
    command = "write memory"
    output = ssh_command(ssh, command)
    print(output)

# Main Script
if __name__ == "__main__":
    try:
        # SSH Connect to Switch
        ssh = ssh_connect(target_switch, switch_username, switch_password)
        ssh.send("terminal length 0\n")
        # Find and Update Matching Interfaces
        print("Searching for Interfaces...")
        for vlan in access_vlans:
            print(f'VLAN = {vlan}')
            time.sleep(1)
            command = f"show interfaces status | include {desc_string}"
            output = ssh_command(ssh, command)
            print(output)
            lines = output.strip().split("\n")
            #print(lines)
            #input("Press the Enter key to continue: ")

            conftenter(ssh)
            for line in lines:
                print(line)
                if 'al length 0\r' in line:
                 pass
                elif line.startswith('sw-ru-pebep-client7'):
                 pass
                elif line.startswith('show interfaces status'):
                 pass
                elif line.startswith('OOO Siemens LAN switch'):
                 pass
                elif line.startswith('_____'):
                 pass
                elif len(line)==0:
                 pass
                elif line.startswith('Gi') or line.startswith('Fa'):
                 print(f'PASSEDLINE {line}')
                 fields = line.split()
                 interface = fields[0]
                 description = fields[1]
                 if (fields[3].isnumeric):
                   if int(fields[3]) == vlan:

                 #if (description == desc_string) and (vlan in [int(vlan_info) for vlan_info in fields[3]]):
                    print('reset_interface')
                    reset_interface(ssh, interface)
                    print('apply new config', interface)
                    apply_new_config(ssh, interface, new_description, new_access_vlan)
#                    input("Press the Enter key to continue: ")
                else:
                 print(f'SKIPPING LINE     {line}')
            conftexit(ssh)
        # Save Configuration
        print('saving config')
        #save_config(ssh)

        # Close SSH Connection
        ssh.close()

    except paramiko.AuthenticationException:
        print("Failed to authenticate.")
    except paramiko.SSHException as ssh_exception:
        print(f"SSH Error: {ssh_exception}")
    except paramiko.ssh_exception.NoValidConnectionsError:
        print("Unable to connect to the SSH server.")
    except Exception as e:
        print(f"An error occurred: {e}")

