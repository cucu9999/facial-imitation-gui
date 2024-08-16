import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap

class CameraApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        self.setWindowTitle("摄像头显示")
        self.setGeometry(100, 100, 800, 600)

        # 创建一个 QLabel 来显示摄像头内容
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)

        # 创建一个垂直布局，将 QLabel 添加到布局中
        layout = QVBoxLayout()
        layout.addWidget(self.label)

        # 创建一个中心窗口并设置布局
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 打开摄像头
        self.cap = cv2.VideoCapture(0)
        # self.cap = cv2.VideoCapture(2)


        # 设置定时器，每30ms调用一次 update_frame 函数
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        # 从摄像头读取一帧
        ret, frame = self.cap.read()

        if ret:
            # 将 BGR 格式转换为 RGB 格式
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 获取图像大小并创建 QImage
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

            # 将 QImage 显示在 QLabel 中
            self.label.setPixmap(QPixmap.fromImage(qimg))

    def closeEvent(self, event):
        # 在窗口关闭时释放摄像头
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = CameraApp()
    win.show()
    sys.exit(app.exec_())
