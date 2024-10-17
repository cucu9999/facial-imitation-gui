


def map_range(x, from_min, from_max, to_min, to_max):
    '''
    线性映射函数，将 x 从 from_min-from_max 线性映射到 to_min-to_max 区间
    '''
    x = max(min(x, from_max), from_min)
    from_range = from_max - from_min
    to_range = to_max - to_min
    mapped_value = (x - from_min) * (to_range / from_range) + to_min

    return mapped_value



def manual_model(bs_dict):

    # ======================================= 头部控制 =======================================
    # 眼皮--二自由度
    left_blink = 0.8*map_range(bs_dict["EyeBlinkLeft"], 0, 0.8, 0.56, 0) + 0.2*map_range(bs_dict["EyeWideLeft"], 0, 1, 0.56, 1)
    right_blink = 0.8*map_range(bs_dict["EyeBlinkRight"], 0, 0.8, 0.56, 0) + 0.2*map_range(bs_dict["EyeWideRight"], 0, 1, 0.56, 1)

    # 眼球--四自由度
    left_eye_level = map_range(1.3*(bs_dict["EyeLookOutLeft"] - bs_dict["EyeLookInLeft"]), -1, 1 , 0 , 1)
    right_eye_level = map_range(1.3*(bs_dict["EyeLookInRight"] - bs_dict["EyeLookOutRight"]), -1, 1, 0, 1)
    left_eye_erect = map_range(1.3*(bs_dict["EyeLookDownLeft"] - bs_dict["EyeLookUpLeft"]), -1, 1, 0, 1)
    right_eye_erect = map_range(1.3*(bs_dict["EyeLookDownRight"] - bs_dict["EyeLookUpRight"]), -1, 1, 0, 1)

    # 眉毛四自由度
    left_eyebrow_erect = map_range(bs_dict["BrowInnerUp"], 0, 1, 0.01, 0.99)
    right_eyebrow_erect = map_range(bs_dict["BrowInnerUp"], 0, 1, 0.01, 0.99)
    left_eyebrow_level = map_range(bs_dict["BrowDownLeft"], 0, 1, 0.2, 1)
    right_eyebrow_level = map_range(bs_dict["BrowDownRight"], 0, 1, 1, 0.2) 

    # 头部--三自由度
    head_bai =  map_range(bs_dict['HeadRoll'], -1, 1, 1, 0)
    head_dian = map_range(bs_dict['HeadPitch'], -0.5, 0.5, 0, 1)  
    head_yao =  map_range(bs_dict['HeadYaw'], -1, 1, 0, 1)


    # ======================================= 嘴部控制 =======================================
    # # 下颚--四自由度
    # jawOpenLeft  = map_range(bs_dict['JawOpen'], 0, 1, 0, 1)     
    # jawOpenRight = map_range(bs_dict['JawOpen'], 0, 1, 0, 1)  
    # jawBackLeft  = 0.5
    # jawBackRight = 0.5

    # # 嘴唇--四自由度
    # mouthUpperUpLeft     = bs_dict['MouthUpperUpLeft']
    # mouthUpperUpRight    = bs_dict['MouthUpperUpRight']
    # mouthLowerDownLeft   = bs_dict['MouthLowerDownLeft']
    # mouthLowerDownRight  = bs_dict['MouthLowerDownRight']

    # # 脸颊--四自由度
    # mouthCornerUpLeft    =   bs_dict['MouthSmileLeft']
    # mouthCornerUpRight   =   bs_dict['MouthSmileRight']
    # mouthCornerDownLeft  =   0.5  # 左悲伤
    # mouthCornerDownRight =   0.5  # 右悲伤

    # 下颚--四自由度
    jawOpenLeft  = map_range(bs_dict['JawOpen'], 0, 1, 0, 1) 
    jawOpenRight = map_range(bs_dict['JawOpen'], 0, 1, 0, 1) 
    jawBackLeft  = map_range((bs_dict['JawForward'] + 1.5*bs_dict['JawLeft'] - 1.5*bs_dict['JawRight']), -0.5, 0.5, 0, 1)
    jawBackRight = map_range((bs_dict['JawForward'] + 1.5*bs_dict['JawRight']- 1.5*bs_dict['JawLeft']) , -0.5, 0.5, 0, 1)

    # 嘴唇--四自由度
    mouthUpperUpLeft     = map_range((bs_dict['MouthUpperUpLeft'] - bs_dict['MouthPucker']) , -0.24, 0.76, 0, 1)                                        # 左上嘴唇  0.24
    mouthUpperUpRight    = map_range((bs_dict['MouthUpperUpRight']- bs_dict['MouthPucker']) , -0.24, 0.76, 0, 1)                                        # 右上嘴唇  0.24 
    mouthLowerDownLeft   = map_range(0.5* bs_dict['MouthLowerDownLeft'] + 1.5*bs_dict['MouthStretchLeft'] - bs_dict['MouthPucker'], -0.2, 0.8 , 0, 1)   #  0.2   # 左下嘴唇
    mouthLowerDownRight  = map_range(0.5* bs_dict['MouthLowerDownRight']+ 1.5*bs_dict['MouthStretchRight']- bs_dict['MouthPucker'], -0.2, 0.8 , 0, 1)   # 0.2   # 右下嘴唇

    # 脸颊--四自由度
    mouthCornerUpLeft    =   map_range((0.5* bs_dict['MouthSmileLeft'] + 0.5* bs_dict['MouthLeft'] - bs_dict['MouthRight']) , -0.23, 0.77, 0, 1) # bs_dict['MouthSmileLeft']
    mouthCornerUpRight   =   map_range((0.5* bs_dict['MouthSmileRight'] + 0.5* bs_dict['MouthRight'] - bs_dict['MouthLeft']) , -0.28, 0.72, 0, 1) # bs_dict['MouthSmileRight']
    mouthCornerDownLeft  =   map_range((4*bs_dict['MouthStretchLeft'] - bs_dict['MouthPucker']) , -0.24, 0.76, 0, 1)  # 左悲伤
    mouthCornerDownRight =   map_range((4*bs_dict['MouthStretchRight']- bs_dict['MouthPucker']) , -0.24, 0.76, 0, 1)  # 右悲伤


    head = [left_blink, left_eye_erect, left_eye_level, left_eyebrow_erect, left_eyebrow_level, right_blink, right_eye_erect, right_eye_level, right_eyebrow_erect, right_eyebrow_level, head_dian, head_yao, head_bai]
    
    mouth = [mouthUpperUpLeft, mouthUpperUpRight, mouthLowerDownLeft, mouthLowerDownRight, mouthCornerUpLeft, mouthCornerUpRight, mouthCornerDownLeft, mouthCornerDownRight, jawOpenLeft, jawOpenRight, jawBackLeft, jawBackRight]

    return head, mouth


