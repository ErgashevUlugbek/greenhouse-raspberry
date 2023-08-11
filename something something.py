def AT_Command_Sender(com, res):
    Response = ""
    counter = 0
    print("counter=0")
    com = com + "\r"
    ser.write(com.encode())
    Response = ser.readlines()
    print(str(Response[0], "UTF-8"))
    print(str(Response[1], "UTF-8"))
    
    while True:
        if res in str(Response[1], "UTF-8"):
            return 1
        else:
            print("Counter++")
            counter+=1
            print("Counter:", counter)
            
        #Checking counter    
        if counter < 4:
            print("\nTrying one more time")
            continue
        else:
            Error_detected(str(Response[1], "UTF-8"))
            return 0  