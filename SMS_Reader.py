#!/usr/bin/python
from email.message import Message
from time import sleep
import time, sys
import RPi.GPIO as GPIO
import datetime
import serial
import datetime
import paho.mqtt.client as mqtt 

SIM_POWK = 23 #Sim Power Key
SIM_STA = 24  # Sim On/Off status (if HIGH it's On and vice versa)

usrName = "admin"
usrPass = "inha2016"
broker = "oxus2.amudar.io"

MessageSim = ""

GPIO.setmode(GPIO.BCM)
GPIO.setup(SIM_POWK, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(SIM_STA, GPIO.IN)

ser = serial.Serial("/dev/ttyS0", baudrate = 9600, timeout = 1)
print()
print(ser.name)
sleep(0.1)
ser.flush()


# FUNCTIONS

#
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True #set flag
        print("Connected OK")

    else:
        print("Bad connection\nReturned code=", rc) 
        client.bad_connection_flag = True   

#end of on_connect


def on_disconnect(client, userdata, rc):
    print("client disconnected OK")
    client.connected_flag = False
    client.disconnect_flag = True

#end of on_disconnect                    

def on_publish(client, userdata, result):       #create function for callback
    print("data published\n")

#end of on_publish()

# Called when error detected
def Error_detected(err):
    print("Error detected")
    print(err)
    d = datetime.datetime.now()
    date = d.strftime("%Y-%m-%d %H:%M:%S")
    print("Date:", date)
    file = open("/home/pi/Documents/SMS_Reading_and_Uploading/errors.txt", "a")
    file.write("\n\n")
    file.write(date)
    file.write(err)
    file.write("\n\n")
    file.close()
    
#end of Error_detected() 


# Turn on Modem
def Modem_on():
    print("\nStarting Up Modem...")
    GPIO.output(SIM_POWK, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(SIM_POWK, GPIO.LOW)
    time.sleep(2)

#end of Modem_on()


# Turn off Modem
def Modem_off():
    print("\nModem is shutting down...")
    GPIO.output(SIM_POWK, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(SIM_POWK, GPIO.LOW)
    time.sleep(2)

#end of Modem_off()


# Sends AT Commands
def SendAT(ATCOM, SuccessMsg, SubStr1="", SubStr2="", indent1=0, indent2=0, sleepAfterCom=0.2): 
    #ATCOM = AT Command
    #SuccessMsg = Success confirmation response, eg: "OK"
    #SubStr1, SubStr2 = strings for start and end index to get Substring from response with negative indent, by default =""
    #indent1, indent2 = negative indent values (minus value to move index forward), by default =0
    #sleepAfterCom = sleep between AT Command and Response from Sim Modul (in sec), by default =.2

    counter = 0
    print()
    # print(ATCOM)
    # ser.write(ATCOM.encode())
    # # sleep(0.1)
    # # ser.flushOutput()
    # sleep(sleepAfterCom)
    # res = ShowResponseData()
    while True:
        print(ATCOM)
        ser.write(ATCOM.encode())
        # sleep(0.1)
        # ser.flushOutput()
        sleep(sleepAfterCom)
        res = ShowResponseData()

        if SuccessMsg in res:
            mesg = SubStringInd(SubStr1, SubStr2, res, indent1, indent2)
            print(mesg)
            global MessageSim 
            MessageSim = mesg
            mesg = ""
            print("OK\nContinue\n\n")
            break
        else:
            print("Counter++")
            counter+=1
            print("Counter:", counter)
            
        #Checking counter    
        if counter < 4:
            print("\nTrying one more time")
            sleep(1)
            continue
        else:
            Error_detected(res)
            return 1 
    return 0
#end of SendAT()


# Prints Response from serial buffer
def ShowResponseData():
    print()
    response = ser.readlines()
    # print("Read response:")
    # print('\n'+ str(response)) #uncomment if you want print response bytes 
    return str(response)

#end of ShowResponseData()


#To get Substring from String with negative indent
def SubStringInd(indStr1, indStr2, str0, indent1=0, indent2=0): #use indent with minus value to move index forward
    ind1 = str0.find(indStr1)
    # print(ind1) #uncomment if you want print index value
    ind2 = str0.find(indStr2, ind1, (len(str0)-1))
    # print(ind2) #uncomment if you want print index value
    mesg = str0[ind1-indent1:ind2-indent2]
    return mesg

#end of SubStringInd()


# Prepare for reading SMS
def Prep():
    res = 0
    #Sending AT command to check whether modem is working
    res = SendAT("AT\r", "OK")
    if res == 1:
        return 1
 
    #Show the SIM model
    res = SendAT("ATI\r", "OK", "SIM", "r", 0, 1)
    if res == 1:
        return 1 

    #Show the network settings
    res = SendAT("AT+COPS?\r", "OK", "+COPS:", "r", 0, 1)
    if res == 1:
        return 1

    #Get curren functionality status
    res = SendAT("AT+CFUN?\r", "OK", "+CFUN:", "r", 0, 1)
    if res == 1:
        return 1    

    #Show SIM status
    res = SendAT("AT+CSCS?\r", "OK", "+CSCS:", "r", 0, 1)
    if res == 1:
        return 1 

    #Show registration status
    res = SendAT("AT+CREG?\r", "OK", "+CREG:", "r", 0, 1)
    if res == 1:
        return 1   

    #Show signal strength
    res = SendAT("AT+CSQ\r", "OK", "+CSQ:", "r", 0, 1)
    if res == 1:
        return 1 


    #Set messages to Text mode
    res = SendAT("AT+CMGF=1\r", "OK")
    if res == 1:
        return 1 

    #Allow indication of receipt of SMS without displaying their content
    res = SendAT("AT+CNMI=2,1\r", "OK")
    if res == 1:
        return 1    

    #Assign SIM memory to view, write and receive SMS
    res = SendAT("AT+CPMS=\"SM\",\"SM\",\"SM\"\r", "OK")
    if res == 1:
        return 1 

    
    # #Show the fullness and capacity of the memory
    # res = SendAT("AT+CPMS?\r", "OK", "SM", ",\"SM", -4)
    # if res == 1:
    #     return 1 
    # print("The fullness and capacity of the memory:" + MessageSim)

    # ind = MessageSim.find(",")
    # fullness = MessageSim[0:ind]
    # capacity = MessageSim[ind:(len(MessageSim)-1)]
    # if fullness >= capacity:
    #     #Delete all messages from memory
    #     res = SendAT("AT+CMGD=1,4\r", "OK")
    #     if res == 1:
    #         return 1

    return 0    
   
#end of Prep

#Reads SMS and upload to server via mqtt protocol
def ReadSMS():
    clientName = "RASPBERRY"
    # clientName += SMS_Content[(SMS_Content.find("=")+1):(SMS_Content.find(" ")-0) ]
    print("client name:", clientName)
    mqtt.Client.connected_flag = False #create flag in class
    mqtt.Client.bad_connection_flag = False
    
    client = mqtt.Client(clientName)   #create new instance
    client.username_pw_set(username=usrName, password=usrPass)
    client.on_connect = on_connect     #bind call back function
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish

    #Reading SMS from memory
    SMS_Content = ""
    #Open file with numbers
    file = open("/home/pi/Documents/SMS_Reading_and_Uploading/Mobile Numbers.txt")
    MNumbers = file.readlines()
    file.close()
    print(MNumbers)
    #Numbers are read

    #Show the fullness and capacity of the memory
    res = SendAT("AT+CPMS?\r", "OK", "SM", ",\"SM", -4)
    if res == 1:
        return 1 
    print("The fullness and capacity of the memory:" + MessageSim)

    ind = MessageSim.find(",")
    fullness = MessageSim[0:ind]
    capacity = MessageSim[ind:(len(MessageSim)-1)]




    #Scanning memory
    i = 1
    
    while i <= int(fullness):
        res = SendAT("AT+CMGR=" + str(i) + "\r", "OK", ":", "OK", -14, 18, 2)
        if res == 1:
            return 1 
        print(MessageSim) 

        numb = MessageSim[1:(MessageSim.find(",")-1)]
        print("\nNumber of Sender:  " + numb)
        if numb in str(MNumbers):
            print("True")
            SMS_Content = MessageSim[(MessageSim.find("r")+10):(len(MessageSim))]
            print("SMS Content: " + SMS_Content + "\n\n")
            j = 0
            while j <= 3:
                #Mqtt publish part
                client.connected_flag = False   #create flag in class
                client.bad_connection_flag = False
                pub = False
                print("\nMQTT Publish part\n")
                # topic = SMS_Content[0:SMS_Content.find(",")]
                topic = "meteodb"
                # payload = SMS_Content[(SMS_Content.find(",")+1):len(SMS_Content)]
                payload = SMS_Content                                                                                     
                print("topic:", topic)
                print("payload:", payload)

                # client.loop()
                print("Connecting to broker", broker)
                try:
                    client.connect(broker)             #connect to broker

                except:
                    Error_detected("connection failed")
                    j+=1    
                    continue
                # while not client.connected_flag and not client.bad_connection_flag:   #wait in loop
                #     print("In wait loop")
                #     sleep(1)

                # if client.connected_flag: #if connected 
                if True:  
                    print("Connected") 
                    res = client.publish(topic, payload)
                    sleep(5)
                    print("res:", str(res)[1:2])
                    if str(res)[1:2] == "0":
                        print("Success  OK")
                        pub = True
                        client.loop_stop()                 #stop loop
                        client.disconnect()
                        break
                    else:
                        Error_detected("MQTT publish error: " + str(res))
                        j+=1
                # if client.bad_connection_flag:   #if not connected   
                #     Error_detected("Bad connection flag is True")
                #     j+=1
                client.loop_stop()                 #stop loop
                client.disconnect()                #disconnect    
                if pub:
                    break    
                # client.loop_stop()                 #stop loop
                # client.disconnect()                #disconnect
        else:
            print("Wrong message from wrong number")
        i+=1   

    


    # #Delete all messages from memory
    # print("Deleting allmessags")
    # res = SendAT("AT+CMGD=1,4\r", "OK")
    # if res == 1:
    #     return 1


if GPIO.input(SIM_STA) == 0:
    Modem_on()
Prep()
# t = 0
# while True:
#     ShowResponseData()
#     sleep(10)
#     t += 10
#     if (t * 10) > 300:
#         break

ReadSMS()
GPIO.cleanup()