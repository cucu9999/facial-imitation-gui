import cv2
from utils.setCamera import SetCamera

# from utils.face_op_img import FaceMeshDetector, HeadPose
from utils.faceCapture import FaceMeshDetector, HeadPose
from model.bsToServos import initFaceRobot, handle_data

from utils.servo_v2.HeadCtrlKit import HeadCtrl
from utils.servo_v2.MouthCtrlKit import MouthCtrl
from utils.servo_v2.facial_plan_ctrl_v2 import Servos_Ctrl,Servos
from utils.facedetect import FacePoseDetector
import numpy as np
import platform


def mask_image(image, mask_side_length=400):

    height, width, _ = image.shape
    
    center_x, center_y = width // 2, height // 2
    
    # Calculate the top-left and bottom-right coordinates of the rectangle
    top_left_x = center_x - mask_side_length // 2
    top_left_y = center_y - mask_side_length // 2
    bottom_right_x = center_x + mask_side_length // 2
    bottom_right_y = center_y + mask_side_length // 2
    
    # Create a mask of the same size as the image, filled with zeros (black)
    mask = np.zeros_like(image)
    
    # Draw a white filled rectangle on the mask
    mask = cv2.rectangle(mask, 
                         (top_left_x, top_left_y), 
                         (bottom_right_x, bottom_right_y), 
                         (255, 255, 255), 
                         -1)
    
    # Apply the mask to the original image using bitwise_and
    masked_image = cv2.bitwise_and(image, mask)
    
    return masked_image, mask


if __name__ == '__main__':

    os_type = platform.system()
    
    if os_type == "Linux":
        port_head = '/dev/ttyACM1'
        port_mouth = '/dev/ttyACM0'
    elif os_type == "Darwin":
        port_head = '/dev/ttyACM1'
        port_mouth = '/dev/ttyACM0'
    elif os_type == "Windows":
        port_head = 'COM10'
        port_mouth = 'COM9'
    else:
        print("Unsupported OS, Please check your PC system")

    cap = cv2.VideoCapture(0)
    zeroServos = Servos()
    zeroServos.head_steps(50)
    servosCtrl = Servos_Ctrl()


    facemeshdetector = FaceMeshDetector()
    headpose = HeadPose()
    fp = FacePoseDetector()

    servo_flag = True

    if servo_flag:
        headCtrl = HeadCtrl(port_head)  # 921600
        mouthCtrl = MouthCtrl(port_mouth)  # 921600
        initFaceRobot(servo_flag, headCtrl, mouthCtrl)


    servosCtrl.plan_and_pub(zeroServos,headCtrl=headCtrl,mouthCtrl=mouthCtrl,cycles=1)

    while True:
        image_flag, image = cap.read()

        if image_flag:                         # 如果摄像头成功采集图片, 则执行后续操作
            masked_image, mask = mask_image(image) # 掩码后的图片，掩码
            cv2.imshow("qwer", masked_image)
            cv2.waitKey(1)
            if fp.initialize(masked_image) == True:
                cv2.destroyAllWindows()
                break

    # count = 0
    # ii = 0
    # import time
    # while True:
    #     t1 = time.time()
    #     image_flag, image = cap.read()
    #     masked_image, mask = mask_image(image) # 掩码后的图片，掩码
    #     if image_flag:                         # 如果摄像头成功采集图片, 则执行后续操作
    #         if fp.process_frame(masked_image):
    #             facemeshdetector.update(masked_image, image_flag)       # 调用关键点检测程序
    #             lm, bs, rm = facemeshdetector.get_results()   # 获取关键点检测结果

    #             # 如果模型推理成功，则滤波、计算头部位姿
    #             if lm is not None and bs is not None and rm is not None:
    #                 rpy = headpose.pose_det(rm=rm)

    #                 # facemeshdetector.visualize_results()
    #                 temp_servos = Servos()
    #                 servos = handle_data(servo_flag, bs, rpy, temp_servos)
    #                 if count == 0:
    #                     servos.head_steps(20)
    #                     count += 1

    #                 elif count == 1:
    #                     servos.head_steps(1)
    #                 servosCtrl.plan_and_pub(servos, headCtrl, mouthCtrl, cycles=1)

    #             else:
    #                 count = 0
    #                 print("head not found")
    #                 servosCtrl.plan_and_pub(zeroServos,headCtrl=headCtrl,mouthCtrl=mouthCtrl,cycles=1)
    #         else:
    #             count = 0
    #             print("move too fast")
    #             servosCtrl.plan_and_pub(zeroServos,headCtrl=headCtrl,mouthCtrl=mouthCtrl, cycles=1)
    #     t2 = time.time()
    #     # print(f"帧率为{1/(t2-t1)}")

    try:
        count = 0
        ii = 0
        import time
        while True:
            t1 = time.time()
            image_flag, image = cap.read()
            masked_image, mask = mask_image(image) # 掩码后的图片，掩码
            if image_flag:                         # 如果摄像头成功采集图片, 则执行后续操作
                
                facemeshdetector.update(masked_image, image_flag)       # 调用关键点检测程序
                lm, bs, rm = facemeshdetector.get_results()   # 获取关键点检测结果
                # 如果模型推理成功，则滤波、计算头部位姿
                if lm is not None and bs is not None and rm is not None:
                    if fp.process_frame(masked_image):
                        rpy = headpose.pose_det(rm=rm)

                        # facemeshdetector.visualize_results()
                        temp_servos = Servos()
                        servos = handle_data(servo_flag, bs, rpy, temp_servos)
                        if count == 0:
                            servos.head_steps(20)
                            count += 1
                        elif count == 1:
                            servos.head_steps(1)
                        servosCtrl.plan_and_pub(servos, headCtrl, mouthCtrl, cycles=1)
                    else:
                        count = 0
                        print("move too fast")
                        servosCtrl.plan_and_pub(zeroServos,headCtrl=headCtrl,mouthCtrl=mouthCtrl, cycles=1)

                else:
                    count = 0
                    print("head not found")
                    servosCtrl.plan_and_pub(zeroServos,headCtrl=headCtrl,mouthCtrl=mouthCtrl,cycles=1)
                
            t2 = time.time()
            print(f"帧率为{1/(t2-t1)}")

    except Exception as e:
        print("错误：",e)

    finally:
        servosCtrl.plan_and_pub(zeroServos,headCtrl=headCtrl,mouthCtrl=mouthCtrl,cycles=1)
        print("----------------end---------------")
        cap.release()
    