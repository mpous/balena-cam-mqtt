import asyncio, json, os, cv2, platform, subprocess, sys
from time import sleep
import time
import base64
from aiohttp import web
from av import VideoFrame
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack, RTCIceServer, RTCConfiguration
from aiohttp_basicauth import BasicAuthMiddleware
from paho.mqtt import client as mqtt_client

class CameraDevice():
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        ret, frame = self.cap.read()
        if not ret:
            print('Failed to open default camera. Exiting...')
            sys.exit()
        self.cap.set(3, 640)
        self.cap.set(4, 480)

    def rotate(self, frame):
        if flip:
            (h, w) = frame.shape[:2]
            center = (w/2, h/2)
            M = cv2.getRotationMatrix2D(center, 180, 1.0)
            frame = cv2.warpAffine(frame, M, (w, h))
        return frame

    async def get_latest_frame(self):
        ret, frame = self.cap.read()
        await asyncio.sleep(0)
        return self.rotate(frame)

    async def get_jpeg_frame(self):
        encode_param = (int(cv2.IMWRITE_JPEG_QUALITY), 90)
        frame = await self.get_latest_frame()
        frame, encimg = cv2.imencode('.jpg', frame, encode_param)        

        return encimg.tostring()

class PeerConnectionFactory():
    def __init__(self):
        self.config = {'sdpSemantics': 'unified-plan'}
        self.STUN_SERVER = None
        self.TURN_SERVER = None
        self.TURN_USERNAME = None
        self.TURN_PASSWORD = None
        if all(k in os.environ for k in ('STUN_SERVER', 'TURN_SERVER', 'TURN_USERNAME', 'TURN_PASSWORD')):
            print('WebRTC connections will use your custom ICE Servers (STUN / TURN).')
            self.STUN_SERVER = os.environ['STUN_SERVER']
            self.TURN_SERVER = os.environ['TURN_SERVER']
            self.TURN_USERNAME = os.environ['TURN_USERNAME']
            self.TURN_PASSWORD = os.environ['TURN_PASSWORD']
            iceServers = [
                {
                    'urls': self.STUN_SERVER
                },
                {
                    'urls': self.TURN_SERVER,
                    'credential': self.TURN_PASSWORD,
                    'username': self.TURN_USERNAME
                }
            ]
            self.config['iceServers'] = iceServers

    def create_peer_connection(self):
        if self.TURN_SERVER is not None:
            iceServers = []
            iceServers.append(RTCIceServer(self.STUN_SERVER))
            iceServers.append(RTCIceServer(self.TURN_SERVER, username=self.TURN_USERNAME, credential=self.TURN_PASSWORD))
            return RTCPeerConnection(RTCConfiguration(iceServers))
        return RTCPeerConnection()

    def get_ice_config(self):
        return json.dumps(self.config)


class RTCVideoStream(VideoStreamTrack):
    def __init__(self, camera_device):
        super().__init__()
        self.camera_device = camera_device
        self.data_bgr = None

    async def recv(self):
        self.data_bgr = await self.camera_device.get_latest_frame()
        frame = VideoFrame.from_ndarray(self.data_bgr, format='bgr24')
        pts, time_base = await self.next_timestamp()
        frame.pts = pts
        frame.time_base = time_base
        return frame

async def index(request):
    content = open(os.path.join(ROOT, 'client/index.html'), 'r').read()
    return web.Response(content_type='text/html', text=content)

async def stylesheet(request):
    content = open(os.path.join(ROOT, 'client/style.css'), 'r').read()
    return web.Response(content_type='text/css', text=content)

async def javascript(request):
    content = open(os.path.join(ROOT, 'client/client.js'), 'r').read()
    return web.Response(content_type='application/javascript', text=content)

async def balena(request):
    content = open(os.path.join(ROOT, 'client/balena-cam.svg'), 'r').read()
    return web.Response(content_type='image/svg+xml', text=content)

async def balena_logo(request):
    content = open(os.path.join(ROOT, 'client/balena-logo.svg'), 'r').read()
    return web.Response(content_type='image/svg+xml', text=content)

async def favicon(request):
    return web.FileResponse(os.path.join(ROOT, 'client/favicon.png'))

async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(
        sdp=params['sdp'],
        type=params['type'])
    pc = pc_factory.create_peer_connection()
    pcs.add(pc)
    # Add local media
    local_video = RTCVideoStream(camera_device)
    pc.addTrack(local_video)
    @pc.on('iceconnectionstatechange')
    async def on_iceconnectionstatechange():
        if pc.iceConnectionState == 'failed':
            await pc.close()
            pcs.discard(pc)
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    return web.Response(
        content_type='application/json',
        text=json.dumps({
            'sdp': pc.localDescription.sdp,
            'type': pc.localDescription.type
        }))

async def mjpeg_handler(request):
    boundary = "frame"
    response = web.StreamResponse(status=200, reason='OK', headers={
        'Content-Type': 'multipart/x-mixed-replace; '
                        'boundary=%s' % boundary,
    })
    await response.prepare(request)
    while True:
        data = await camera_device.get_jpeg_frame()
        await asyncio.sleep(0.2) # this means that the maximum FPS is 5
        
        
        await response.write(
            '--{}\r\n'.format(boundary).encode('utf-8'))
        await response.write(b'Content-Type: image/jpeg\r\n')
        await response.write('Content-Length: {}\r\n'.format(
                len(data)).encode('utf-8'))
        await response.write(b"\r\n")
        await response.write(data)
        await response.write(b"\r\n")
    return response


async def config(request):
    return web.Response(
        content_type='application/json',
        text=pc_factory.get_ice_config()
    )

async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)

def checkDeviceReadiness():
    if not os.path.exists('/dev/video0') and platform.system() == 'Linux':
        print('Video device is not ready')
        print('Trying to load bcm2835-v4l2 driver...')
        #os.system('bash -c "modprobe bcm2835-v4l2"')
        try:
            subprocess.run(['modprobe', 'bcm2835-v4l2'], check=True)
        except FileNotFoundError:
            print("Cannot modeprobe bcm2835-v4l2, not a Raspberry-Pi ?")
        except subprocess.CalledProcessError as err:
            print(err)
        sleep(1)
        sys.exit()
    else:
        print('Video device is ready')


def capture_image():
    # Start the webcam capture
    print("Start the webcam capture...")

    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        # Convert the image to JPEG format
        print("Convert the image to JPEG format")
        ret, buffer = cv2.imencode('.jpg', frame)

        scale_percent = 50 # percent of original size
        #width = int(img.shape[1] * scale_percent / 100)
        #height = int(img.shape[0] * scale_percent / 100)
        #dim = (width, height)
        
        # resize image
        resized = cv2.resize(ret, (200,200), interpolation = cv2.INTER_AREA)

        if ret:
            # Return the image as a bytes object
            print("Return the image as a bytes object")
            cap.release()
            buffer_bytes = buffer.tobytes()
            buffer_b64 = base64.b64encode(buffer_bytes)
            return buffer_b64
    else:
        print('Failed to open default camera. Exiting...')

    cap.release()
    return None


def send_mqtt_message(broker, port, topic, image):
    # Generate a random client ID
    print("Send MQTT image...")
    print(broker)
    print(port)
    print(topic)

    client_id = f'python-mqtt-{int(time.time())}'
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    # Set Connecting Client ID
    print(client_id)
    print(broker)
    print(port)
    print(topic)
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, 1883)
    client.loop_start()

    # Publish the image to the MQTT broker
    result = client.publish(topic, image)

    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Sent image to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")

    client.loop_stop()



if __name__ == '__main__':

    # MQTT broker definition
    print("Setting up the MQTT broker")
    broker = os.environ['mqtt_broker']
    port = os.environ['mqtt_port']
    topic = os.environ['mqtt_topic']
    if topic == "":
        topic='balena/site/area/line/cell/camera/raw'

    #print("checkDeviceReadiness")
    #checkDeviceReadiness()

    ROOT = os.path.dirname(__file__)
    #pcs = set()
    #print("CameraDevice")
    #camera_device = CameraDevice()

    flip = False
    try:
        if os.environ['rotation'] == '1':
            flip = True
    except:
        pass
    
    # mqtt
    while(True):
        # Capture the image
        print("Trying to Capture the image...")
        image = capture_image()
        if image is not None:
            # Send the image to the MQTT broker
            send_mqtt_message(broker, port, topic, image)
        else:
            print("Failed to capture the image.")
        
        sleep(2)

    ##

    # auth = []
    # if 'username' in os.environ and 'password' in os.environ:
    #     print('\n#############################################################')
    #     print('Authorization is enabled.')
    #     print('Your balenaCam is password protected.')
    #     print('#############################################################\n')
    #     auth.append(BasicAuthMiddleware(username = os.environ['username'], password = os.environ['password']))
    # else:
    #     print('\n#############################################################')
    #     print('Authorization is disabled.')
    #     print('Anyone can access your balenaCam, using the device\'s URL!')
    #     print('Set the username and password environment variables \nto enable authorization.')
    #     print('For more info visit: \nhttps://github.com/balena-io-playground/balena-cam')
    #     print('#############################################################\n')
    
    # Factory to create peerConnections depending on the iceServers set by user
    pc_factory = PeerConnectionFactory()

    app = web.Application(middlewares=auth)
    app.on_shutdown.append(on_shutdown)
    app.router.add_get('/', index)
    app.router.add_get('/favicon.png', favicon)
    app.router.add_get('/balena-logo.svg', balena_logo)
    app.router.add_get('/balena-cam.svg', balena)
    app.router.add_get('/client.js', javascript)
    app.router.add_get('/style.css', stylesheet)
    app.router.add_post('/offer', offer)
    app.router.add_get('/mjpeg', mjpeg_handler)
    app.router.add_get('/ice-config', config)
    web.run_app(app, port=80)
