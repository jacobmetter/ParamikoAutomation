import myparmiko

router1 = {'server_ip':'10.1.2.20','server_port': '22','user':'u1','password':'cisco'}
client=myparmiko.connect(**router1)
shell=myparmiko.get_shell(client)

myparmiko.send_command(shell,'terminal len 0')
myparmiko.send_command(shell,'en')
myparmiko.send_command(shell,'cisco')
myparmiko.send_command(shell,'show run')

output=myparmiko.show(shell)

output_list=output.splitlines()
output_list=output_list[11:-1]
output='\n'.join(output_list)


from datetime import datetime
now=datetime.now()
year=now.year
month=now.month
day=now.day

file_name=f'{router1["server_ip"]}_{year}-{month}-{day}.txt'
print(file_name)
with open(file_name,'w') as f:
    f.write(output)

myparmiko.close(client) #close the client