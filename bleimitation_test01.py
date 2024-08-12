# ==========================================================================
# 导入Python库, 设置环境路径, 设置文件路径
# ==========================================================================
import cv2
from utils.setCamera import SetCamera

# from utils.face_op_img import FaceMeshDetector, HeadPose
from utils.faceCapture import FaceMeshDetector, HeadPose
from model.bsToServos import initFaceRobot, handle_data

from utils.servo_v2.HeadCtrlKit import HeadCtrl
from utils.servo_v2.MouthCtrlKit import MouthCtrl
import numpy as np



def mask_image(image, mask_side_length=250):

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



# ==========================================================================
# 程序入口
# ==========================================================================
if __name__ == "__main__":

    # setcamera = SetCamera(2)                # 摄像头类实例
    facemeshdetector = FaceMeshDetector()  # 关键点检测类实例
    headpose = HeadPose()                  # 头部姿态类实例

    servo_flag = False# True
    if servo_flag:
        port_head = "/dev/ttyACM1"
        port_mouth = "/dev/ttyACM0"
        headCtrl = HeadCtrl(port_head)  # 921600
        mouthCtrl = MouthCtrl(port_mouth)  # 921600

        initFaceRobot(servo_flag, headCtrl, mouthCtrl)

    cap = cv2.VideoCapture(2)
    count = 0

    while True:
        count = count +1
        # 运行摄像头，读入图片
        # image, image_flag = setcamera.start_camera(3)
        image_flag, image = cap.read()

        image = cv2.flip(image, 1)

        # --------------------------------------------------
        masked_image, mask = mask_image(image) # 掩码后的图片，掩码
        # cv2.imshow('Original Image', image)
        cv2.imshow('Masked Image', masked_image)
        cv2.waitKey(1)
        # --------------------------------------------------

        
        facemeshdetector.update(masked_image, image_flag)

        lm, bs, rm = facemeshdetector.get_results()



        # 如果模型推理成功，则滤波、计算头部位姿
        if lm is not None and bs is not None and rm is not None:

            rpy = headpose.pose_det(rm=rm)
            print(rpy)

            # 可视化 检测结果

            # facemeshdetector.visualize_results()

            # 如果仿真人头连接成功, 则驱动仿真人头硬件
            # handle_data(servo_flag, bs, rpy, headCtrl, mouthCtrl)
        else:
            print("请移动到摄像头中心 体验表情模仿功能")
            # 回正
            

    
    setcamera.stop_camera()  # 关闭摄像头
