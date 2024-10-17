
import platform
import socket

from utils.servo.HeadCtrlKit_v2 import HeadCtrl
from utils.servo.MouthCtrlKit_v2 import MouthCtrl
from utils.det_face_livelink import PyLiveLinkFace
from utils.Obtain_61bs import get_61_blendshape

from model.bs61_servo import manual_model

UDP_PORT = 8000
IP_ADDRESS = "192.168.50.151"
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


os_type = platform.system()

if os_type == "Linux":
    port_head = '/dev/ttyACM1'
    port_mouth = '/dev/ttyACM0'
elif os_type == "Darwin":
    port_head = 'serialxxxxx'
    port_mouth = 'serialxxxxx'
elif os_type == "Windows":
    port_head = 'COM7'
    port_mouth = 'COM8'
else:
    print("Unsupported OS, Please check your PC system")

headCtrl = HeadCtrl(port_head)    # 921600
mouthCtrl = MouthCtrl(port_mouth) # 921600


def send_control_msgs(head_list, mouth_list):
    try:
        headCtrl.setmsg(head_list)
        mouthCtrl.setmsg(mouth_list)
        headCtrl.send()
        mouthCtrl.send()
    except Exception as e:
        print(f"Failed to send control messages: {e}")



def main():
    try:
        s.bind((IP_ADDRESS, UDP_PORT))

        while True: 
            data, addr = s.recvfrom(1024)
            success, live_link_face = PyLiveLinkFace.decode(data)
            if success:
                try:
                    bs_dict = get_61_blendshape(live_link_face)
                    head_list, mouth_list = manual_model(bs_dict)
                    
                    send_control_msgs(head_list, mouth_list)

                except Exception as e:
                    print(f"Failed to process data: {e}")

    except KeyboardInterrupt:
        print("Program interrupted by user.")

    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally: 
        s.close()
        headCtrl.close()
        mouthCtrl.close()
  
if __name__ == '__main__':
    main()
