import bluetooth
from gpiozero import OutputDevice
import time
import threading
import json

motor_a = OutputDevice(pin=17, initial_value=True)
motor_b = OutputDevice(pin=18, initial_value=True)
accelertor = OutputDevice(pin=27, initial_value=False)
light_1 = OutputDevice(pin=22, initial_value=False)
light_2 = OutputDevice(pin=23, initial_value=False)
light_3 = OutputDevice(pin=9, initial_value=False)
light_4 = OutputDevice(pin=25, initial_value=False)
horn = OutputDevice(pin=11, initial_value=False)
music = OutputDevice(pin=8, initial_value=False)

direction = 1
light_status = 0
is_light_blink = False
light_thread = None


def handle_command(command):
    global direction, light_status, is_light_blink, light_thread

    if command == "forward":
        direction = 1
        motor_a.on()
        motor_b.on()
        response = {
            "status": True,
            "direction": direction,
            "light": light_status,
            "message": "Motor forward",
        }

    elif command == "backward":
        direction = 2
        motor_a.off()
        motor_b.off()
        response = {
            "status": True,
            "direction": direction,
            "light": light_status,
            "message": "Motor backward",
        }

    elif command == "start":
        accelertor.on()
        response = {
            "status": True,
            "direction": direction,
            "light": light_status,
            "message": "Motor started",
        }

    elif command == "stop":
        accelertor.off()
        response = {
            "status": True,
            "direction": direction,
            "light": light_status,
            "message": "Motor stopped",
        }

    elif command == "front_light_on":
        if light_status > 3:
            turn_off_all_light()

        light_status += 1
        is_light_blink = False
        light_1.on()
        light_2.on()
        response = {
            "status": True,
            "direction": direction,
            "light": light_status,
            "message": "front_light_on",
        }

    elif command == "back_light_on":
        if light_status > 3:
            turn_off_all_light()

        light_status += 2
        is_light_blink = False
        light_3.on()
        light_4.on()
        response = {
            "status": True,
            "direction": direction,
            "light": light_status,
            "message": "back_light_on",
        }

    elif command == "light_left_blink":
        turn_off_all_light()
        is_light_blink = True
        light_status = 4
        light_thread = threading.Thread(target=light_left_blink)
        light_thread.start()
        response = {
            "status": True,
            "direction": direction,
            "light": light_status,
            "message": "light_left_blink",
        }

    elif command == "light_right_blink":
        turn_off_all_light()
        is_light_blink = True
        light_status = 5
        light_thread = threading.Thread(target=light_right_blink)
        light_thread.start()
        response = {
            "status": True,
            "direction": direction,
            "light": light_status,
            "message": "light_right_blink",
        }

    elif command == "light_blink":
        turn_off_all_light()
        is_light_blink = True
        light_status = 6
        light_thread = threading.Thread(target=light_blink)
        light_thread.start()
        response = {
            "status": True,
            "direction": direction,
            "light": light_status,
            "message": "light_blink",
        }

    elif command == "light_off":
        turn_off_all_light()
        light_status = 0
        response = {
            "status": True,
            "direction": direction,
            "light": light_status,
            "message": "light_off",
        }

    elif command == "speaker_horn":
        horn.on()
        time.sleep(0.1)
        horn.off()
        response = {
            "status": True,
            "direction": direction,
            "light": light_status,
            "message": "Speaker horn",
        }

    elif command == "speaker_music":
        music.on()
        time.sleep(0.1)
        music.off()
        response = {
            "status": True,
            "direction": direction,
            "light": light_status,
            "message": "Speaker music",
        }

    else:
        response = {"status": False, "message": "Invalid command"}

    print(response)
    return json.dumps(response)


def turn_off_all_light():
    global light_status, is_light_blink, light_thread
    is_light_blink = False
    light_status = 0

    if light_thread is not None:
        light_thread.join()

    light_1.off()
    light_2.off()
    light_3.off()
    light_4.off()


def light_left_blink():
    global is_light_blink
    while is_light_blink:
        print("light_left_blink")
        light_1.on()
        light_3.on()
        time.sleep(0.5)
        light_1.off()
        light_3.off()
        time.sleep(0.5)


def light_right_blink():
    global is_light_blink
    while is_light_blink:
        print("light_right_blink")
        light_2.on()
        light_4.on()
        time.sleep(0.5)
        light_2.off()
        light_4.off()
        time.sleep(0.5)


def light_blink():
    global is_light_blink
    while is_light_blink:
        print("light_blink")
        light_1.on()
        light_2.on()
        light_3.on()
        light_4.on()
        time.sleep(0.5)
        light_1.off()
        light_2.off()
        light_3.off()
        light_4.off()
        time.sleep(0.5)


def start_bluetooth_server():
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    port = bluetooth.PORT_ANY
    server_sock.bind(("", port))
    server_sock.listen(1)

    bluetooth.advertise_service(
        server_sock,
        "MotorControlService",
        service_id="00001101-0000-1000-8000-00805F9B34FB",
        service_classes=[bluetooth.SERIAL_PORT_CLASS],
        profiles=[bluetooth.SERIAL_PORT_PROFILE],
    )

    print("Waiting for connection...")

    while True:
        client_sock, address = server_sock.accept()
        response = json.dumps(
            {
                "status": True,
                "direction": direction,
                "light": light_status,
                "message": "Connected",
            }
        )
        client_sock.send(response.encode("utf-8"))
        print(f"Connected to {address}")

        try:
            while True:
                data = client_sock.recv(1024).decode("utf-8")
                if not data:
                    print("Client disconnected.")
                    break

                response = handle_command(data.strip())
                client_sock.send(response.encode("utf-8"))

        except bluetooth.btcommon.BluetoothError as e:
            print("Bluetooth error:", e)

        except OSError as e:
            print("OS error:", e)
            break

        print("Closing connection")
        client_sock.close()

    server_sock.close()


if __name__ == "__main__":
    start_bluetooth_server()
