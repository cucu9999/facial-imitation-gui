import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir))

from det_face_mediapipe import FaceMeshDetector
import cv2
import numpy as np
from enum import Enum

from scipy.spatial.transform import Rotation


class FaceBlendShape(Enum):

    # 眉毛5个自由度
    BrowDownLeft = 1
    BrowDownRight = 2
    BrowInnerUp = 3
    BrowOuterUpLeft = 4
    BrowOuterUpRight = 5
    
    # 脸颊 3个自由度
    CheekPuff = 6
    CheekSquintLeft = 7
    CheekSquintRight = 8
    
    # 眼睛 14个自由度
    EyeBlinkLeft = 9
    EyeBlinkRight = 10
    EyeLookDownLeft = 11
    EyeLookDownRight = 12
    EyeLookInLeft = 13
    EyeLookInRight = 14
    EyeLookOutLeft = 15
    EyeLookOutRight = 16
    EyeLookUpLeft = 17
    EyeLookUpRight = 18
    EyeSquintLeft = 19
    EyeSquintRight = 20
    EyeWideLeft = 21
    EyeWideRight = 22
    
    # 下颚 4个自由度
    JawForward = 23
    JawLeft = 24
    JawOpen = 25
    JawRight = 26
    
    # 嘴部 23个自由度
    MouthClose = 27
    MouthDimpleLeft = 28
    MouthDimpleRight = 29
    MouthFrownLeft = 30
    MouthFrownRight = 31
    MouthFunnel = 32
    MouthLeft = 33
    MouthLowerDownLeft = 34
    MouthLowerDownRight = 35
    MouthPressLeft = 36
    MouthPressRight = 37
    MouthPucker = 38
    MouthRight = 39
    MouthRollLower = 40
    MouthRollUpper = 41
    MouthShrugLower = 42
    MouthShrugUpper = 43
    MouthSmileLeft = 44
    MouthSmileRight = 45
    MouthStretchLeft = 46
    MouthStretchRight = 47
    MouthUpperUpLeft = 48
    MouthUpperUpRight = 49
    
    # 鼻子 2个自由度
    NoseSneerLeft = 50
    NoseSneerRight = 51



class Obtain_head:
    def __init__(self):
        self.face_mesh_detector = FaceMeshDetector()
        self.blendshape_dict = {}
        
    def get_51_blendshape_rpy(self, image):
        self.image = image
        landmark, blendshape, r_mat = self.face_mesh_detector.get_results(self.image)

        blendshape_dict = {}
        rpy_angles = []
        if blendshape is not None:
            for shape in FaceBlendShape:
                blendshape_dict[shape.name] = blendshape[shape.value]

            r = Rotation.from_matrix(r_mat[:3, :3])
            result = r.as_euler('xyz', degrees=True)

            dian = result[0]
            yao = result[1]
            bai = result[2]
            rpy_angles = [dian, yao, bai]
        
        return blendshape_dict, rpy_angles


if __name__ == '__main__':
    # img_path = os.path.join(script_dir, "test.png")
    # img = cv2.imread(img_path)
    # head_obtainer = Obtain_head()

    # if img is None:
    #     print("can not find the image, please check the path")
    # else:
    #     blendshape, angles = head_obtainer.get_52_blendshape_rpy(img)
    #     print(blendshape, angles)
    

    head_obtainer = Obtain_head()

    cap = cv2.VideoCapture(4)

    if not cap.isOpened():
        print("Cannot open webcam")
        exit()

    # Get frame dimensions
    ret, frame = cap.read()
    frame_height, frame_width = frame.shape[:2]

    # Font settings
    font_scale = 0.4  # Smaller font size
    font_thickness = 1
    font = cv2.FONT_HERSHEY_SIMPLEX
    line_type = cv2.LINE_AA

    # Calculate maximum number of lines per column based on frame height
    line_height = int(cv2.getTextSize('Text', font, font_scale, font_thickness)[0][1] * 1.5)
    max_lines = frame_height // line_height - 1  # Leave space for angles

    # Number of blendshapes
    num_blendshapes = len(FaceBlendShape)
    num_columns = (num_blendshapes + max_lines - 1) // max_lines  # Ceiling division

    # Column widths
    col_width = frame_width // num_columns

    while True:
        # Read a frame from the webcam
        ret, frame = cap.read()

        if not ret:
            print("Failed to grab frame")
            break

        # Process the frame to get blendshape dictionary and angles
        blendshape, angles = head_obtainer.get_51_blendshape_rpy(frame)

        overlay = frame.copy()

        if blendshape is not None and angles is not None:
            # Create semi-transparent background
            cv2.rectangle(overlay, (0, 0), (frame_width, frame_height), (0, 0, 0), -1)
            alpha = 0.4  # Transparency factor
            frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

            # Display blendshape values in columns
            blendshape_items = list(blendshape.items())
            for idx, (key, value) in enumerate(blendshape_items):
                column = idx // max_lines
                row = idx % max_lines

                x = column * col_width + 10
                y = (row + 1) * line_height

                text = f"{key}: {value:.2f}"
                cv2.putText(frame, text, (x, y), font, font_scale, 
                            (0, 255, 0), font_thickness, line_type)

            # Display rotation angles at the bottom
            angle_text = f"Roll: {angles[0]:.2f}, Pitch: {angles[1]:.2f}, Yaw: {angles[2]:.2f}"
            cv2.putText(frame, angle_text, (10, frame_height - 10), font, font_scale, 
                        (0, 255, 255), font_thickness, line_type)
        else:
            cv2.putText(frame, "No face detected", (10, 30), font, 0.7, 
                        (0, 0, 255), 2, line_type)

        # Display the frame with overlay
        cv2.imshow('Blendshape Live Feed', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and close windows
    cap.release()
    cv2.destroyAllWindows()

