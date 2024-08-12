import time


# 机器人初始化
def initFaceRobot(servo_flag, headCtrl, mouthCtrl):
    if not servo_flag:
        return
    while True:
        try:
            headCtrl.send()
            mouthCtrl.send()
            break
        except:
            print("error")
            time.sleep(1)


# BS数据映射
def map_range(x, from_min, from_max, to_min, to_max):
    # 确保 x 在 from_min 和 from_max 之间
    x = max(min(x, from_max), from_min)
    from_range = from_max - from_min
    to_range = to_max - to_min
    mapped_value = (x - from_min) * (to_range / from_range) + to_min

    return mapped_value


# BS数据驱动
def bs2head_mouth(bs, rpy_angles, servos):
    l_blink = bs[9]
    l_eye_wide = bs[21]
    r_blink = bs[10]
    r_eye_wide = bs[22]


    l_eye_out = bs[15]          # eye_look_out_left
    l_eye_in = bs[13]           # eye_look_in_left
    l_eye_up = bs[17]             # EyeLookUpLeft
    l_eye_down = bs[11]           # EyeLookDownLeft

    r_eye_out = bs[16] # eye_look_out_right
    r_eye_in = bs[14]  # eye_look_in_right
    r_eye_up = bs[18]    # EyeLookUpRight
    r_eye_down = bs[12]  # EyeLookDownRight

    brow_up = bs[3]

    l_brow_in = bs[1]
    r_brow_in = bs[2]

    brow_up_left = bs[17]
    brow_up_right = bs[18]
    brow_down_left = bs[11]
    brow_down_right = bs[12]


    
    
    
    servos.left_blink[0] = 0.8*map_range(l_blink, 0, 0.8, 0.56, 0) + 0.2*map_range(l_eye_wide, 0, 1, 0.56, 1)
    servos.right_blink[0] = 0.8*map_range(r_blink, 0, 0.8, 0.56, 0) + 0.2*map_range(r_eye_wide, 0, 1, 0.56, 1)

    
    servos.left_eye_level[0] = map_range(1.3*(l_eye_out - l_eye_in), -1, 1 , 0 , 1)
    servos.right_eye_level[0] = map_range(1.3*(r_eye_in - r_eye_out), -1, 1, 0, 1)
    servos.left_eye_erect[0] = map_range(1.3*(l_eye_down - l_eye_up), -1, 1, 1, 0) # pad --> 0-1
    servos.right_eye_erect[0] = map_range(1.3*(r_eye_down - r_eye_up), -1, 1, 1, 0) # pad --> 0-1
    

    servos.left_eyebrow_erect[0] = map_range(brow_up, 0, 1, 0.01, 0.99)
    servos.right_eyebrow_erect[0] = map_range(brow_up, 0, 1, 0.01, 0.99)
    
    servos.left_eyebrow_level[0] = map_range(l_brow_in, 0, 1, 0.2, 1)
    servos.right_eyebrow_level[0] = map_range(r_brow_in, 0, 1, 1, 0.2) 



    # print("--------------------",rpy_angles[2],rpy_angles[0],rpy_angles[1])
    servos.head_bai[0] = map_range(1.5 * rpy_angles[2], -45, 45,  0, 1)      # 左摆[-45,45]
    servos.head_dian[0] = map_range(1.5 * rpy_angles[0], -45, 45, 1, 0)    # 抬头[-45,45]
    servos.head_yao[0] = map_range(1.5 * rpy_angles[1], -45, 45,1, 0)      # 右摇[-45,45]



    # -----------------------------------------------------------------
    JawOpen = bs[25]
    JawLeft = bs[24]
    JawRight = bs[26]
    JawForward = bs[23]*100


    servos.jawOpenLeft[0]  = map_range(JawOpen, 0, 1, 0, 1)
    servos.jawOpenRight[0] = map_range(JawOpen, 0, 1, 0, 1)


    if JawForward >0.15:
        servos.jawBackLeft[0]  = map_range(JawForward, 0, 0.3, 0.4, 0.9)
        servos.jawBackRight[0] = map_range(JawForward, 0, 0.3, 0.4, 0.9)
    else:

        if JawRight > 0.2:
            servos.jawBackLeft[0]  = map_range(JawRight, 0, 1, 0.5, 0)
            servos.jawBackRight[0] = map_range(JawRight, 0, 1, 0.5, 1)
            jawBackLeft1  = map_range(JawLeft, 0, 1, 0.5, 0)
            jawBackRight1 = map_range(JawLeft, 0, 1, 0.5, 1)

        else:
            servos.jawBackLeft[0]  = map_range(JawLeft, 0, 1, 0.5, 1)
            servos.jawBackRight[0] = map_range(JawLeft, 0, 1, 0.5, 0)




    '''
    # 下颚 前伸
    servos.jawBackLeft  = map_range(JawForward, 0, 1, 0.5, 1)
    servos.jawBackRight = map_range(JawForward, 0, 1, 0.5, 1)

    # 下颚左右平移
    servos.jawBackLeft  = map_range(JawLeft, 0, 1, 0.5, 0)  + map_range(JawRight, 0, 1, 0.5, 1)
    servos.jawBackRight = map_range(JawLeft, 0, 1, 0.5, 1)  + map_range(JawRight, 0, 1, 0.5, 0)
    
    '''



    mouth_UpperUpLeft     = bs[48] # mouth_UpperUpLeft
    mouth_UpperUpRight    = bs[49] # mouth_UpperUpRight
    mouth_LowerDownLeft   = bs[34] # mouth_LowerDownLeft
    mouth_LowerDownRight  = bs[35] # mouth_LowerDownRight

    servos.mouthUpperUpLeft[0]     = mouth_UpperUpLeft
    servos.mouthUpperUpRight [0]   = mouth_UpperUpRight
    servos.mouthLowerDownLeft[0]   = mouth_LowerDownLeft
    servos.mouthLowerDownRight[0]  = mouth_LowerDownRight


# ----------------------------------------------------------------------------------------------------------------------------
    MouthLeft = bs[33]  # MouthLeft
    MouthRight = bs[39]  # MouthRight
    MouthSmileLeft = bs[44]  # MouthSmileLeft
    MouthSmileRight = bs[45]  # MouthSmileRight
    MouthFrownLeft = bs[30]  # MouthFrownLeft
    MouthFrownRight = bs[31]  # MouthFrownRight


    MouthFunnel         = bs[32]
    MouthPucker         = bs[38]
    MouthUpperUpLeft     = bs[48] # mouth_UpperUpLeft
    MouthUpperUpRight    = bs[49] # mouth_UpperUpRight
    MouthLowerDownLeft   = bs[34] # mouth_LowerDownLeft
    MouthLowerDownRight  = bs[35] # mouth_LowerDownRight

    mouth_UpperUpLeft    = 1 - (JawOpen*0.5 + MouthFunnel*0.3 + MouthUpperUpLeft*0.2)
    mouth_UpperUpRight   = 1 - (JawOpen*0.5 + MouthFunnel*0.3 + MouthUpperUpRight*0.2)
    mouth_LowerDownLeft  = JawOpen*0.5 + MouthPucker*0.1 + MouthLowerDownLeft*0.2
    mouth_LowerDownRight = JawOpen*0.5 + MouthPucker*0.1 + MouthLowerDownRight*0.2



    mouth_CornerLx = (MouthLeft*0.8 + MouthRight*0.2 + JawOpen)
    mouth_CornerLy = MouthSmileLeft*0.5 + 0.5*(1 - MouthFrownLeft*2)
    mouth_CornerRx = (MouthLeft*0.2 + MouthRight*0.8 + JawOpen)
    mouth_CornerRy = MouthSmileRight*0.5 + 0.5*(1- MouthFrownRight*2)

    mouth_CornerLy = 1 - mouth_CornerLy
    # mouth_CornerRx = 1 - mouth_CornerRx



    servos.mouthCornerUpLeft[0]    = 0.5#  mouth_CornerLx + mouth_CornerLy
    servos.mouthCornerUpRight[0]   = 0.5# -mouth_CornerRx + mouth_CornerRy
    servos.mouthCornerDownLeft[0]  = 0.5# -mouth_CornerLx + mouth_CornerLy
    servos.mouthCornerDownRight[0] =  0.5#  mouth_CornerRx + mouth_CornerRy



    return servos
 

# BS数据接收处理
def handle_data(servo_flag, bs, rpy,servos):
    if not servo_flag:
        return
    bs_array = bs
    dian, yao, bai = rpy[0], rpy[1], rpy[2]

    # 纠正头部姿态信息
    dian = -dian if 360 - dian > dian else 360 - dian
    yao = -yao if 360 - yao > yao else 360 - yao
    bai = -bai if 360 - bai > bai else 360 - bai

    return bs2head_mouth(bs_array, [dian, yao, bai], servos)

