# ParamikoAutomation
### Overview:
This folder shows how I use the function Paramiko in Python to automate tasks in a simple GNS3 lab set up. 

### Lab set up: GNS3

GNS3 is an open-source software that allows users to download image files of various networking devices such as routers, switches, firewalls, IDS, IPS, etc and use them in a virtual enviornment using a VM as the server. For these automation tasks I will be using two main set ups: a single router directly connected to the "Internet" (which is really a loopback interface on my host device) and a three router topology connected to each other and a switch. Let's take a look at the first topology.

![image](https://github.com/user-attachments/assets/221078a7-7078-4348-89eb-c239c45e52c9)

As you can see, a very simple topology. the interface e0/1 on CiscoRouter1 is directly connected to the cloud internet. In a real enviornment, this would be the edge router directly connected to the ISP, where NAT, ACLs, firewalls would all be set up. The GNS3Loopback is a Microsoft KVM-Test loopback address that I created on my host machine

![image](https://github.com/user-attachments/assets/c6137946-bc15-43d2-8a1b-b1e0befceed7)

One thing thats important to note, make sure that your edge router, is in the same subnet as your loopback interface. I spent a lot of time troubleshooting various connectivity issues only to learn that my edge router and loopback interfaces were in different subnets and therefore could not communicate with each other.

### set up router for SSH via Putty

First thing you want to do is ensure your router is connected to the cloud, the interface is up/up, and it can ping your host's loopback interface (10.1.2.2). To do this, enter global config and use the commands:

          int e0/1
          ip add 10.1.2.10 255.255.255.0
          no shut
          end
from there verify the connection is up with show ip int brief

![image](https://github.com/user-attachments/assets/c0bf0021-4b21-4a41-99de-629c4b55bd79)

Looks, good, now use command:

          ping 10.1.2.2
to ping the loopback

![image](https://github.com/user-attachments/assets/60882599-a9b5-48f5-a537-7e27eb233076)

Everything looks good. now to enable SSH/Telnet to allow us to connect to the router remotely from our host machine, which will be essential for sending it scripted commands. Enter in global config mode the following:

          username u1 secret cisco
          enable secret cisco
          ip domain-name network-automation.com
          crypto key generate rsa (this will prompt you to enter a number of bits, use anything higher than 768, for this lab, I will be generating a key of 1028 bits)
          line vty 0 4
          transport input ssh telnet
          login local
          exit
          ip ssh version 2

![image](https://github.com/user-attachments/assets/6183a877-90eb-4adf-b0bc-b385b7912b7f)

to verify it works, use Putty and SSH or telnet into the router. Use username:u1 and password: cisco for login and enable.

![image](https://github.com/user-attachments/assets/9b1122cc-0c73-49be-afdc-da6fe1065866)

## Paramiko: Send commands via Python Script

The first thing we want to do is create a script that will connect to our router, enter commands, then print an output in the terminal. For that, the code will look something like this

      import paramiko
      import time

      ssh_client=paramiko.SSHClient()
      ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      
      router={'hostname':'10.1.2.10','port': '22','username':'u1','password':'cisco'}
      print(f'Connecting to {router['hostname']}')
      #**router unpacks the dictionary router and puts it in this command
      ssh_client.connect(**router, look_for_keys=False, allow_agent=False) 
      shell=ssh_client.invoke_shell()
      
      shell.send('enable\n')
      shell.send('cisco\n')
      shell.send('terminal len 0\n')
      shell.send('show ip interface brief\n')
      time.sleep(0.5)
      
      output=shell.recv(10000).decode()
      print(output)

Lets break down this code. The first two lines, are used to import the commands paramiko and time, which will be essential for use in all paramiko scripts. the variable "ssh_client" those two lines of code basically allow paramiko to create an SSH client and attempt to connect to the router, using the router touple. Inside the router touple we have all the information paramiko needs to connect to the router: ip address, port, username, password.

from there, the client connects and creates a shell. the shell is how we send commands to the router with the command shell.send('command'). Its important to note the \n after each command, this is because the interface doesnt recognize the end of the command to input. You have to add that. When you add \n think of it as just hitting enter. time.sleep() pauses the shell for half a second in order for it to process the commands just given, from there it gives an output in machine readable language, which needs to be decoded using the commands shell.recv(10000).decode() to a human readable format. Inside the terminal we get the expected result.

![image](https://github.com/user-attachments/assets/93d5ca8c-5779-404f-8341-d420a5e8593f)

From here we can begin doing more and more advanced things.

## Paramiko: Read commands from a file and execute

Lets say we don't want to go into the Python code at all and change anything, all we want to do is give Python a text file of commands we want it to run, then it will run them sequentially. This brings us further into automation because now if we get a new router into our network, all we have to do is run the script with the file of given commands and it will automatically be configured, saving us a ton of time.

![image](https://github.com/user-attachments/assets/d89cb04d-8bc7-4b4c-9db4-d72e267373cb)


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
          #**router unpacks the dictionary router and puts it in this command
          ssh_client.connect(**router, look_for_keys=False, allow_agent=False) 
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

This code is very similar to what we did in the last one, it's important to note at the beginning we take the file 'commands.txt', open it, and read it into a list variable called "commands". From there we use a for loop to insert each command into the shell.send command until the for loop is complete, then we print the output. If we wanted to, we could also save the outputs to a file by adding the following block of code to the end:

          from datetime import datetime
          now=datetime.now()
          year=now.year
          month=now.month
          day=now.day
          
          file_name=f'{router1["server_ip"]}_{year}-{month}-{day}.txt'
          print(file_name)
          with open(file_name,'w') as f:
              f.write(output)
By adding this code it takes the output of above and writes it to a new .txt file. This can be usful if you want to back up configurations, simply run the show run command and write the configuration to a text file. You can also name the file whatever you want, but by adding day, month, year it adds a layer of accountability so you know the last time you backed up a router.

![image](https://github.com/user-attachments/assets/6e9fa263-18b2-44bc-a5cf-e65ee2425a22)

As we can see, router configured a RIP route in network 10.0.0.0

## Paramiko: Reading commands from a file to multiple devices and saving the config to a file
Lets adjust the lab and add a few more routers. shown below is a new lab with three routers in the same subnet.

![image](https://github.com/user-attachments/assets/252bbd5f-2999-4963-bc41-c75adb0a3198)

Lets say we just deployed three offices with these as their distribution layer routers. We want to run a command, then back up their configurations and save it to a file in case we need it.

    import myparmiko

    router1 = {'server_ip':'10.1.2.10','server_port': '22','user':'u1','password':'cisco'}
    router2 = {'server_ip':'10.1.2.20','server_port': '22','user':'u1','password':'cisco'}
    router3 = {'server_ip':'10.1.2.30','server_port': '22','user':'u1','password':'cisco'}

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

Here we created three routers and added them to a list called "routers" from there we simply did what we have been doing, but iterating over each one, then saving a file with their router name, and the date.

![image](https://github.com/user-attachments/assets/861e86a2-06ff-44ad-85b5-d2c56c13d647)

As we can see, the program iterated over each router, ran the "show run" command and saved it to a file with its name and the date. However, its important to note, this method of doing things sequentially is vey slow. If we had 50 or even 100 routers that we were backing up daily, it would take up a lot of time. Thankfully there is a way to speed it up with a method called threading.

### Paramiko: Threading

Threading is when the python script runs each script for a router concurrently, rather than sequentially. This dramatically speeds up configuration time, but at a cost of processing power. The code will look very similar, but with the threading commands at the bottom.

    import myparmiko
    import threading

    def backup(router):
        client = myparmiko.connect(**router)
        shell = myparmiko.get_shell(client)

        myparmiko.send_command(shell, 'terminal len 0')
        myparmiko.send_command(shell, 'en')
        myparmiko.send_command(shell, 'cisco')
        myparmiko.send_command(shell, 'show run')

        # the code below is how you parse output to get only what you want
        output = myparmiko.show(shell)
        output_list = output.splitlines()
        output_list = output_list[11:-1]
        output = '\n'.join(output_list)

        from datetime import datetime
        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day

        file_name = f'{router["server_ip"]}_{year}-{month}-{day}.txt'
        print(file_name)
        with open(file_name, 'w') as f:
            f.write(output)

        myparmiko.close(client)  # close the client

    router1 = {'server_ip':'10.1.2.10','server_port': '22','user':'u1','passwd':'cisco'}
    router2 = {'server_ip':'10.1.2.20','server_port': '22','user':'u1','passwd':'cisco'}
    router3 = {'server_ip':'10.1.2.30','server_port': '22','user':'u1','passwd':'cisco'}

    routers=[router1,router2,router3]
    threads=list()
    for router in routers:
        th=threading.Thread(target=backup,args=(router,))
    threads.append(th)

    for th in threads:
        th.start()

    for th in threads:
        th.join()

The code at the bottom is how you can use multithreading. Essentially how it works is it creates an empty list, then using the threading.Thread() command, you input a function (for this example the funtion is called backup(router) with the argument = router. From there it iterates over the list of routers and runs each one concurrently. and adds it to the threads list. From there the output is the threadds list.
