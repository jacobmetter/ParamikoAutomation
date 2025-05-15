import myparmiko

router1 = {'server_ip':'10.1.2.10','server_port': '22','user':'u1','passwd':'cisco'}
router2 = {'server_ip':'10.1.2.20','server_port': '22','user':'u1','passwd':'cisco'}
router3 = {'server_ip':'10.1.2.30','server_port': '22','user':'u1','passwd':'cisco'}

routers=[router1,router2,router3]
for router in routers:
    client=myparmiko.connect(**router)
    shell=myparmiko.get_shell(client)

    myparmiko.send_command(shell,'terminal len 0')
    myparmiko.send_command(shell,'en')
    myparmiko.send_command(shell,'cisco')
    myparmiko.send_command(shell,'show run')

    #the code below is how you parse output to get only what you want
    output=myparmiko.show(shell)
    output_list=output.splitlines()
    output_list=output_list[11:-1]
    output='\n'.join(output_list)

    from datetime import datetime
    now=datetime.now()
    year=now.year
    month=now.month
    day=now.day
    hour=now.hour
    minute=now.minute

    file_name=f'{router["server_ip"]}_{year}-{month}-{day}.txt'
    print(file_name)
    with open(file_name,'w') as f:
        f.write(output)

    myparmiko.close(client) #close the client