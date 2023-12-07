import socket

##Given CODE
def scan_port(target, port):
    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Set a timeout for the connection attempt

        # Attempt to connect to the target and port
        result = sock.connect((target, port))
        print(f"Port {port} is open")

    except ConnectionRefusedError:
        print(f"Port {port} is closed")

    except socket.timeout:
        print(f"Port {port} timed out")

    except Exception as e:
        print(f"An error occurred while scanning port {port}: {e}")

    finally:
        sock.close()
## Given CODE
def main():
    target = input("Enter the target IP address or hostname: ")
    scan_mode = input("Enter scan mode (quick/thorough): ").lower()

    if scan_mode == 'quick':
        filter_option = input("Enter filter: (open/closed/all): ").lower()
        quick_scan(target, filter_option)

    elif scan_mode == 'thorough':
        filter_option = input("Enter filter: (open/closed/all): ").lower()
        start_port = int(input("Enter the initial port: "))
        end_port = int(input("Enter the last port: "))
        print(f"Scanning ports {start_port} to {end_port} on {target}...\n")
        thorough_scan(target, start_port, end_port, filter_option)

    else:
        print("Invalid scan mode. Please enter 'quick' or 'thorough'.")

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
            print(f"Port {port} is closed")

    except socket.timeout:
        if not is_open:
            print(f"Port {port} timed out")

    except Exception as e:
        print(f"An error occurred while scanning port {port}: {e}")

    finally:
        sock.close()
###################################################################################################################################
##2. Scan Modes
def quick_scan(target, filter_option):
    common_ports = [80, 443, 21, 22]

    for port in common_ports:
        if filter_option == 'open':
            specific_ports(target, port, True)
        elif filter_option == 'closed':
            specific_ports(target, port, False)
        elif filter_option == 'all':
            scan_port(target, port)
        else:
            print("Invalid filter option. Please enter 'open', 'closed', or 'all'.")

def thorough_scan(target, start_port, end_port, filter_option):
    for port in range(start_port, end_port + 1):
        if filter_option == 'open':
            specific_ports(target, port, True)
        elif filter_option == 'closed':
            specific_ports(target, port, False)
        elif filter_option == 'all':
            scan_port(target, port)
        else:
            print("Invalid filter option. Please enter 'open', 'closed', or 'all'.")




###################################################################################################################################
##3. Custom Port Lists 






###################################################################################################################################
##4. User-Friendly CLI



###################################################################################################################################
##5. Support for Scanning Multiple Targets 







###################################################################################################################################
##6. Logging and Reporting








###################################################################################################################################
if __name__ == "__main__":
    main()
    
