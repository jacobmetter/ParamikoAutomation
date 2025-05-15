import paramiko
import time

ssh_client=paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

router={'hostname':'10.1.2.10','port': '22','username':'u1','password':'cisco'}
print(f'Connecting to {router['hostname']}')
ssh_client.connect(**router, look_for_keys=False, allow_agent=False) #**router unpacks the dictionary router and puts it in this command
shell=ssh_client.invoke_shell()

shell.send('enable\n')
shell.send('cisco\n')
shell.send('terminal len 0\n')
shell.send('show ip int brief\n')
time.sleep(0.5)

output=shell.recv(10000).decode()
print(output)

file_name='router 1 run config.txt'
with open(file_name,'w') as f:
    f.write(output)

if ssh_client.get_transport().is_active() == True:  # if the connection is active, then close connection
    print('Closing connection')
    ssh_client.close()