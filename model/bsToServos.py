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
def bs2head_mouth(bs, rpy_angles, headCtrl, mouthCtrl):
    l_blink =bs[9]
    l_eye_wide =bs[21]
    r_blink =bs[10]
    r_eye_wide = bs[22]
    brow_up =bs[3]
    l_brow_in =bs[1]
    r_brow_in = bs[2]
    brow_up_left = bs[17]
    brow_up_right = bs[18]
    brow_down_left = bs[11]
    brow_down_right = bs[12]
    eye_look_out_left = bs[15]
    eye_look_out_right = bs[16]
    eye_look_in_left = bs[13]
    eye_look_in_right = bs[14]
    # print("brow_up",brow_up)
    # ============== head control ================
    # headCtrl.left_blink = 0.9*map_range(l_blink, 0, 0.7, 0.5, 0)
    # headCtrl.right_blink = 0.9*map_range(r_blink, 0, 0.7, 0.3, 0)


    ################眼睛闭合太多左右眼睛会因为眉毛的拉伸而导致眼皮闭合不一致，尽量0.3以上####################
    headCtrl.left_blink = map_range(l_blink, 0, 0.8, 0.3, 0) # + 0.1*map_range(l_eye_wide, 0, 1, 0.56, 1)

    headCtrl.right_blink = map_range(r_blink, 0, 0.5, 0.3, 0) # + 0.1*map_range(r_eye_wide, 0, 1, 0.56, 1)

    headCtrl.left_eye_erect = 0.5 +0.4*(brow_down_left-brow_up_left)# 左眼竖 上 [0.01 - 0.50 - 0.99] 下
    headCtrl.left_eye_level = 0.5 +0.4*(eye_look_out_left-eye_look_in_left) # 左眼平 内 [0.01 - 0.50 - 0.99] 外
    headCtrl.right_eye_erect = 0.5 + 0.4*(brow_up_right-brow_down_right)# 右眼竖 下 [0.01 - 0.50 - 0.99] 上
    headCtrl.right_eye_level = 0.5 +0.4*(eye_look_in_right-eye_look_out_right) # 右眼平 外 [0.01 - 0.50 - 0.99] 眼左
    



    headCtrl.left_eyebrow_erect = map_range(brow_up, 0, 0.2, 0.01, 0.99)
    headCtrl.right_eyebrow_erect = map_range(brow_up, 0, 0.2, 0.01, 0.99)

    
    headCtrl.left_eyebrow_level = map_range(l_brow_in, 0, 1, 0.2, 1)
    headCtrl.right_eyebrow_level = map_range(r_brow_in, 0, 1, 1, 0.2)

    # headCtrl.head_dian = 0.5
    # headCtrl.head_yao = 0.5 # 0.5 + HeadYaw
    # headCtrl.head_bai = 0.5  # 0.5 - HeadRoll
    headCtrl.head_dian = map_range(1.5 * rpy_angles[0], -45, 45, 0.1, 0.9)  # 0.5 + HeadPitch
    headCtrl.head_yao = map_range(1.5 * rpy_angles[1], -45, 45, 0.1, 0.9)  # 0.5 + HeadYaw
    headCtrl.head_bai = map_range(1.5 * rpy_angles[2], -45, 45, 0.9, 0.1)  # 0.5 - HeadRoll


    # ================ mouth control ==================
    JawOpen = bs[25]  # JawOpen
    JawLeft = bs[24]
    JawRight = bs[26]
    JawForward = bs[23]*100
    print("JawForward",JawForward)


    # --------------------------------
    mouthCtrl.jawOpenLeft  = map_range(JawOpen, 0, 1, 0, 1)
    mouthCtrl.jawOpenRight = map_range(JawOpen, 0, 1, 0, 1)


    # if JawLeft > 0.15 or JawRight > 0.15:
    #     mouthCtrl.jawBackLeft  = map_range(JawLeft, 0, 0.15, 0.5, 0)  + map_range(JawRight, 0, 0.15, 0.5, 1)
    #     mouthCtrl.jawBackRight = map_range(JawLeft, 0, 0.15, 0.5, 1)  + map_range(JawRight, 0, 0.15, 0.5, 0)

    if JawForward >0.15:
        mouthCtrl.jawBackLeft  = map_range(JawForward, 0, 0.3, 0.4, 0.9)
        mouthCtrl.jawBackRight = map_range(JawForward, 0, 0.3, 0.4, 0.9)
    else:
        print("JawLeft",JawLeft)
        print("JawRight",JawRight)
        if JawRight > 0.2:
            mouthCtrl.jawBackLeft  = map_range(JawRight, 0, 1, 0.5, 0)
            mouthCtrl.jawBackRight = map_range(JawRight, 0, 1, 0.5, 1)
            jawBackLeft1  = map_range(JawLeft, 0, 1, 0.5, 0)
            jawBackRight1 = map_range(JawLeft, 0, 1, 0.5, 1)
            print("mouthCtrl.jawBackLeft",jawBackLeft1)
            print("mouthCtrl.jawBackLeft",jawBackRight1)
        else:
            mouthCtrl.jawBackLeft  = map_range(JawLeft, 0, 1, 0.5, 1)
            mouthCtrl.jawBackRight = map_range(JawLeft, 0, 1, 0.5, 0)




    '''
    # 下颚 前伸
    mouthCtrl.jawBackLeft  = map_range(JawForward, 0, 1, 0.5, 1)
    mouthCtrl.jawBackRight = map_range(JawForward, 0, 1, 0.5, 1)

    # 下颚左右平移
    mouthCtrl.jawBackLeft  = map_range(JawLeft, 0, 1, 0.5, 0)  + map_range(JawRight, 0, 1, 0.5, 1)
    mouthCtrl.jawBackRight = map_range(JawLeft, 0, 1, 0.5, 1)  + map_range(JawRight, 0, 1, 0.5, 0)
    
    '''



    mouth_UpperUpLeft     = bs[48]
    mouth_UpperUpRight    = bs[49]
    mouth_LowerDownLeft   = bs[34]
    mouth_LowerDownRight  = bs[35]

    mouthCtrl.mouthUpperUpLeft     = mouth_UpperUpLeft
    mouthCtrl.mouthUpperUpRight    = mouth_UpperUpRight
    mouthCtrl.mouthLowerDownLeft   = mouth_LowerDownLeft
    mouthCtrl.mouthLowerDownRight  = mouth_LowerDownRight

# ----------------------------------------------------------------------------------------------------------------------------
    MouthLeft = bs[33]  # MouthLeft
    MouthRight = bs[39]  # MouthRight
    MouthSmileLeft = bs[44]  # MouthSmileLeft
    MouthSmileRight = bs[45]  # MouthSmileRight
    MouthFrownLeft = bs[30]  # MouthFrownLeft
    MouthFrownRight = bs[31]  # MouthFrownRight

    mouth_CornerLx = (MouthLeft*0.8 + MouthRight*0.2 + JawOpen)
    mouth_CornerLy = MouthSmileLeft*0.5 + 0.5*(1 - MouthFrownLeft*2)
    mouth_CornerRx = (MouthLeft*0.2 + MouthRight*0.8 + JawOpen)
    mouth_CornerRy = MouthSmileRight*0.5 + 0.5*(1- MouthFrownRight*2)

    # print(mouth_CornerLx, mouth_CornerLy, mouth_CornerRx, mouth_CornerRy)

    mouth_CornerLy = 1 - mouth_CornerLy
    # mouth_CornerRx = 1 - mouth_CornerRx
    mouthCtrl.mouthCornerUpLeft    =  mouth_CornerLx + mouth_CornerLy
    mouthCtrl.mouthCornerUpRight   = -mouth_CornerRx + mouth_CornerRy
    mouthCtrl.mouthCornerDownLeft  = -mouth_CornerLx + mouth_CornerLy
    mouthCtrl.mouthCornerDownRight =  mouth_CornerRx + mouth_CornerRy


    try:
        headCtrl.send()
        mouthCtrl.send()
    except:
        print("error write")
        headCtrl.close()
        mouthCtrl.close()
 

# BS数据接收处理
def handle_data(servo_flag, bs, rpy, headCtrl, mouthCtrl):
    if not servo_flag:
        return
    bs_array = bs
    dian, yao, bai = rpy[0], rpy[1], rpy[2]

    # 纠正头部姿态信息
    dian = -dian if 360 - dian > dian else 360 - dian
    yao = -yao if 360 - yao > yao else 360 - yao
    bai = -bai if 360 - bai > bai else 360 - bai

    bs2head_mouth(bs_array, [dian, yao, bai], headCtrl, mouthCtrl)

