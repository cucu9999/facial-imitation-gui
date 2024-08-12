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


# ==========================================================================
# 程序入口
# ==========================================================================
if __name__ == "__main__":

    setcamera = SetCamera(2)                # 摄像头类实例
    facemeshdetector = FaceMeshDetector()  # 关键点检测类实例
    headpose = HeadPose()                  # 头部姿态类实例

    servo_flag = True
    if servo_flag:
        port_head = "/dev/ttyACM1"
        port_mouth = "/dev/ttyACM0"
        headCtrl = HeadCtrl(port_head)  # 921600
        mouthCtrl = MouthCtrl(port_mouth)  # 921600

        initFaceRobot(servo_flag, headCtrl, mouthCtrl)

    while True:

        # 运行摄像头，读入图片
        image, image_flag = setcamera.start_camera(2)
        image = cv2.flip(image, 1)

        # 如果摄像头成功采集图片, 则图像输入模型进行推理
        facemeshdetector.update(image, image_flag)
        lm, bs, rm = facemeshdetector.get_results()

        # 如果模型推理成功，则滤波、计算头部位姿
        if lm is not None and bs is not None and rm is not None:
            rpy = headpose.pose_det(rm=rm)

            # 可视化检测结果
            facemeshdetector.visualize_results()

            # 如果仿真人头连接成功, 则驱动仿真人头硬件
            handle_data(servo_flag, bs, rpy, headCtrl, mouthCtrl)
    
    setcamera.stop_camera()  # 关闭摄像头
