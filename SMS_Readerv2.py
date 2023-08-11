#!/usr/bin/env python3
from cmath import nan
import string
from time import sleep
import time, sys
import RPi.GPIO as GPIO
import datetime
import serial
import datetime
import paho.mqtt.client as mqtt 
import json

SIM_POWK = 23 #Sim Power Key
SIM_STA = 24  # Sim On/Off status (if HIGH it's On and vice versa)

usrName = "admin"
usrPass = "inha2016"
broker = "oxus2.amudar.io"

network_operator_index = 3
netOper_apn = ["internet", "internet.beeline.uz", "internet.uzmobile.uz", "net.mobiuz.uz"]
netOper_user = ["", "beeline", "", ""]
netOper_pass = ["", "beeline", "", ""]

brokerURL = "http://oxus2.amudar.io:3001/api/"


MessageSim = ""

Unsent_dic = []

type(Unsent_dic)

Unsent_fol = []
type(Unsent_fol)


GPIO.setmode(GPIO.BCM)
GPIO.setup(SIM_POWK, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(SIM_STA, GPIO.IN)

ser = serial.Serial("/dev/ttyS0", baudrate = 9600, timeout = 1)
print()
print(ser.name)
sleep(0.1)
ser.flush()


# FUNCTIONS


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

    while True:
        print(ATCOM)
        ser.write(ATCOM.encode())
        sleep(0.1)

        sleep(sleepAfterCom)
        res = ShowResponseData()

        if SuccessMsg in res:
            mesg = SubStringInd(SubStr1, SubStr2, res, indent1, indent2)
            print(mesg)
            sleep(0.5)
            global MessageSim 
            MessageSim = mesg
            mesg = ""
            print("\nOK\nContinue\n\n")
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
    response = ser.readlines()
    # print("\nRead response:")
    # print('\n'+ str(response) + '\n') #uncomment if you want print response bytes 
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


#HTTP upload data in json
def HTTP_Upload(d, f):
    
    #Converts dictionary to JSON string
    data_json = json.dumps(d)
    print("\n\nJSON String:")
    print(data_json)
    print()
    respon = nan
    #Initiate the HTTP service
    res = SendAT("AT+HTTPINIT\r", "OK", "+HTTPINIT:", "r", 0, 1, 2)
    if res == 1:
        Error_detected("Uploading error: " + MessageSim)
        return 1        

    if res == 0:
        #Set the HTTP session
        res = SendAT("AT+HTTPPARA=\"CID\",1\r", "OK", "+HTTPPARA:", "r", 0, 1, 1)
        if res == 1:
            Error_detected("Uploading error: " + MessageSim)
            return 1

    if res == 0:
        #Set the HTTP session(URL of server)
        res = SendAT("AT+HTTPPARA=\"URL\",\"" + brokerURL + f + "\"\r", "OK", "+HTTPPARA:", "r", 0, 1, 1)
        if res == 1:
            Error_detected("Uploading error: " + MessageSim)
            return 1

    if res == 0:
        #Set the HTTP session (sets content type to JSON)
        res = SendAT("AT+HTTPPARA=\"CONTENT\",\"application/json\"\r", "OK", "+HTTPPARA:", "r", 0, 1, 1)
        if res == 1:
            Error_detected("Uploading error: " + MessageSim)
            return 1
    bytesJSON = bytes(data_json, "UTF-8")

    if res == 0:
        #Input HTTP data
        res = SendAT("AT+HTTPDATA=" + str(len(bytesJSON)) + ",10000\r", "")
        res = SendAT((data_json + "\r"), "OK", "", "", 0,0,2)
        # ser.write(bytesJSON) 
        # ser.write(b"\r")   
        # sleep(10)
        # ShowResponseData()

        if res == 1:
            Error_detected("Uploading error: " + MessageSim)
            return 1
   

    if res == 0:
        #HTTP POST session start
        res = SendAT("AT+HTTPACTION=1\r", "OK", "+HTTPACTION: ", "r", 0, 1, 10)
        if res == 1:
            Error_detected("Uploading error: " + MessageSim)
            return 1
        if "200" in MessageSim:
            print("Successfully uploaded")
            respon = 0
        else:
            Error_detected("Uploading error: " + MessageSim)
            respon = 1


    if res == 0:
        #Read the data of HTTP server
        res = SendAT("AT+HTTPREAD\r", "OK", "+HTTPREAD:", "OK", 0, 9, 2)
        if res == 1:
            Error_detected("Uploading error: " + MessageSim)
            return 1

    if res == 0:
        #Terminate HTTP service
        res = SendAT("AT+HTTPTERM\r", "OK", "+HTTPTERM:", "r", 0, 1, 2)
        if res == 1:
            Error_detected("Uploading error: " + MessageSim)
            return 1        
        if res == 0:
            print("Successfully Terminated")
    return respon      


# Prepare for reading SMS
def Prep():
    res = 0
    #Sending AT command to check whether modem is working
    res = SendAT("AT\r", "OK")
    if res == 1:
        Error_detected("Uploading error: " + MessageSim)
        return 1
 
    #Show the SIM model
    res = SendAT("ATI\r", "OK", "SIM", "r", 0, 1, 0.1)
    if res == 1:
        Error_detected("Uploading error: " + MessageSim)
        return 1 

    #Show the network settings
    res = SendAT("AT+COPS?\r", "OK", "+COPS:", ", ", 0, 5, 6)
    if res == 1:
        Error_detected("Uploading error: " + MessageSim)
        return 1

    #Get current functionality status
    res = SendAT("AT+CFUN?\r", "OK", "+CFUN:", "r", 0, 1, 0.1)
    if res == 1:
        Error_detected("Uploading error: " + MessageSim)
        return 1    

    #Set for full functionality
    res = SendAT("AT+CFUN=1\r", "OK","+CFUN:", "r", 0, 1, 0.1)
    if res == 1:
        Error_detected("Uploading error: " + MessageSim)
        return 1 

    #Show SIM status
    res = SendAT("AT+CSCS?\r", "OK", "+CSCS:", "r", 0, 1)
    if res == 1:
        Error_detected("Uploading error: " + MessageSim)
        return 1 

    #Show registration status
    res = SendAT("AT+CREG?\r", "OK", "+CREG:", "r", 0, 1)
    if res == 1:
        Error_detected("Uploading error: " + MessageSim)
        return 1   

    #Show signal strength
    res = SendAT("AT+CSQ\r", "OK", "+CSQ:", "r", 0, 1)
    if res == 1:
        Error_detected("Uploading error: " + MessageSim)
        return 1 

    #Check if module ready for sms, call, etc
    res = SendAT("AT+CPIN?\r", "OK", "+CPIN:", "r", 0, 1)
    if res == 1:
        Error_detected("Uploading error: " + MessageSim)
        return 1

    #Set messages to Text mode
    res = SendAT("AT+CMGF=1\r", "OK")
    if res == 1:
        Error_detected("Uploading error: " + MessageSim)
        return 1 

    #Allow indication of receipt of SMS without displaying their content
    res = SendAT("AT+CNMI=2,1\r", "OK")
    if res == 1:
        Error_detected("Uploading error: " + MessageSim)
        return 1    

    #Assign SIM memory to view, write and receive SMS
    res = SendAT("AT+CPMS=\"SM\",\"SM\",\"SM\"\r", "OK")
    if res == 1:
        Error_detected("Uploading error: " + MessageSim)
        return 1 


    #GPRS settings
    if res == 0:
        #Set APN,Username, Userpassword
        res = SendAT("AT+SAPBR=3,1,Contype,GPRS\r", "OK")
        if res == 1:
            Error_detected("Uploading error: " + MessageSim)
            return 1

        res = SendAT("AT+SAPBR=3,1,APN,\"" + netOper_apn[network_operator_index] + "\"\r", "OK")
        if res == 1:
            Error_detected("Uploading error: " + MessageSim)
            return 1

        res = SendAT("AT+SAPBR=3,1,USER,\"" + netOper_user[network_operator_index] + "\"\r", "OK")
        if res == 1:
            Error_detected("Uploading error: " + MessageSim)
            return 1 

        res = SendAT("AT+SAPBR=3,1,PWD,\"" + netOper_pass[network_operator_index] + "\"\r", "OK")
        if res == 1:
            Error_detected("Uploading error: " + MessageSim)
            return 1       
        
    # if res == 0:
    #     #Start wireless connection with the GPRS


    # if res == 0:
        #Show the IP address assigned to the module
        


        #Start wireless connection with the GPRS
        SendAT("AT+SAPBR=0,1\r", "OK", "+SAPBR", "r", 0, 1, 2)

        res = SendAT("AT+SAPBR=1,1\r", "OK", "+SAPBR:", "r", 0, 1, 6)
        if res == 1:
            Error_detected("Uploading error: " + MessageSim)
            return 1

        if res == 0:
            #Show the IP address assigned to the module
            res = SendAT("AT+SAPBR=2,1\r", "OK", "+SAPBR:", "r", 0, 1, 1)
            if res == 1:
                Error_detected("Uploading error: " + MessageSim)
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
    response = 0
    #Reading SMS from memory
    SMS_Content = ""
    #Open file with numbers
    file = open("/home/pi/Documents/SMS_Reading_and_Uploading/Mobile Numbers.txt")
    MNumbers = file.readlines()
    file.close()
    print(MNumbers, "\n\n")
    #Numbers are read

    #Show the fullness and capacity of the memory
    res = SendAT("AT+CPMS?\r", "OK", "+CPMS:", ",\"SM", -12)
    if res == 1:
        return 1 
    # print("The fullness and capacity of the memory:" + MessageSim)

    ind = MessageSim.find(",")
    fullness = MessageSim[0:ind]
    capacity = MessageSim[ind+1:len(MessageSim)]
    print("The fullness of the memory:" + fullness)
    print("The capacity of the memory:" + capacity + "\n")

    if int(fullness) == 0:
        print("The memory of messages is empty")
        return 0

    #Scanning memory
    j = 1
    
    while j <= int(fullness):
        res = SendAT("AT+CMGR=" + str(j) + "\r", "OK", ":", "OK", -14, 18, 2)
        if res == 1:
            return 1 
        print("SMS Content:\n" + MessageSim) 
        numb = ""
        numb = MessageSim[(MessageSim.find("+") + 1):(MessageSim.find(",", 5)-1)]
        print("\nNumber of Sender:  " + numb + "\n")
        if numb in str(MNumbers) and numb != "":
            print("True")
            SMS_Content = MessageSim[(MessageSim.find("b") + 0):(len(MessageSim))]
            print("SMS Content: " + SMS_Content[2:len(SMS_Content)] + "\n\n")
            if "metric" not in SMS_Content:
                Error_detected("Wrong content of message")
                j+=1
                continue
            
            folder = ""
            if "ghmetric" in SMS_Content:
                folder="ghmetrics"

            if "meteometric" in SMS_Content:
                folder = "meteometrics"

            data_split = SMS_Content.split(" ", 3)
            data1 = str(data_split[0])
            data2 = str(data_split[1])
            if len(data_split) == 3:
                data3 = str(data_split[2])
            else:
                data3 = ""    

            print("data1:", data1 ) 
            print("data2:", data2 )
            print("data3:", data3 )

            data1 = data1 + ","
            data2 = data2 + ","

            data_dict = {}
            type(data_dict) 

            #Writing data1 to dict
            i = 0
            print("\ni:", i)

            while i < len(data1):
                if data1[i] == "," and i != (len(data1) - 1):
                    key = data1[i+1:data1.find("=", i)]
                    value = data1[(data1.find("=", i) + 1):data1.find(",", i+1)]
                    print("i:", i)
                    print("\nkey:", key)
                    print("\nvalue:", value)
                    data_dict[key] = value
                    sleep(.1)
                i+=1

            #Writing data2 to dict
            i = 0
            print("\ni:", i)

            while i < len(data2):
                if data2[i] == "," and i != (len(data2) - 1):
                    key = data2[i+1:data2.find("=", i)]
                    value = data2[(data2.find("=", i) + 1):data2.find(",", i+1)]
                    print("i:", i)
                    print("\nkey:", key)
                    print("\nvalue:", value)
                    data_dict[key] = value
                    sleep(.1)
                i+=1
                   

            #writing data3 to dict if it's not empty
            if data3 != "":
                key = "timestamp"
                value = data3
                print("\nkey:", key)
                print("\nvalue:", value)
                data_dict[key] = value

            #Uploading data
            response = ""
            c = 0
            while c < 3:
                response = HTTP_Upload(data_dict, folder)
                if response == 0:
                    break
                c+=3
            if response == 1:
                print("Adding failed to upload data into Unsent data list\n")
                Unsent_dic.append(data_dict)
                Unsent_fol.append(folder)   

        else:
            print("\nWrong message from wrong number\n\n")

        j+=1   

    #Delete all messages from memory
    print("if response == 0 delete all messages from memory\nresponse: " + str(response))
    if response == 0:
        res = SendAT("AT+CMGD=1,4\r", "OK")
        if res == 1:
            return 1

    return response

#Uploads unsent data
def Send_Unsent():
    ind = []
    response = 0
    print("Uploading not uploaded data")
    for x in range(0, len(Unsent_dic), 1):
        response = HTTP_Upload(Unsent_dic[x], Unsent_fol[x])
        if response == 0:
            ind.append(x)

    #if data uploaded successfully delete this data from list
    for x in ind:
        Unsent_dic.pop(ind[x])
        Unsent_fol.pop(ind[x])        


#Main

if GPIO.input(SIM_STA) == 1:
    Modem_off()
if GPIO.input(SIM_STA) == 0:
    Modem_on()
sleep(5)
res = Prep()
t = 0

print("\nWaiting in delay...\n")
while True:
    messg = ""
    messg = str(ser.readlines())
    # print('\nmessg:', messg , '\n')
    if "+CMTI:" in messg:
        print("True")
        ind = messg.find("+CMTI")
        # print("ind:", ind)
        # print("r ind:", messg.find("r", ind))
        print(messg[messg.find("+CMTI:"):(messg.find("r", ind) - 1)], '\n')
        
        if res == 0:
            res = ReadSMS()
            if res == 1:
                if GPIO.input(SIM_STA) == 1:
                    Modem_off()
                if GPIO.input(SIM_STA) == 0:
                    Modem_on()

                SendAT("AT+SAPBR=0,1\r", "OK", "+SAPBR", "r", 0, 1, 2) 
                res = Prep()
                if len(Unsent_dic) != 0:
                    Send_Unsent()
        else:
            if GPIO.input(SIM_STA) == 1:
                    Modem_off()
            if GPIO.input(SIM_STA) == 0:
                    Modem_on()
            SendAT("AT+SAPBR=0,1\r", "OK", "+SAPBR", "r", 0, 1, 2)      
            res = Prep()
            if len(Unsent_dic) != 0:
                    Send_Unsent()
            
        print("\nWaiting in delay...\n")
    
    sleep(5)
    t += 5
    if t > 250:
        print("Timeout")
        if res == 0:
            if len(Unsent_dic) != 0:
                    Send_Unsent()
            res = ReadSMS()

            if res == 1:
                if GPIO.input(SIM_STA) == 1:
                    Modem_off()
                if GPIO.input(SIM_STA) == 0:
                    Modem_on()
                SendAT("AT+SAPBR=0,1\r", "OK", "+SAPBR", "r", 0, 1, 2)    
                res = Prep()
        else:
            if GPIO.input(SIM_STA) == 1:
                    Modem_off()
            if GPIO.input(SIM_STA) == 0:
                    Modem_on()
            SendAT("AT+SAPBR=0,1\r", "OK", "+SAPBR", "r", 0, 1, 2)       
            res = Prep()
        print("\nWaiting in delay...\n") 
        t = 0   

  
Modem_off()
GPIO.cleanup()