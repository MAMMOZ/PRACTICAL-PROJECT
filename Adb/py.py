import subprocess
import time
import cv2
import numpy as np
import ctypes
import logging
from colorlog import ColoredFormatter
import os
import subprocess
import concurrent.futures

import requests
import socket
import json
from PIL import Image

file_path = 'config.json'

with open(file_path, 'r') as file:
    config = json.load(file)

hostname = socket.gethostname()



LOG_LEVEL = logging.DEBUG
LOGFORMAT = "  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"
logging.root.setLevel(LOG_LEVEL)
formatter = ColoredFormatter(LOGFORMAT)
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)
log = logging.getLogger('pythonConfig')
log.setLevel(LOG_LEVEL)
log.addHandler(stream)

def set_window_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)


class ADeAuto():
    def __init__(self, emulator):
        self.emulator = emulator

    def capture_screen(self, name):
        os.system(f'adb -s {self.emulator} exec-out screencap -p > {name}.png')

        img = Image.open(f'{name}.png')

        # crop_area = (367, 422, 601, 444)
        crop_area = (367, 444, 601, 466)

        cropped_img = img.crop(crop_area)

        cropped_img.save(f'{name}_cropped.png')
        print(f'{name}cap')

        with open(f'{name}_cropped.png', 'rb') as img_file:
            files = {'file': (f'{name}_cropped.png', img_file, 'image/png')}
            response = requests.post("http://127.0.0.1:8000/detectImage", files=files)

        print(f'API response: {response.status_code}, {response.text}')

        return response.text


    def click(self, x, y):
        os.system(f'adb -s {self.emulator} shell input tap {x} {y}')

    def slide(self, x1, y1, x2, y2, delay):
        os.system(f'adb -s {self.emulator} shell input touchscreen swipe {x1} {y1} {x2} {y2} {delay}')

    def checkRoblox(self, placeId, vip_server_link):
        cmd = f'adb -s {self.emulator} shell ps | findstr "com.roblox.client"'
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if "com.roblox.client" in result.stdout:
            return True
        else:
            if vip_server_link != "":
                run = f'adb -s {self.emulator} shell am start -a android.intent.action.VIEW -d "{vip_server_link}" -n com.roblox.client/.ActivityProtocolLaunch'
            else:
                run = f'adb -s {self.emulator} shell am start -n com.roblox.client/.ActivityProtocolLaunch -d "roblox://experiences/start?placeId={placeId}"'

            subprocess.run(run, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            log.info(f"Start Roblox {self.emulator}")
            return False
    
    def runRoblox(self, placeId, vip_server_link):
        if vip_server_link != "":
            run = f'adb -s {self.emulator} shell am start --activity-clear-top -a android.intent.action.VIEW -d "{vip_server_link}" -n com.roblox.client/.ActivityProtocolLaunch'
        else:
            run = f'adb -s {self.emulator} shell am start "roblox://experiences/start?placeId={placeId}"'

        subprocess.run(run, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        log.info(f"Start Roblox {self.emulator}")
        return False
        
    def closeRoblox(self):
        cmd = f'adb -s {self.emulator} shell am force-stop "com.roblox.client"'
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)


def get_connected_devices():
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, check=True)
        output_lines = result.stdout.split('\n')
        devices = [line.split('\t')[0] for line in output_lines[1:] if line.strip() and 'device' in line]
        return devices
    except subprocess.CalledProcessError as adb_error:
        log.error(f"ADB Command Failure: {adb_error}")
        log.info("Trying to start ADB server...")
        try:
            subprocess.run(['adb', 'start-server'], check=True)
            log.info("ADB server started successfully.")
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, check=True)
            output_lines = result.stdout.split('\n')
            devices = [line.split('\t')[0] for line in output_lines[1:] if line.strip() and 'device' in line]
            return devices
        except subprocess.CalledProcessError as start_error:
            log.error(f"Error starting ADB server: {start_error}")
            return []
    except Exception as e:
        log.error(f"Error: {e}")
        return []
    

def sendServer(text):
    data = {
        "gem":text,
        "gold":""
    }
    response = requests.post("https://cm0obybgw0000mnbsdcdfu7qi.iservkmitl.tech/addlog",json=data)

    print(response.text)
    

def process_device(device):
    placeId = "17017769292"
    vipserver = ""

    d = ADeAuto(device)

    # d.checkRoblox(placeId,vipserver)
    
    # time.sleep(40)
    
    text = d.capture_screen(device.split(":")[1])

    print(text)

    time.sleep(40)

    # sendServer(text)

    # time.sleep(10)
    

def aaa():
    connected_devices = get_connected_devices()
    print(connected_devices)
    set_window_title(f"{len(connected_devices)}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        executor.map(process_device, connected_devices)


while True:
    try:
        aaa()
    except:
        print("error")
        aaa()