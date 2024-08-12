import cv2


# ==========================================================================
# 摄像头程序(普通摄像头)
# ==========================================================================
class SetCamera:
    def __init__(self,cameraIdx):
        self.cap = None
        self.cameraIdx = cameraIdx
        self.cap = cv2.VideoCapture(self.cameraIdx)
        self.frame_width, self.frame_height, self.fps = 640, 480, 10
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)

    # start camera
    def start_camera(self,index):
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.cameraIdx)

            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        else:
            pass
        return True

    def read(self):
        success, image = self.cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            return None, False
        else:
            return image, True

    # stop camera
    def stop_camera(self):
        self.cap.release()
        self.cap = None
        cv2.destroyAllWindows()
