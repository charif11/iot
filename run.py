import eventlet
from flask import Flask, redirect, url_for, render_template
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
import json

app = Flask(__name__)
socketio = SocketIO(app)
eventlet.monkey_patch()
bootstrap = Bootstrap(app)

app.secret_key = 'it003'
app.config['SECRET'] = 'it003'
app.config['TEMPLATES_AUTO_RELOAD'] = True

app.config['MQTT_BROKER_URL'] = 'broker.hivemq.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_CLIENT_ID'] = 'webapp003'
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_REFRESH_TIME'] = 1.0
mqtt = Mqtt(app)

@socketio.on('publish')
def publish(json_str):
    data = json.loads(json_str)
    mqtt.publish(data['topic'], data['message'], data['qos'])  

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print("---------------")
    print("Mqtt Connect")
    print("---------------")
    client.subscribe('esp/tmp')
    client.subscribe('esp/hum')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    topic = message.topic
    data = message.payload.decode()
    if topic == 'esp/tmp':
        print("Received temperature data:", data)
        socketio.emit('tmp', data=data)
    elif topic == 'esp/hum':
        print("Received humidity data:", data)
        socketio.emit('hum', data=data)

@app.route('/')
def Home():
    return redirect(url_for('Index'))

@app.route('/Home')
def Index():
    return render_template("index.html")

@app.route('/Page2')
def Page2():
    return render_template("page2.html")

if __name__ == '__main__':
    socketio.run(app, port=8000)
