import cv2


class ConfigCamera:
    def __init__(self, input_source=0, width=640, height=480):
        self.cap = None
        self.input_source = input_source
        self.image_w = width
        self.image_h = height
        self.cameras_num = 10
        
        self.open_camera()

    def open_camera(self):
        self.cap = cv2.VideoCapture(self.input_source)
        if self.cap.isOpened():
            print("successfully load source input:{str(self.input_source)}")

        if not self.cap.isOpened():
            if isinstance(self.input_source, int):
                for idx in range(self.input_source, self.cameras_num):
                    self.cap = cv2.VideoCapture(idx)
                    if self.cap.isOpened():
                        print(f"successfully opened camera index: {self.input_source}")
                        self.input_source = idx
                        break
                    print(f"\n cannot open camera index: {idx}. trying next camera...")
            
            print("there is no camera available.")
            raise RuntimeError("no camera available")
            

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.image_w)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.image_h)
        print("camera resolution: [width, height] = [%d, %d]" % (self.image_w, self.image_h))

    def start_camera(self):
        success, image = self.cap.read()
        if not success:
            print("ignoring empty camera frame, please check your camera!!!")
            return None, False
        return image, True

    def stop_camera(self):
        if self.cap is not None:
            self.cap.release()
            cv2.destroyAllWindows()
            self.cap = None

if __name__ == '__main__':
    camera = None

    try:
        # camera = ConfigCamera(input_source="/media/2T/yongtong/Rena/RenaBlender/demo.mp4", width=640, height=480)
        camera = ConfigCamera(input_source=4, width=640, height=480)

        while True:
            image, success = camera.start_camera()
            if success:
                cv2.imshow("camera view", image)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    except Exception as e:
        print(f"unexpected error: {e}")
        
    finally:
        if camera is not None:
            camera.stop_camera()

