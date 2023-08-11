#!/usr/bin/python
from time import sleep
import time, sys
import RPi.GPIO as GPIO
import datetime
import serial
import re
import vlc

# '--aout=alsa'
instance = vlc.Instance()
p = instance.media_player_new()

ser = serial.Serial("/dev/ttyS0", baudrate = 9600, timeout = 1)
print(ser.name)
sleep(0.1)
ser.flush()

Flag = 0
Balance = ""
balance_check = "*100*1#"

def Error_detected(err):
    print("Error detected")
    print(err)
    error_code = err
    
#end of Error_detected()    
    
def Play_Message(n, m):
    p.pause()
    sleep(0.2)
    sound_file = ""
    if n == -1:
        sound_file = "./Ovozli_javoblar/Assalom.mp3"
        mess = instance.media_new(sound_file)
        p.set_media(mess)
        p.play()
        return 0
    
    if n == -2:
        sound_file = "./Ovozli_javoblar/Timeout.mp3"
        mess = instance.media_new(sound_file)
        p.set_media(mess)
        p.play()
        return 0
    
    if n == -3:
        sound_file = "./Ovozli_javoblar/Disconnecting2.mp3"
        mess = instance.media_new(sound_file)
        p.set_media(mess)
        p.play()
        sleep(4)
        p.pause()
        return 0
    
    if n == -4:
        sound_file = "./Ovozli_javoblar/ConfirmIt.mp3"
        mess = instance.media_new(sound_file)
        p.set_media(mess)
        p.play()
        sleep(4)
        p.pause()
        return 0
        
    
    if m == 0:
        sound_file = "./Ovozli_javoblar/" + str(n) + ".mp3"
        mess = instance.media_new(sound_file)
        p.set_media(mess)
        p.play()
        return 0
    
    if m != 0:
        sound_file = "./Ovozli_javoblar/raqamlar/" + str(m) + "-.mp3"
        mess = instance.media_new(sound_file)
        p.set_media(mess)
        p.play()
        
        sleep(0.8)
        p.pause()
        
        sound_file = "./Ovozli_javoblar/" + str(n) + ".mp3"
        mess = instance.media_new(sound_file)
        p.set_media(mess)
        p.play()
        return 0
    
#end of Play_Message()
    
    
def Alarm_call(aCode, call_number, id_gh):
    Flag = 0
    error_code = ""
    counter = 0
    Response = ""
    com = ""
    
    #Preparation block
    print("\nPREPARATION BLOCK")
    print("counter=0\n")
    
    #Checking whether sim is not locked and it is ready
    print("Checking whether sim is not locked and it is ready")
    com = "AT+CPIN?\r"
    ser.write(com.encode())
    Response = ser.readlines()
    print(str(Response[0], "UTF-8"))
    print(str(Response[1], "UTF-8"))
    
    while True:
        if "READY" in str(Response[1], "UTF-8"):
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
            Error_detected(str(Response[1], "UTF-8"))
            return 0  
    
    counter = 0
    Response = ""
    com = ""
#     print("counter=0")
    
    
    #Checking the signal strength
    print("Checking the signal strength")
    com = "AT+CSQ\r"
    ser.write(com.encode())
    Response = ser.readlines()
    print(str(Response[0], "UTF-8"))
    print(str(Response[1], "UTF-8"))
    signal = re.search(": (.*),", str(Response[1]))
    
    while True:
        if signal != "99" and signal != "0":
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
            Error_detected(str(Response[1], "UTF-8"))
            return 0 

    counter = 0
    #Checking what network is the device on
    print("Checking what network is the device on")
    com = "AT+COPS?\r"
    ser.write(com.encode())
    Response = ser.readlines()
    print(str(Response[0], "UTF-8"))
    print(str(Response[1], "UTF-8"))
    
    while True:
        if "+COPS:" in str(Response[1], "UTF-8"):
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
            Error_detected(str(Response[1], "UTF-8"))
            return 0 
    
    
    counter = 0
    #Checking the registration status of the device
    print("Checking the registration status of the device")
    com = "AT+CREG?\r"
    ser.write(com.encode())
    Response = ser.readlines()
    print(str(Response[0], "UTF-8"))
    print(str(Response[1], "UTF-8"))
    ind1 = 0
    ind1 = str(Response[1]).find(',')
    stat = str(Response[1])[ind1+1]
    print("<stat> = ", stat)
    print()
    
    while True:
        if stat == "1":
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
            Error_detected(str(Response[1], "UTF-8"))
            return 0 
    
    
    counter = 0
    #Checking balance
    print("Checking balance")
    com = "AT+CUSD=1,\"" + balance_check + "\",15\r"
    ser.write(com.encode())
    sleep(4)
    Response = ser.readlines()
    sleep(1.5)
    str_X = ""
    for x in Response:
        str_X += x.decode("iso-8859-1")
        print(x.decode("iso-8859-1"))
        
#     print("Response:", str_X)
    while True:
        if "+CUSD: " in str_X:
            Balance = re.search("\"(.*)\", 15", str_X).group(1)
            print("Balance:", Balance)
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
            for x in Response:
                str_X += x
            Error_detected(str_X)
            return 0 
    
    
    counter = 0
    #Report a list of current calls automatically
    print("Report a list of current calls automatically")
    com = "AT+CLCC=1\r"
    ser.write(com.encode())
    Response = ser.readlines()
    print(str(Response[0], "UTF-8"))
    print(str(Response[1], "UTF-8"))
    
    while True:
        if "OK" in str(Response[1]):
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
            Error_detected(str(Response[1], "UTF-8"))
            return 0
        
        
    
    counter = 0
    #Enable Call termination indication
    print("Enable Call terminal indication")
    com = "AT+CDRIND=1\r"
    ser.write(com.encode())
    Response = ser.readlines()
    print(str(Response[0], "UTF-8"))
    print(str(Response[1], "UTF-8"))
    
    while True:
        if "OK" in str(Response[1]):
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
            Error_detected(str(Response[1], "UTF-8"))
            return 0
    
    
    
    counter = 0
    #Enable DTMF detection control
    print("Enable DTMF detection control")
    com = "AT+DDET=1\r"
    ser.write(com.encode())
    Response = ser.readlines()
    print(str(Response[0], "UTF-8"))
    print(str(Response[1], "UTF-8"))
    
    while True:
        if "OK" in str(Response[1]):
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
            Error_detected(str(Response[1], "UTF-8"))
            return 0
        
        counter = 0
        
        
        
    #Calling block
    print("\nCALLING BLOCK")        
    DTMF_num = "0"
    DTMF_counter = 0
    Flag = 0
    Timeout = 60
    Time = int(time.time())
    Response = ""
#   aCode, call_number, id_gh
    
    
    sleep(0.1)    
    ser.flush()
    ser.read_all()
    sleep(0.1)
    
    #Calling user
    print("Calling User\nATD", end="")
    print(call_number)
    com = "ATD" + call_number + "\r"
    ser.write(com.encode())
    Response = ser.readlines()
    print(str(Response[0], "UTF-8"))
    print(str(Response[1], "UTF-8"))
    
    while True:
        if "OK" in str(Response[1], "UTF-8"):
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
            Error_detected(str(Response[1], "UTF-8"))
            return 0
        
        counter = 0
    
    while True:
        print("Time:", int(time.time()) - Time)
        if (int(time.time()) - Time) > Timeout:
            #Timeout
            print("Timeout")
            Play_Message(-2, 0)
            sleep(1.2)
            break
        
                
#         sleep(2)
#         ser.flush()
#         ser.flushInput()
#         ser.flushOutput()
#         ser.read_all()
#         sleep(0.1)

        Response = ser.readline()
        sleep(0.5)
        str_X = ""
        print("Response: ", Response, sep = "")
        str_X = str(Response, "iso-8859-1")
#         for x in Response:
#             str_X += str(x, "UTF-8")
#             print(str(x, "UTF-8"))
        
        print("Response str:", str_X)
        
        if Response == b'':
            continue
        
        if "+CDRIND: 0" in str_X:
            #Call terminated
            print("Call terminated")
            break
        
        if "+CLCC: " in str_X:
            ind1 = 0
            stat = "6"
#             ind1 = str_X.find(',')
            stat = str_X[11]
            
            if stat == "2":
                print("Dialing")
                
            if stat == "3":
                print("Alerting\nTimer = 15 sec\nTime = 0")
                Timeout = 15
                Time = int(time.time())
                
            if stat == "1":
                print("Holding\nTimer = 15 sec\nTime = 0")
                Timeout = 15
                Time = int(time.time())
                
            if stat == "5":
                print("Waiting\nTimer = 15 sec\nTime = 0")
                Timeout = 15
                Time = int(time.time())
                
            if stat == "6":
                print("Disconnect\nTimer = 0 sec\nTime = 0")
                Timeout = 0
                Time = int(time.time())
                sleep(1)
                
            if stat == "0":
                print("Active\nTimer = 60 sec\nTime = 0")
                Timeout = 60
                Time = int(time.time())
                Play_Message(-1, 0)
                sleep(7.2)
                Play_Message(aCode, id_gh)
                sleep(5.2)
                Play_Message(-4, 0)
                
                
        if "+DTMF: " in str_X:

#                 DTMF_counter = DTMF_counter - 1
#                 num_t = int(str_X[7])
#                 DTMF_num += (num_t * (10**(DTMF_counter)))
            DTMF_num = str_X[7]
            print("DTMF_num:", DTMF_num)
                
            if DTMF_num == "1":
                #Confiramtion
                print("Confirmation")
#                 DTMF_counter = 2
                Flag = 1
                Play_Message(1, 0)
                sleep(1.5)
                break
                
            elif DTMF_num != "1":
                #Not confirmed
                print("Not confirmed")
                Flag = 0
#                 DTMF_counter = 2
                Play_Message(0, 0)
                sleep(2)
#                 print("DTMF_counter: ", str(DTMF_counter), "\nDTMF_num: ", str(DTMF_num), "\n")
#             elif DTMF_counter <= 0:
#                 if DTMF_num == 179:
#                     #Confiramtion
#                     print("Confirmation")
#                     Flag = 1
#                     Play_Message(1, 0)
#                     sleep(1.5)
#                     break
#                 
#                 elif DTMF_num != 179:
#                     #Not confirmed
#                     print("Not confirmed")
#                     Flag = 0
#                     Play_Message(0, 0)
#                     sleep(1)
    

    #Disconnecting
    print("Disconnecting")
    Play_Message(-3, 0)
    com = "ATH\r"
    ser.write(com.encode())
    Response = ser.readlines()
    str_X = ""
    for x in Response:
        str_X += x.decode("UTF-8")
    print(str_X)
    
    while True:
        if "OK" in str_X:
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
            Error_detected(str(Response[1], "UTF-8"))
            return Flag
        
    counter = 0
    return Flag
        
        
#End of Alar_call()



com = "AT\r"
ser.write(com.encode())
Response = ser.readlines()
print(str(Response[0], "UTF-8"))
print(str(Response[1], "UTF-8"))
    

if "OK" in str(Response[1], "UTF-8"):
    print("Continue\n")


# Alarm_call(7, "00998971397700;", 5)
Alarm_call(3, "00998993205472;", 2)
# Alarm_call(2, "00998973441136;", 5)
# Alarm_call(4, "00998977678379;", 4)
