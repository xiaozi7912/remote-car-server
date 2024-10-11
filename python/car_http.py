from flask import Flask, request, jsonify
from gpiozero import OutputDevice

app = Flask(__name__)

accelertor = OutputDevice(17)
light = OutputDevice(27)

@app.route('/start', methods=['POST'])
def start_motor():
    accelertor.on() 
    return jsonify({'status': 'success', 'message': '馬達啟動'}), 200

@app.route('/stop', methods=['POST'])
def stop_motor():
    accelertor.off() 
    return jsonify({'status': 'success', 'message': '馬達停止'}), 200

@app.route('/light', methods=['POST'])
def switch_light():
    data = request.get_json() 
    if 'on' in data:
        on = data['on'] 
        if on:
            light.on()
            return jsonify({'status': 'success', 'message': '燈已開啟'}), 200
        else:
            light.off()
            return jsonify({'status': 'success', 'message': '燈已關閉'}), 200
    else:
        return jsonify({'status': 'error', 'message': '缺少參數'}), 400

@app.route('/status', methods=['GET'])
def get_status():
    status = 'on' if accelertor.is_active else 'off'
    return jsonify({'status': status}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
