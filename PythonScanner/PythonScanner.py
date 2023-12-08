import socket
import ipaddress
import threading


##Globles
COMMONPORTS = [80, 443, 21, 22, 445,]
LASTPORT = COMMONPORTS[-1]
CHECKER = False
STARTPORT = 0  
ENDPORT = 0  
RESTARTFLAG = False  ##Flag to control program restart
USERLOGS = []
###################################################################################################################################
##System Funcations 

 ##Funcation to prompt user to savefile
def save_file(log_entries):
    filename = input("Enter the filename to save the port list to (e.g., log.txt, log.cvv, etc): ")
    with open(filename, 'w') as file:
        for entry in log_entries:
            file.write(entry)
    print(f"Scanner file saved to {filename}")

##Funcation to prompt user to restart
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
##1. Port Filtering
def specific_ports(target, port, is_open):
    try:
        ##Creates a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # Set a timeout for the connection attempt

        ##Attempt to connect to the target and port
        result = sock.connect((target, port))

        ##Runs if the socket is open(bool) | EXECPTION if connection is refused 
        if is_open:
            message = f"Port {port} is open"
            print(message)
            USERLOGS.append(message)

    except ConnectionRefusedError:
        if not is_open:
            message = f"Port {port} is closed | Error: ConnectionRefusedError\n"
            print(message)
            USERLOGS.append(message)

    except socket.timeout:
        if not is_open:
            message = f"Port {port} timed out | Error: socket.timeout\n"
            print(message)
            USERLOGS.append(message)

    except Exception as e:
        message = f"Port {port} Had An Unknown error occurred: {e}\n"
        print(message)
        USERLOGS.append(message)

    finally:
        sock.close()

###################################################################################################################################
##2. Scan Modes ##3. Custom Port Lists 
def quick_scan(target, filter_option, RESTARTFLAG):

    threads = []
    for port in COMMONPORTS:
        thread = threading.Thread(target=single_scan, args=(target, port, RESTARTFLAG))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    for port in COMMONPORTS:
        if filter_option == 'open':
            single_scan(target, port, RESTARTFLAG)
        elif filter_option == 'closed':
            single_scan(target, port, RESTARTFLAG)
        elif filter_option == 'all':
            single_scan(target, port, RESTARTFLAG)
        else:
            print("Invalid filter option. Please enter 'open', 'closed', or 'all'.")
            restart_program()

    if RESTARTFLAG:
        restart_program()

##Main Funcation for a through scan
def thorough_scan(target, STARTPORT, ENDPORT, filter_option):
    global LASTPORT
    global CHECKER
    global RESTARTFLAG

    use_port_list = input("Do you want to use a port list? (yes/no): ").lower()

    if use_port_list == 'yes':
        port_list = input("Enter the port list (comma-separated): ")
        port_list = [int(port) for port in port_list.split(',')]
        CHECKER = True
    else:
        STARTPORT = int(input("Enter the initial port: "))
        if STARTPORT <= 0 or STARTPORT > 65535:
            print("Invalid Start Port")
            RESTARTFLAG = True  ##Set the flag to restart the program

        ENDPORT = int(input("Enter the last port: "))
        if ENDPORT <= 0 or ENDPORT > 65535:
            print("Invalid End Port")
            RESTARTFLAG = True  ##Set the flag to restart the program

        CHECKER = True
        LASTPORT = ENDPORT
        port_list = range(STARTPORT, ENDPORT + 1)

    ##Create a thread for each port in the range or in the specified port list
    threads = []
    for port in port_list:
        thread = threading.Thread(target=specific_ports, args=(target, port, True))
        threads.append(thread)
        thread.start()

    ##Wait for all threads to finish
    for thread in threads:
        thread.join()

    ##Filter results based on user input
    for port in port_list:
        if filter_option == 'open':
            specific_ports(target, port, True)
        elif filter_option == 'closed':
            specific_ports(target, port, False)
        elif filter_option == 'all':
            single_scan(target, port, RESTARTFLAG)
        else:
            print("Invalid filter option. Please enter 'open', 'closed', or 'all'.\n")

    ##Update LASTPORT for thorough scan
    LASTPORT = ENDPORT

    return RESTARTFLAG  ##Return the flag

 

##Scans single port
def single_scan(target, port, RESTARTFLAG):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)

        print(f"Scanning port {port} on target {target}...")

        result = sock.connect_ex((target, port))

        if result == 0:
            message = f"Port {port} is open"
            print(message)
            USERLOGS.append(message)

    except ConnectionRefusedError:
        message = f"Port {port} is closed | Error: ConnectionRefusedError\n"
        print(message)
        USERLOGS.append(message)

    except socket.timeout:
        message = f"Port {port} timed out | Error: socket.timeout\n"
        print(message)
        USERLOGS.append(message)

    except Exception as e:
        message = f"Port {port} encountered an error: {e}\n"
        print(message)
        USERLOGS.append(message)

    finally:
        sock.close()




###################################################################################################################################
##4. User-Friendly CLI



###################################################################################################################################
##5. Support for Scanning Multiple Targets 




###################################################################################################################################
##6. Logging and Reporting








###################################################################################################################################
##7. Output Customizaon





###################################################################################################################################
##8. Port Range Validaon





###################################################################################################################################
##9. Service Detecon






###################################################################################################################################
##11. Security Scanning









###################################################################################################################################
def main():
    global STARTPORT
    global ENDPORT
    global CHECKER
    global RESTARTFLAG

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
            quick_scan(target, filter_option, RESTARTFLAG)
        elif scan_mode == 'thorough':
            RESTARTFLAG = thorough_scan(target, STARTPORT, ENDPORT, filter_option)
        else:
            print("Invalid input for our scan mode option. Please enter 'quick' or 'thorough'\n")
            restart_program()

if __name__ == "__main__":
    main()
