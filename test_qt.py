import sys, os
sys.path.append(os.getcwd())

import numpy as np
import platform
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
import threading
import time,datetime
import cv2
from PyQt5.QtGui import QImage, QPixmap
from utils.setCamera import SetCamera
from utils.faceCapture import FaceMeshDetector, HeadPose
from utils.servo_v2.HeadCtrlKit import HeadCtrl
from utils.servo_v2.MouthCtrlKit import MouthCtrl
from utils.servo_v2.facial_plan_ctrl_v2 import Servos_Ctrl, Servos
from utils.facedetect import FacePoseDetector
from qt_01 import Ui_MainWindow
from model.bsToServos import initFaceRobot, handle_data


def mask_image(image, mask_side_length=400):
    height, width, _ = image.shape
    center_x, center_y = width // 2, height // 2

    top_left_x = center_x - mask_side_length // 2
    top_left_y = center_y - mask_side_length // 2
    bottom_right_x = center_x + mask_side_length // 2
    bottom_right_y = center_y + mask_side_length // 2

    mask = np.zeros_like(image)
    
    mask = cv2.rectangle(mask, 
                         (top_left_x, top_left_y), 
                         (bottom_right_x, bottom_right_y), 
                         (255, 255, 255), 
                         -1)
    
    masked_image = cv2.bitwise_and(image, mask)
    
    return masked_image, mask

class MyMainForm(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)
        self.on_off_state = False
        ################################# MMMMMMMMMMMMMMMMMMMMM 初始设置
        self.os_type = platform.system()
        if self.os_type == "Linux":
            self.port_head = '/dev/ttyACM1'
            self.port_mouth = '/dev/ttyACM0'
        elif self.os_type == "Darwin":
            self.port_head = '/dev/ttyACM1'
            self.port_mouth = '/dev/ttyACM0'
        elif self.os_type == "Windows":
            self.port_head = 'COM8'
            self.port_mouth = 'COM7'
        else:
            print("Unsupported OS, Please check your PC system")
        ################################# WWWWWWWWWWWWWWWWWWWWW

        ################################# MMMMMMMMMMMMMMMMMMMMM摄像头设置
        # self.cap = cv2.VideoCapture(2)
        self.cap = cv2.VideoCapture(2)

        self.zeroServos = Servos()
        self.zeroServos.head_steps(50)
        self.servosCtrl = Servos_Ctrl()
        self.facemeshdetector = FaceMeshDetector()
        self.headpose = HeadPose()
        self.fp = FacePoseDetector()

        self.servo_flag = True

        if self.servo_flag:
            self.headCtrl = HeadCtrl(self.port_head)  # 921600
            self.mouthCtrl = MouthCtrl(self.port_mouth)  # 921600
            initFaceRobot(self.servo_flag, self.headCtrl, self.mouthCtrl)
        self.servosCtrl.plan_and_pub(self.zeroServos,headCtrl=self.headCtrl,mouthCtrl=self.mouthCtrl,cycles=1)

        #################### 启动摄像头
        # 设置定时器，每30ms调用一次 update_frame 函数
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(100)
        ################################# WWWWWWWWWWWWWWWWWWWWW

        self.checkBox_main.stateChanged.connect(self.on_off_change)
        self.rena_thread =None
        self.rena_thread = threading.Thread(target=self.Facial_Expression_Imitation)
        self.rena_thread.start()


    def update_frame(self):
        # 从摄像头读取一帧
        ret, frame = self.cap.read()

        if ret:
            # try :
                # 将 BGR 格式转换为 RGB 格式
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # # 使用cv2.resize进行降采样            
                frame = cv2.resize(frame, (self.label_video_origin.size().width(),  self.label_video_origin.size().height()), interpolation=cv2.INTER_LINEAR)

                # 获取图像大小并创建 QImage
                h, w, ch = frame.shape
                bytes_per_line = ch * w         # h,w    (480, 640)
                qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

                # 将 QImage 显示在 QLabel 中
                self.label_video_origin.setPixmap(QPixmap.fromImage(qimg))



    def on_off_change(self) :
        if self.checkBox_main.isChecked() == True :
            self.on_off_state = True

        if self.checkBox_main.isChecked() == False :
            self.on_off_state = False

    def Facial_Expression_Imitation(self) :

            while True:
                image_flag, image = self.cap.read()

                if image_flag:                         # 如果摄像头成功采集图片, 则执行后续操作
                    masked_image, mask = mask_image(image) # 掩码后的图片，掩码
                    # cv2.imshow("qwer", masked_image)   # cv 显示
                    # cv2.waitKey(1)
                    if self.fp.initialize(masked_image) == True:
                        # cv2.destroyAllWindows()
                        break

            try:
            # if True :
                count = 0
                ii = 0
                while True:
                    if self.on_off_state :
                        t1 = time.time()
                        image_flag, image = self.cap.read()
                        masked_image, mask = mask_image(image) # 掩码后的图片，掩码
                        if image_flag:                         # 如果摄像头成功采集图片, 则执行后续操作
                            
                                self.facemeshdetector.update(masked_image, image_flag)       # 调用关键点检测程序
                                lm, bs, rm = self.facemeshdetector.get_results()   # 获取关键点检测结果

                                # 如果模型推理成功，则滤波、计算头部位姿
                                if lm is not None and bs is not None and rm is not None:
                                    if self.fp.process_frame(masked_image):
                                         
                                        rpy = self.headpose.pose_det(rm=rm)

                                        # self.facemeshdetector.visualize_return()
                                        # cv2.imshow("Camera", facemeshdetector.visualize_return())               ##### cv2显示人脸
                                        # cv2.waitKey(1)
                                        ################################# MMMMMMMMMMMMMMMMMMMMM 显示到界面
                                        img_detect = self.facemeshdetector.visualize_results()
                                        img_detect = cv2.cvtColor(img_detect, cv2.COLOR_BGR2RGB)
                                        # # 使用cv2.resize进行降采样     self.label_video_origin.size().width()  361          self.label_video_origin.size().height()
                                        img_detect = cv2.resize(img_detect, (self.label_video_detect.size().width(),  self.label_video_detect.size().height()), interpolation=cv2.INTER_LINEAR)

                                        # 获取图像大小并创建 QImage
                                        h, w, ch = img_detect.shape
                                        bytes_per_line = ch * w         # h,w    (480, 640)
                                        qimg = QImage(img_detect.data, w, h, bytes_per_line, QImage.Format_RGB888)

                                        # 将 QImage 显示在 QLabel 中
                                        self.label_video_detect.setPixmap(QPixmap.fromImage(qimg))
                                        ################################# WWWWWWWWWWWWWWWWWWWWW
                                        temp_servos = Servos()
                                        servos = handle_data(self.servo_flag, bs, rpy, temp_servos)
                                        if count == 0:
                                            servos.head_steps(20)
                                            count += 1

                                        elif count == 1:
                                            servos.head_steps(1)
                                        self.servosCtrl.plan_and_pub(servos, self.headCtrl, self.mouthCtrl, cycles=1)
                                    else:
                                        count = 0
                                        # print("move too fast")
                                        self.textBrowser_msg.insertPlainText('['+ str(datetime.datetime.now())+']\tmove too fast\n')
                                        self.textBrowser_msg.verticalScrollBar().setValue(self.textBrowser_msg.verticalScrollBar().maximum())
                                        self.servosCtrl.plan_and_pub(self.zeroServos,headCtrl=self.headCtrl,mouthCtrl=self.mouthCtrl, cycles=1)

                                else:
                                    count = 0
                                    # print("head not found")
                                    self.textBrowser_msg.insertPlainText('['+ str(datetime.datetime.now())+']\thead not found\n')
                                    self.textBrowser_msg.verticalScrollBar().setValue(self.textBrowser_msg.verticalScrollBar().maximum())
                                    self.servosCtrl.plan_and_pub(self.zeroServos,headCtrl=self.headCtrl,mouthCtrl=self.mouthCtrl,cycles=1)
                            
                        t2 = time.time()
                        print(f"帧率为{1/(t2-t1)}")
                        # self.textBrowser_msg.insertPlainText('['+ str(datetime.datetime.now())+']\t'+f"帧率为{1/(t2-t1)}\n")
                        # self.textBrowser_msg.verticalScrollBar().setValue(self.textBrowser_msg.verticalScrollBar().maximum())


                    else :
                        print('关闭状态')
                        # self.textBrowser_msg.insertPlainText('['+ str(datetime.datetime.now())+']\t关闭状态\n')
                        # self.textBrowser_msg.verticalScrollBar().setValue(self.textBrowser_msg.verticalScrollBar().maximum())

                        time.sleep(0.08)            # pyqt 发送过快会崩溃

            except Exception as e:
                print("错误：",e)
                # self.textBrowser_msg.insertPlainText('['+ str(datetime.datetime.now())+']\t错误\n')


            finally:
                self.servosCtrl.plan_and_pub(self.zeroServos,headCtrl=self.headCtrl,mouthCtrl=self.mouthCtrl,cycles=1)
                print("----------------end---------------")
                self.cap.release()
    



if __name__ == "__main__":
    # 固定的，PyQt5程序都需要QApplication对象。sys.argv是命令行参数列表，确保程序可以双击运行
    app = QApplication(sys.argv)
    # 初始化
    myWin = MyMainForm()
    # 将窗口控件显示在屏幕上
    myWin.show()
    # 程序运行，sys.exit方法确保程序完整退出。
    sys.exit(app.exec_())
