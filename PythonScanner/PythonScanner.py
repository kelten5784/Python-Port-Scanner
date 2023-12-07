import socket
import ipaddress
import threading


##Globles
COMMONPORTS = [80, 443, 21, 22, 445,]
LASTPORT = COMMONPORTS[-1]
CHECKER = False

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
            save_log = input("Do you want to save the console log to a scan list file? (yes/no): ").lower()
            if save_log == 'yes':
                save_file()
            print("Exiting the program.")
            return  ## Add a return statement to exit the loop
        else:
            print("Invalid option. Please enter 'yes' or 'no.'")

###################################################################################################################################
##1. Port Filtering
def specific_ports(target, port, is_open):
    try:
        ##Creates a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Set a timeout for the connection attempt

        ##Attempt to connect to the target and port
        result = sock.connect((target, port))

        ##Runs if the socket is open(bool) | EXECPTION if connection is refused 
        if is_open:
            print(f"Port {port} is open")

    except ConnectionRefusedError:
        if not is_open:
            print(f"Port {port} is closed | Error: ConnectionRefusedError")

    except socket.timeout:
        if not is_open:
            print(f"Port {port} timed out | Error: socket.timeout")

    except Exception as e:
        print(f"Port {port} Had An Unknown error occurred: {e}")

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

##Main Funcation for a through scan
def thorough_scan(target, start_port, end_port, filter_option):
    use_port_list = input("Do you want to use a port list? (yes/no): ").lower()

    if use_port_list == 'yes':
        port_list = input("Enter the port list (comma-separated): ")
        port_list = [int(port) for port in port_list.split(',')]
        CHECKER = True
    else:
        ##Validates whether the input is in proper configuration with possible ports (0-65535)
        start_port = int(input("Enter the initial port: "))
        if start_port <= 0 or start_port > 65535:
            print("Invalid Start Port")
            restart_program()

        end_port = int(input("Enter the last port: "))
        if end_port <= 0 or end_port > 65535:
            print("Invalid End Port")
            restart_program()

        CHECKER = True
        LASTPORT = end_port
        port_list = range(start_port, end_port + 1)


    ## Create a thread for each port in the range or in the specified port list
    threads = []
    for port in port_list:
        thread = threading.Thread(target=specific_ports, args=(target, port, True))
        threads.append(thread)
        thread.start()

    ## Wait for all threads to finish
    for thread in threads:
        thread.join()

    ## Filter results based on user input
    for port in port_list:
        if filter_option == 'open':
            specific_ports(target, port, True)
        elif filter_option == 'closed':
            specific_ports(target, port, False)
        elif filter_option == 'all':
            single_scan(target, port)
        else:
            print("Invalid filter option. Please enter 'open', 'closed', or 'all'.")

##Scans single port
def single_scan(target, port):
    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Set a timeout for the connection attempt

        # Attempt to connect to the target and port
        result = sock.connect((target, port))
    except ConnectionRefusedError:
        print(f"Port {port} is closed | Error: ConnectionRefusedError")

    except socket.timeout:
        print(f"Port {port} timed out | Error: socket.timeout")

    except Exception as e:
        print(f"Port {port} occurred an error: {e}")

    finally:
        sock.close()

        # Check if the current port is the last one
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

    start_port = 0
    end_port = 0
    target = input("Enter the target IP address or hostname: ")
    filter_option = input("Enter filter: (open/closed/all): ").lower()

    ##Validate whether the input is a valid IP address
    while True:
        try:
            ipaddress.ip_address(target)
            break  ##Exit loop if the user input is a valid IP address
        except ValueError:
            print("Invalid IP address format. Please enter a valid IP address. Example (192.168.1.1)")
            target = input("Enter the target IP address or hostname: ")

    ##Prompts user for their scan mode and runs the scan type
    scan_mode = input("Enter scan mode (quick/thorough): ").lower()

    if scan_mode == 'quick':
        quick_scan(target, filter_option)
        print(f"Scanning ports {start_port} to {end_port} on {target}...\n")

    elif scan_mode == 'thorough':
        thorough_scan(target, start_port, end_port, filter_option)
        if CHECKER:
            thorough_scan(target, start_port, end_port, filter_option)
            print(f"Scanning ports {start_port} to {end_port} on {target}...\n")

    else:
        print("Invalid input for our scan mode option. Please enter 'quick' or 'thorough'")
        restart_program()
if __name__ == "__main__":
    main()
###################################################################################################################################
