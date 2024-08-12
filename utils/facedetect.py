# ==========================================================================
# 导入Python库, 设置环境路径, 设置文件路径
# ==========================================================================
import cv2
from .setCamera import SetCamera
from .faceCapture import FaceMeshDetector, HeadPose

class FacePoseDetector:
    def __init__(self):
        self.fm = FaceMeshDetector()  # 初始化面部网格检测器
        self.hp = HeadPose()          # 初始化头部姿态估计器
        self.past_pose = None         # 存储之前的姿态信息

    def initialize(self, image):
        """初始化检测器，并计算初始姿态"""
        self.fm.update(image, True)    # 更新面部网格检测结果
        _, _, r_mat = self.fm.get_results()  # 获取检测结果
        if r_mat is not None:
            self.past_pose = self.hp.pose_det(r_mat)  # 计算并存储初始人脸姿态
            return True
        else:
            return "initialize failed"

    def process_frame(self, image):
        """处理每一帧图像，计算当前姿态并判断运动速度"""
        if image.any() != None:
            self.fm.update(image, True)   # 更新检测结果
            _, _, r_mat = self.fm.get_results()
            if r_mat is not None:
                cur_pose = self.hp.pose_det(r_mat)  # 计算当前姿态

                # 计算姿态变化
                delta_pose = max(
                    abs(cur_pose[0] - self.past_pose[0]),
                    abs(cur_pose[1] - self.past_pose[1]),
                    abs(cur_pose[2] - self.past_pose[2])
                )

                # print(delta_pose)
                if delta_pose > 16:
                    self.past_pose = cur_pose
                    print("Move too fast!!!!!")  # 判断是否移动过快
                    return False

                # 更新过去的姿态
                self.past_pose = cur_pose

        return True  # 表示没有移动过快


# ==========================================================================
# 程序入口
# ==========================================================================
if __name__ == "__main__":
    fm = FaceMeshDetector()
    hp = HeadPose()
    sc = SetCamera(0)
    fp = FacePoseDetector()
    # sc.start_camera()  # 启动摄像头
    image,image_flag = sc.read()
    if image_flag:                         # 如果摄像头成功采集图片, 则执行后续操作
        fp.initialize(image)               # 调用关键点检测程序


    try:
        while True:
            image, image_flag = sc.read()  # 启动摄像头
            if image_flag:                         # 如果摄像头成功采集图片, 则执行后续操作
                if fp.process_frame(image):
                    fm.update(image, image_flag)       # 调用关键点检测程序
                    lm, _, _ = fm.get_results()   # 获取关键点检测结果
                    if lm is not None:
                        fm.visualize_results()
                        print("1111111111")
                else:
                    break
    finally:
        sc.stop_camera()