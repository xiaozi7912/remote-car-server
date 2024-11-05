from flask import Flask, request, jsonify
from gpiozero import OutputDevice
import time
import threading

app = Flask(__name__)

motor_a = OutputDevice(pin=17, initial_value=True)
motor_b = OutputDevice(pin=18, initial_value=True)
accelertor = OutputDevice(pin=27, initial_value=False)
light_1 = OutputDevice(pin=22, initial_value=False)
light_2 = OutputDevice(pin=23, initial_value=False)
light_3 = OutputDevice(pin=25, initial_value=False)
light_4 = OutputDevice(pin=9, initial_value=False)
horn = OutputDevice(pin=11, initial_value=False)
music = OutputDevice(pin=8, initial_value=False)

direction = 1
light_status = 0
is_light_blink = False
light_thread = None

@app.route('/motor', methods=['POST'])
def motor():
    global direction, light_status
    data = request.get_json() 

    if 'cmd' in data:
        cmd = data['cmd']
        value = data['value']
        match cmd:
            case 'accelertor':
                match value:
                    case 1:
                        accelertor.on()
                        response= jsonify({'code': 0,'direction':direction,'light_status':light_status, 'message': '馬達啟動'}), 200
                    case _:
                        accelertor.off()
                        response= jsonify({'code': 0,'direction':direction,'light_status':light_status, 'message': '馬達停止'}), 200
            case 'direction':
                match value:
                    case 1:
                        direction=1
                        motor_a.on()
                        motor_b.on()
                        response= jsonify({'code': 0,'direction':direction,'light_status':light_status, 'message': '前進'}), 200
                    case 2:
                        direction=2
                        motor_a.off()
                        motor_b.off()
                        response= jsonify({'code': 0,'direction':direction,'light_status':light_status, 'message': '後退'}), 200
    else:
        response= jsonify({'code': 400, 'message': '缺少參數'}), 400
    return response
    

@app.route('/light', methods=['POST'])
def light():
    global direction, light_status, is_light_blink, light_thread
    data = request.get_json()

    if 'cmd' in data:
        cmd = data['cmd'] 
        value = data['value']
        match cmd:
            case 'all':
                match value:
                    case 0:
                        turn_off_all_light()
                        light_status =0
                        response= jsonify({'code': 0,'direction':direction,'light_status':light_status, 'message': '燈全關'}), 200
                    case 1:
                        turn_on_all_light()
                        light_status =3
                        response= jsonify({'code': 0,'direction':direction,'light_status':light_status, 'message': '燈全開'}), 200
            case 'front_light':
                turn_off_all_light()
                match value:
                    case 1:
                        light_status =1
                        light_1.on()
                        light_2.on()
                        response= jsonify({'code': 0,'direction':direction,'light_status':light_status, 'message': '開前燈'}), 200
                    case _:
                        response= jsonify({'code': 400,'direction':direction,'light_status':light_status, 'message': '數值錯誤'}), 400
            case 'back_light':
                turn_off_all_light()
                match value:
                    case 1:
                        light_status =2
                        light_3.on()
                        light_4.on()
                        response= jsonify({'code': 0,'direction':direction,'light_status':light_status, 'message': '開後燈'}), 200
                    case _:
                        response= jsonify({'code': 400,'direction':direction,'light_status':light_status, 'message': '數值錯誤'}), 400
            case 'turn_left':
                turn_off_all_light()
                match value:
                    case 1:
                        light_status = 4
                        is_light_blink = True
                        light_thread = threading.Thread(target=turn_left_light)
                        light_thread.start()
                        response= jsonify({'code': 0,'direction':direction,'light_status':light_status, 'message': '左轉燈'}), 200
                    case _:
                        response= jsonify({'code': 400,'direction':direction,'light_status':light_status, 'message': '數值錯誤'}), 400
            case 'turn_right':
                turn_off_all_light()
                match value:
                    case 1:
                        light_status = 5
                        is_light_blink = True
                        light_thread = threading.Thread(target=turn_right_light)
                        light_thread.start()
                        response= jsonify({'code': 0,'direction':direction,'light_status':light_status, 'message': '右轉燈'}), 200
                    case _:
                        response= jsonify({'code': 400,'direction':direction,'light_status':light_status, 'message': '數值錯誤'}), 400
            case 'parking':
                turn_off_all_light()
                match value:
                    case 1:
                        light_status = 6
                        is_light_blink = True
                        light_thread = threading.Thread(target=parking_light)
                        light_thread.start()
                        response= jsonify({'code': 0,'direction':direction,'light_status':light_status, 'message': '臨停燈'}), 200
                    case _:
                        response= jsonify({'code': 400,'direction':direction,'light_status':light_status, 'message': '數值錯誤'}), 400
    else:
        response= jsonify({'code': 400, 'message': '缺少參數'}), 400
    return response

@app.route('/sound', methods=['POST'])
def sound():
    global direction, light_status, is_light_blink, light_thread
    data = request.get_json()

    if 'cmd' in data:
        cmd = data['cmd'] 
        value = data['value']

        match cmd:
            case 'music':
                music.on()
                time.sleep(0.1)
                music.off()
                response= jsonify({'code': 0,'direction':direction,'light_status':light_status, 'message': '播放音樂'}), 200
            case 'horn':
                horn.on()
                time.sleep(0.1)
                horn.off()
                response= jsonify({'code': 0,'direction':direction,'light_status':light_status, 'message': '喇叭'}), 200
    else:
        response= jsonify({'code': 400, 'message': '缺少參數'}), 400
    return response

@app.route('/status', methods=['GET'])
def get_status():
    response= jsonify({'code': 0,'direction':direction,'light_status':light_status, 'message': ''}), 200
    return response

@app.after_request
def log_request(response):
    try:
        data = request.get_json()
        print("Request:" ,data)
    except:
        pass
    return response

def turn_on_all_light():
    global light_status, is_light_blink, light_thread
    is_light_blink = False

    if light_thread is not None:
        light_thread.join()

    light_1.on()
    light_2.on()
    light_3.on()
    light_4.on()

def turn_off_all_light():
    global light_status, is_light_blink, light_thread
    is_light_blink = False

    if light_thread is not None:
        light_thread.join()

    light_1.off()
    light_2.off()
    light_3.off()
    light_4.off()

def turn_left_light():
    global is_light_blink
    while is_light_blink:
        light_1.on()
        light_3.on()
        time.sleep(0.5)
        light_1.off()
        light_3.off()
        time.sleep(0.5)

def turn_right_light():
    global is_light_blink
    while is_light_blink:
        light_2.on()
        light_4.on()
        time.sleep(0.5)
        light_2.off()
        light_4.off()
        time.sleep(0.5)

def parking_light():
    global is_light_blink
    while is_light_blink:
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
