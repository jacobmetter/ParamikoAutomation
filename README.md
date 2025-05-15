# ParamikoAutomation
### Synopsis:
This folder shows how I use the function Paramiko in Python to automate tasks in a simple GNS3 lab set up. Lets begin with the lab set up

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
