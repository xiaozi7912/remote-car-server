import bluetooth
from gpiozero import OutputDevice
import time
import threading

accelertor = OutputDevice(17)
light = OutputDevice(27)
is_light_blink = False

def handle_command(command):
    global is_light_blink
    if command == 'start':
        print('Motor started')
        accelertor.on()
        return 'Motor started'
    
    elif command == 'stop':
        accelertor.off()
        print('Motor stopped')
        return 'Motor stopped'
    
    elif command == 'light_on':
        light.on()
        is_light_blink = False
        print('Light turned on')
        return 'Light turned on'
    
    elif command == 'light_off':
        light.off()
        is_light_blink = False
        print('Light turned off')
        return 'Light turned off'
    
    elif command == 'light_blink':
        if not is_light_blink:
            is_light_blink = True
            light_thread = threading.Thread(target=light_blink)
            light_thread.start()
        print('Light blink')
        return 'Light blink'
    
    else:
        return 'Invalid command'
    
def light_blink():
    global is_light_blink
    while is_light_blink:
        light.on()
        time.sleep(0.5)
        light.off()
        time.sleep(0.5)

def start_bluetooth_server():
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    port = bluetooth.PORT_ANY
    server_sock.bind(("", port))
    server_sock.listen(1)

    bluetooth.advertise_service(server_sock, "MotorControlService",
                                service_id="00001101-0000-1000-8000-00805F9B34FB",
                                service_classes=[bluetooth.SERIAL_PORT_CLASS],
                                profiles=[bluetooth.SERIAL_PORT_PROFILE])

    print("Waiting for connection...")

    while True:
        client_sock, address = server_sock.accept()
        print(f"Connected to {address}")

        try:
            while True:
                data = client_sock.recv(1024).decode('utf-8')
                if not data:
                    print("Client disconnected.")
                    break 

                response = handle_command(data.strip())
                client_sock.send(response.encode('utf-8'))

        except bluetooth.btcommon.BluetoothError as e:
            print("Bluetooth error:", e)

        except OSError as e:
            print("OS error:", e)
            break 

        print("Closing connection")
        client_sock.close() 

    server_sock.close() 

if __name__ == '__main__':
    start_bluetooth_server()
