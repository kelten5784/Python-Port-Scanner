import socket
import ipaddress
import threading


## Globals
COMMONPORTS = [80, 443, 21, 22, 445,]
LASTPORT = COMMONPORTS[-1]
CHECKER = False
STARTPORT = 0  
ENDPORT = 0  
RESTARTFLAG = False  ##Flag to control program restart
USERLOGS = []
###################################################################################################################################
## System Functions

###################################################################################################################################
 ## 7. Function to prompt user to savefile
def save_file(log_entries):
    filename = input("Enter the filename to save the port list to (e.g., log.txt, log.cvv, etc): ")
    with open(filename, 'w') as file:
        for entry in log_entries:
            file.write(entry)
    print(f"Scanner file saved to {filename}")

## Function to prompt user to restart
def restart_program():
    global USERLOGS  # Access the global variable
    ##Loop to allow the user to enter a valid reset option
    while True:
        restart = input("\n Do you want to try again? (yes/no): ").lower()
        if restart == 'yes':
            main()
        elif restart == 'no':
            save_log = input("Do you want to save the console log to a scan list file? (yes/no): \n").lower()
            if save_log == 'yes':
                save_file(USERLOGS)
                print("Saving and Exiting the program.")
            elif save_log == 'no':
                print("Exiting the program.")
                exit()
            return  ##Add a return statement to exit the loop
        else:
            print("Invalid option. Please enter 'yes' or 'no.'")

###################################################################################################################################
## 10. Function to define IP and IP range
## Function to define IP and IP range
def parse_targets(user_target):
    more_targets = []

    while True:
        targets = [t.strip() for t in user_target.split(',')]
        more_targets = []

        for target in targets:
            if '-' in target:
                start, end = target.split('-')
                try:
                    start_ip = int(ipaddress.IPv4Address(start.strip()))
                    end_ip = int(ipaddress.IPv4Address(end.strip()))
                    more_targets.extend(str(ipaddress.IPv4Address(ip)) for ip in range(start_ip, end_ip + 1))
                except ValueError:
                    print(f"Invalid IP address range: {target}")
            else:
                try:
                    more_targets.append(str(ipaddress.IPv4Address(target.strip())))
                except ValueError:
                    print(f"Invalid IP address: {target}")

        if more_targets:
            break
        else:
            user_target = input("Enter the target IP addresses or hostnames (comma-separated or IP range (-) ): ")

    return more_targets



###################################################################################################################################
## 1. Port Filtering
def specific_scan(target, port, is_open):
    try:
        ## Creates a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(9)  # Set a timeout for the connection attempt

        ## Attempt to connect to the target and port
        result = sock.connect((target, port))

        ## Runs if the socket is open(bool) | Exception if connection is refused
        if is_open:
            message = f"Port {port} is open"
            print(message)
            USERLOGS.append(message + "\n")

    except ConnectionRefusedError:
        if not is_open:
            message = f"Port {port} is closed"
            print(message)
            USERLOGS.append(message + "\n")

    except socket.timeout:
        if not is_open:
            message = f"Port {port} timed out"
            print(message)
            USERLOGS.append(message + "\n")

    except Exception as e:
        message = f"Port {port} Had An Unknown error occurred: {e}"
        print(message)
        USERLOGS.append(message + "\n")

    finally:
        sock.close()
        if RESTARTFLAG:
            restart_program()
        


###################################################################################################################################
##2. Scan Modes 
##3. Custom Port Lists 
def quick_scan(target, filter_option, RESTARTFLAG, specific_scan):
    threads = []
    
    # Start threads for scanning
    for port in COMMONPORTS:
        thread = threading.Thread(target=specific_scan, args=(target, port, RESTARTFLAG))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Check filter_option and restart unconditionally
    if filter_option in ['open', 'closed', 'all']:
        RESTARTFLAG = True
        restart_program()
    else:
        print("Invalid filter option. Please enter 'open', 'closed', or 'all'.")
        restart_program()



##Main Function for a thorough scan
def thorough_scan(target, STARTPORT, ENDPORT, filter_option, specific_scan):
    global LASTPORT
    global RESTARTFLAG

    use_port_list = input("Do you want to use a port list? (yes/no): ").lower()

    if use_port_list == 'yes':
        port_list = input("Enter the port list (comma-separated): ")
        port_list = [int(port) for port in port_list.split(',')]
    else:
        STARTPORT = int(input("Enter the initial port: "))
        if STARTPORT <= 0 or STARTPORT > 65535:
            print("Invalid Start Port")
            RESTARTFLAG = True  ##Set the flag to restart the program

        ENDPORT = int(input("Enter the last port: "))
        if ENDPORT <= 0 or ENDPORT > 65535:
            print("Invalid End Port")
            RESTARTFLAG = True  ##Set the flag to restart the program

        port_list = range(STARTPORT, ENDPORT + 1)

    ## Create a thread for each port in the range or in the specified port list
    threads = []
    for port in port_list:
        thread = threading.Thread(target=specific_scan, args=(target, port, True))
        threads.append(thread)
        thread.start()

    ## Wait for all threads to finish
    for thread in threads:
        thread.join()

    ## Filter results based on user input
    for port in port_list:
        if filter_option == 'open':
            specific_scan(target, port, False)
        elif filter_option == 'closed':
            specific_scan(target, port, False)
        elif filter_option == 'all':
            specific_scan(target, port, False)
        else:
            print("Invalid filter option. Please enter 'open', 'closed', or 'all'.\n")

    ## Update LASTPORT for a thorough scan
    LASTPORT = ENDPORT

    return RESTARTFLAG  ## Return the flag
 

##Scans single port


###################################################################################################################################
def main():
    user_target = input("Enter the target IP addresses or hostnames (comma-separated or IP range (-) ): ")
    targets = parse_targets(user_target)

    for target in targets:
        while True:
            try:
                ipaddress.ip_address(target)
                break
            except ValueError:
                print(f"Invalid IP address or hostname format: {target}")
                user_target = input("Enter the target IP addresses or hostnames (comma-separated or IP range (-) ): ")
                targets = parse_targets(user_target)

    while True:
        filter_option = input("Enter filter: (open/closed/all): ").lower()
        if filter_option in ['open', 'closed', 'all']:
            break
        else:
            print("Invalid filter option. Please enter 'open', 'closed', or 'all'.")

    scan_mode = input("Enter scan mode (quick/thorough): ").lower()

    threads = []
    RESTARTFLAG = False

    for target in targets:
        if scan_mode == 'quick':
            quick_scan(target, filter_option, RESTARTFLAG,specific_scan)
        elif scan_mode == 'thorough':
            RESTARTFLAG = thorough_scan(target, STARTPORT, ENDPORT, filter_option, specific_scan)
        else:
            print("Invalid input for our scan mode option. Please enter 'quick' or 'thorough'\n")
            restart_program()

if __name__ == "__main__":
    main()
