import paramiko
import time

#step 1: pull commands from a txt file and place them in a list
with open('commands.txt') as f:
    commands=f.read().splitlines()

#Open SSH and connect to router
ssh_client=paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

router={'hostname':'10.1.2.10','port': '22','username':'u1','password':'cisco'}
print(f'Connecting to {router['hostname']}')
ssh_client.connect(**router, look_for_keys=False, allow_agent=False) #**router unpacks the dictionary router and puts it in this command
shell=ssh_client.invoke_shell()

#iterate over the commands list and execute each command sequentially
for cmd in commands:

    print(f'Executing Command: {cmd}')
    shell.send(f'{cmd} \n')
    time.sleep(0.5)

output=shell.recv(10000).decode()
print(output)

#close the connection
if ssh_client.get_transport().is_active() == True:  # if the connection is active, then close connection
    print('Closing connection')
    ssh_client.close()