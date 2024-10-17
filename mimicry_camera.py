
import platform
import socket

from utils.servo.HeadCtrlKit_v2 import HeadCtrl
from utils.servo.MouthCtrlKit_v2 import MouthCtrl

from utils.config_cam import ConfigCamera

from utils.Obtain_51bs import Obtain_head 
from model.bs51_servo import manual_model   
import time
import cv2

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

camera = ConfigCamera(input_source=0, width=640, height=480)
# camera = ConfigCamera(input_source="/media/2T/yongtong/Rena/RenaBlender/demo.mp4", width=640, height=480)

head_obtainer = Obtain_head()


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
        while True: 
            image, success = camera.start_camera()
            image = cv2.flip(image, -1)
            cv2.imshow("camera", image)
            cv2.waitKey(1)

            if success:
                try:

                    bs_dict, rpy_angles = head_obtainer.get_51_blendshape_rpy(image)
                    rpy_angles= [0,0,0]

                    head_list, mouth_list = manual_model(bs_dict, rpy_angles)

                    # stable_list = [1, 2, 6, 7]
                    # for i in stable_list:
                    #     head_list[i] = 0.5
                    
                    send_control_msgs(head_list, mouth_list)

                except Exception as e:
                    print(f"Failed to process data: {e}")

    except KeyboardInterrupt:
        print("Program interrupted by user.")

    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally: 
        camera.stop_camera()
        headCtrl.close()
        mouthCtrl.close()

if __name__ == '__main__':
    main()
