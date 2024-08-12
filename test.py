import cv2
from utils.setCamera import SetCamera

# from utils.face_op_img import FaceMeshDetector, HeadPose
from utils.faceCapture import FaceMeshDetector, HeadPose
from model.bsToServos import initFaceRobot, handle_data

from utils.servo_v2.HeadCtrlKit import HeadCtrl
from utils.servo_v2.MouthCtrlKit import MouthCtrl
from utils.servo_v2.facial_plan_ctrl_v2 import Servos_Ctrl,Servos
from utils.facedetect import FacePoseDetector

from bleimitation_test01 import mask_image


if __name__ == '__main__':
    # initFaceRobot()
    sc = SetCamera(0)
    zeroServos = Servos()
    zeroServos.head_steps(50)
    servosCtrl = Servos_Ctrl()



    facemeshdetector = FaceMeshDetector()
    headpose = HeadPose()
    sc = SetCamera(0)
    fp = FacePoseDetector()

    servo_flag = True

    if servo_flag:
        port_head = "COM10"
        port_mouth = "COM9"
        headCtrl = HeadCtrl(port_head)  # 921600
        mouthCtrl = MouthCtrl(port_mouth)  # 921600

        initFaceRobot(servo_flag, headCtrl, mouthCtrl)

    servosCtrl.plan_and_pub(zeroServos,headCtrl=headCtrl,mouthCtrl=mouthCtrl,cycles=1)

    image,image_flag = sc.read()
    while True:
        if image_flag:                         # 如果摄像头成功采集图片, 则执行后续操作
            masked_image, mask = mask_image(image) # 掩码后的图片，掩码
            cv2.imshow("qwer",masked_image)
            cv2.waitKey(1)
            if fp.initialize(masked_image) == True:               # 调用关键点检测程序
                break


    try:
        while True:
            image, image_flag = sc.read()  # 启动摄像头
            masked_image, mask = mask_image(image) # 掩码后的图片，掩码
            if image_flag:                         # 如果摄像头成功采集图片, 则执行后续操作
                if fp.process_frame(masked_image):
                    facemeshdetector.update(masked_image, image_flag)       # 调用关键点检测程序
                    lm, bs, rm = facemeshdetector.get_results()   # 获取关键点检测结果

                    # 如果模型推理成功，则滤波、计算头部位姿
                    if lm is not None and bs is not None and rm is not None:
                        rpy = headpose.pose_det(rm=rm)
                        # 可视化检测结果
                        facemeshdetector.visualize_results()
                        # 如果仿真人头连接成功, 则驱动仿真人头硬件
                        temp_servos = Servos()
                        servosCtrl.plan_and_pub(handle_data(servo_flag, bs, rpy, temp_servos),headCtrl,mouthCtrl,1)
                        facemeshdetector.visualize_results()
                        print("1111111111")
                    else:
                        servosCtrl.plan_and_pub(zeroServos,headCtrl=headCtrl,mouthCtrl=mouthCtrl,cycles=1)
                else:
                    servosCtrl.plan_and_pub(zeroServos,headCtrl=headCtrl,mouthCtrl=mouthCtrl,cycles=1)
                    # break
    finally:
        sc.stop_camera()
    