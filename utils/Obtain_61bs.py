import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir))


from enum import Enum
import socket
from utils.det_face_livelink import PyLiveLinkFace, FaceBlendShape


class FaceBlendShape(Enum):
    # 眼部14个自由度
    EyeBlinkLeft = 0
    EyeLookDownLeft = 1
    EyeLookInLeft = 2
    EyeLookOutLeft = 3
    EyeLookUpLeft = 4
    EyeSquintLeft = 5
    EyeWideLeft = 6
    EyeBlinkRight = 7
    EyeLookDownRight = 8
    EyeLookInRight = 9
    EyeLookOutRight = 10
    EyeLookUpRight = 11
    EyeSquintRight = 12
    EyeWideRight = 13

    # 下颚4个自由度
    JawForward = 14
    JawLeft = 15
    JawRight = 16
    JawOpen = 17
    
    # 嘴部 23个自由度
    MouthClose = 18
    MouthFunnel = 19
    MouthPucker = 20
    MouthLeft = 21
    MouthRight = 22
    MouthSmileLeft = 23
    MouthSmileRight = 24
    MouthFrownLeft = 25
    MouthFrownRight = 26
    MouthDimpleLeft = 27
    MouthDimpleRight = 28
    MouthStretchLeft = 29
    MouthStretchRight = 30
    MouthRollLower = 31
    MouthRollUpper = 32
    MouthShrugLower = 33
    MouthShrugUpper = 34
    MouthPressLeft = 35
    MouthPressRight = 36

    MouthLowerDownLeft = 37
    MouthLowerDownRight = 38
    MouthUpperUpLeft = 39
    MouthUpperUpRight = 40

    # 眉毛5个自由度
    BrowDownLeft = 41
    BrowDownRight = 42
    BrowInnerUp = 43
    BrowOuterUpLeft = 44
    BrowOuterUpRight = 45
    
    CheekPuff = 46
    CheekSquintLeft = 47
    CheekSquintRight = 48
    NoseSneerLeft = 49
    NoseSneerRight = 50
    TongueOut = 51
    
    # 头部3个自由度
    HeadYaw = 52
    HeadPitch = 53
    HeadRoll = 54
    
    LeftEyeYaw = 55
    LeftEyePitch = 56
    LeftEyeRoll = 57
    RightEyeYaw = 58
    RightEyePitch = 59
    RightEyeRoll = 60


def get_61_blendshape(live_link_face):
    blend_shapes = {}
    try:
        # 定义所有需要获取的BlendShape
        for shape in FaceBlendShape:
            blend_shapes[shape.name] = live_link_face.get_blendshape(shape)
    except Exception as e:
        print(f"获取BlendShape时出错: {e}")
        return None

    return blend_shapes



if __name__ == "__main__":
    UDP_PORT = 8000
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("192.168.50.151", UDP_PORT))  # 50 --> droid ip
    
    while True: 
        data, addr = s.recvfrom(1024)
        success, live_link_face = PyLiveLinkFace.decode(data)
        if success:
            blendshape_data = get_61_blendshape(live_link_face)
            
            if blendshape_data is not None:
                for shape_name, value in blendshape_data.items():
                    print(f"{shape_name}: {value}")
            else:
                print("未能获取BlendShape数据.")
        