import socket
import ipaddress
import threading


##Globles
COMMONPORTS = [80, 443, 21, 22, 445,]
LASTPORT = COMMONPORTS[-1]
CHECKER = False
STARTPORT = 0  
ENDPORT = 0  

##Funcation to prompt user to savefile
def save_file():
    filename = input("Enter the filename to save the port list to (e.g., log.txt): ")
    with open(filename, 'w') as file:
        file.write()
    print(f"Scanner file saved to {filename}")

##Loop to allow the user to enter a valid reset option
def restart_program():
    while True:
        restart = input("Do you want to try again? (yes/no): ").lower()
        if restart == 'yes':
            main()
        elif restart == 'no':
            save_log = input("Do you want to save the console log to a scan list file? (yes/no): \n").lower()
            if save_log == 'yes':
                save_file()
            print("Saving and Exiting the program.")
            if save_log == 'no':
                print("Exiting the program.")
                main()
            return  ## Add a return statement to exit the loop
        else:
            print("Invalid option. Please enter 'yes' or 'no.'")

def parse_targets(user_target):
    targets = [t.strip() for t in user_target.split(',')]
    more_targets = []

    for target in targets:
        if '-' in target:
            start, end = target.split('-')
            start_ip = ipaddress.ip_address(start.strip())
            end_ip = ipaddress.ip_address(end.strip())
            more_targets.extend(str(ip) for ip in range(start_ip, end_ip + 1))
        else:
            more_targets.append(target)

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
            print(f"Port {port} is open\n")

    except ConnectionRefusedError:
        if not is_open:
            print(f"Port {port} is closed | Error: ConnectionRefusedError\n")

    except socket.timeout:
        if not is_open:
            print(f"Port {port} timed out | Error: socket.timeout\n")

    except Exception as e:
        print(f"Port {port} Had An Unknown error occurred: {e}\n")

    finally:
        sock.close()
###################################################################################################################################
##2. Scan Modes ##3. Custom Port Lists 
def quick_scan(target, filter_option):

    ##Creates a thread for each port in the range
    threads = []
    for port in COMMONPORTS:
        thread = threading.Thread(target=specific_ports, args=(target, port, True))
        threads.append(thread)
        thread.start()

    ##Waits for all threads to finish
    for thread in threads:
        thread.join()

    ##Filter results based on user input
    for port in COMMONPORTS:

        if filter_option == 'open':
            specific_ports(target, port, True)
        elif filter_option == 'closed':
            specific_ports(target, port, False)
        elif filter_option == 'all':
            single_scan(target, port)
        else:
            print("Invalid filter option. Please enter 'open', 'closed', or 'all'.")
    if port == LASTPORT:
        restart_program()

##Main Funcation for a through scan
def thorough_scan(target, STARTPORT, ENDPORT, filter_option):
    global LASTPORT
    global CHECKER

    use_port_list = input("Do you want to use a port list? (yes/no): ").lower()

    if use_port_list == 'yes':
        port_list = input("Enter the port list (comma-separated): ")
        port_list = [int(port) for port in port_list.split(',')]
        CHECKER = True
    else:
        ##Validates whether the input is in proper configuration with possible ports (0-65535)
        STARTPORT = int(input("Enter the initial port: "))
        if STARTPORT <= 0 or STARTPORT > 65535:
            print("Invalid Start Port")
            restart_program()

        ENDPORT = int(input("Enter the last port: "))
        if ENDPORT <= 0 or ENDPORT > 65535:
            print("Invalid End Port")
            restart_program()

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
            single_scan(target, port)
        else:
            print("Invalid filter option. Please enter 'open', 'closed', or 'all'.\n")

    ##Update LASTPORT for thorough scan
    LASTPORT = ENDPORT 

##Scans single port
def single_scan(target, port):
    try:
        ##Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)  # Set a timeout for the connection attempt

        ##Attempt to connect to the target and port
        result = sock.connect((target, port))
        print(f"Port {port} is open")

    except ConnectionRefusedError:
        print(f"Port {port} is closed | Error: ConnectionRefusedError")

    except socket.timeout:
        print(f"Port {port} timed out | Error: socket.timeout")

    except Exception as e:
        print(f"Port {port} occurred an error: {e}")

    finally:
        sock.close()

        ##Check if the current port is the last one
        if port == LASTPORT:
            restart_program()


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
##10. IP Range Scanning










###################################################################################################################################
##11. Security Scanning









###################################################################################################################################
## MAIN FUNCATION 
def main():
    global STARTPORT 
    global ENDPORT  
    global CHECKER

    user_target = input("Enter the target IP addresses or hostnames (comma-separated or IP range): ")
    targets = parse_targets(user_target)
    filter_option = input("Enter filter: (open/closed/all): ").lower()

    # Validate whether the inputs are valid IP addresses or hostnames
    for target in targets:
        while True:
            try:
                ipaddress.ip_address(target)
                break  # Exit loop if the user input is a valid IP address
            except ValueError:
                print(f"Invalid IP address or hostname format: {target}")
                user_target = input("Enter the target IP addresses or hostnames (comma-separated or IP range): ")
                targets = parse_targets(user_target)

    # Prompts user for their scan mode and runs the scan type
    scan_mode = input("Enter scan mode (quick/thorough): ").lower()

    # Create a thread for each target in the list
    threads = []
    for target in targets:
        if scan_mode == 'quick':
            thread = threading.Thread(target=quick_scan, args=(target, filter_option))
        elif scan_mode == 'thorough':
            # Assume that STARTPORT, ENDPORT, and CHECKER are defined elsewhere in your code
            thread = threading.Thread(target=thorough_scan, args=(target, STARTPORT, ENDPORT, filter_option))
        else:
            print("Invalid input for our scan mode option. Please enter 'quick' or 'thorough'\n")
            restart_program()

        threads.append(thread)
        thread.start()

if __name__ == "__main__":
    main()
###################################################################################################################################
