from serial import *
import time

# TODO: 从xml文件直接读取配置
class Servo:
    def __init__(self, id, jdStart, jdMax, jdMin, fScale, fOffSet, pos, norm):
        self.id = id
        self.jdStart = jdStart
        self.jdMax = jdMax
        self.jdMin = jdMin
        self.fScale = fScale
        self.fOffSet = fOffSet
        self.pos = pos
        self.norm = norm

# norm的方向，动作执行的执行方向，四个嘴角的提拉， 四个微笑角的咧嘴， 下颚的张开，下颚的从后往前
mouthUpperUpLeft     = Servo(13, 90,  162,  67.5, 11.1, 0, 0, 1) # 左上唇  下拉 [67.5- 90 - 162] 上提   0.24    ******
mouthUpperUpRight    = Servo( 6, 90, 112, 18, 11.1, 0, 0, -1)  # 右上唇  上提 [18- 90 - 112] 下拉     0.76   ******

mouthLowerDownLeft   = Servo( 5, 90, 126, 81, 11.1, 0, 0, 1)  # 左下唇  上提 [81 - 90 - 126] 下拉    0.2
mouthLowerDownRight  = Servo(14, 90,  99, 54, 11.1, 0, 0, -1) # 右下唇  下拉 [54 - 90 - 99] 上提    0.8
 
mouthCornerUpLeft    = Servo( 0, 90, 117, 0, 11.1, 0, 0, -1) # 嘴角左上；  左微笑上   上[0 - 90 - 117]下   0.77   ******
mouthCornerUpRight   = Servo( 8, 90, 160, 63, 11.1, 0, 0, 1) # 嘴角右上；  右微笑上  上[63 - 90 - 180]下  0.23  ******
mouthCornerDownLeft  = Servo(12, 90, 135, 45, 11.1, 0, 0, 1) # 嘴角左下；  左微笑下  上[45 - 90 - 135]下   0.5  ******
mouthCornerDownRight = Servo( 7, 90, 135, 45, 11.1, 0, 0, -1) # 嘴角右下；  右微笑下  下[45 - 90 - 135]上   0.5  ******

jawOpenLeft         = Servo( 2, 90, 135, 90, 11.1, 0, 0, 1)  # 左下颌  -  [90 - 90 - 135] 张        0.0
jawOpenRight        = Servo(10, 90,  90, 45, 11.1, 0, 0, -1) # 右下颌  张 [45 - 90 - 90] -         0.0

jawBackLeft          = Servo( 9, 90, 135, 45, 11.1, 0, 0, 1) # 左下颚斜；  前拉  [45 - 90 - 135] 后拉     0.5
jawBackRight         = Servo( 1, 90, 135, 45, 11.1, 0, 0, -1)  # 左下颚斜；  后拉  [45 - 90 - 135] 前拉    0.5

servos = [mouthUpperUpLeft, mouthUpperUpRight, mouthLowerDownLeft, mouthLowerDownRight,
          mouthCornerUpLeft, mouthCornerUpRight, mouthCornerDownLeft, mouthCornerDownRight,
          jawOpenLeft, jawOpenRight, jawBackLeft, jawBackRight
]

class MouthCtrl(Serial):
    #*args, **kwargs 这种写法代表这个方法接受任意个数的参数
    def __init__(self, arg, *args, **kwargs):
        super().__init__(arg, *args, **kwargs)
        if self.is_open:
            print('Open Success')
        else:
            print('Open Error')

        self.mouthUpperUpLeft     = 0.24   # 左上嘴唇  0.24
        self.mouthUpperUpRight    = 0.24   # 右上嘴唇  0.24
        self.mouthLowerDownLeft   = 0.2   # 左下嘴唇  0.2
        self.mouthLowerDownRight  = 0.2   # 右下嘴唇  0.2
        
        self.mouthCornerUpLeft    = 0.23   # 左上角  0.23
        self.mouthCornerUpRight   = 0.23   # 右上角  0.23
        self.mouthCornerDownLeft  = 0.5   # 左下角  0.5
        self.mouthCornerDownRight = 0.5   # 右下角  0.5

        self.jawOpenLeft         = 0.01   # 0.01
        self.jawOpenRight        = 0.01   # 0.01

        self.jawBackLeft          = 0.5   # 0.5  左前 [0.01 - 0.5 - 0.99] 右后
        self.jawBackRight         = 0.5   # 0.5  左后 [0.01 - 0.5 - 0.99] 右前

    @property
    def msgs(self):
        return [
            self.mouthUpperUpLeft, self.mouthUpperUpRight, self.mouthLowerDownLeft, self.mouthLowerDownRight,
            self.mouthCornerUpLeft, self.mouthCornerUpRight, self.mouthCornerDownLeft, self.mouthCornerDownRight,
            self.jawOpenLeft, self.jawOpenRight, self.jawBackLeft, self.jawBackRight
        ]

    def setmsg(self, data):
        self.mouthUpperUpLeft     = data[0]
        self.mouthUpperUpRight    = data[1]
        self.mouthLowerDownLeft   = data[2]
        self.mouthLowerDownRight  = data[3]
        
        self.mouthCornerUpLeft    = data[4]
        self.mouthCornerUpRight   = data[5]
        self.mouthCornerDownLeft  = data[6]
        self.mouthCornerDownRight = data[7]

        self.jawOpenLeft         = data[8]
        self.jawOpenRight        = data[9]

        self.jawBackLeft          = data[10]
        self.jawBackRight         = data[11]


    def send(self):
        # print(self.msgs)
        head = 0xaa
        num=0x00
        end=0x2f

        frameData = [head, num]

        servo_num = 0
        #msg[[95,1],[50,1],[],[],[]....]
        for node, servo in zip(self.msgs, servos):
            # print("node和servo的值为：",node,servo.pos)
            # node = servo.jdMin+node*(servo.jdMax-servo.jdMin)

            servo_init = {1:servo.jdMin, -1:servo.jdMax}
            node = servo_init[servo.norm] + node*(servo.jdMax - servo.jdMin) * servo.norm

            if node and node != servo.pos: # 目标位置改变
                if node != 0: # msg 没有值
                    # 限幅
                    if node > servo.jdMax:
                        node = servo.jdMax
                    if node < servo.jdMin:
                        node = servo.jdMin
                    servo.pos = node
                    node = int((node + servo.fOffSet) * servo.fScale)
                    pos_l = node & 0xFF
                    pos_h = (node >> 8) & 0x07
                    pos_h = pos_h | (servo.id<<3)
                    # print(servo.id)
                    # print(pos_h,pos_l)
                    frameData.extend([pos_h, pos_l])
                    servo_num += 1
        if servo_num == 0:
            return
        # print("servo_num的值为：",servo_num)
        num=servo_num
        frameData[1] = num
        frameData.extend([end])


        # for i in range(len(frameData)):
        #     # print("{0:0.2x} ".format(frameData[i]), end='')
        #     # print(frameData[i])
        if self.is_open:
            self.write(frameData)
            # print('send to servo ok')
    

#直接执行这个.py文件运行下边代码，import到其他脚本中下边代码不会执行
if __name__ == '__main__':
    
    ctrl = MouthCtrl('/dev/ttyACM0')
    # ctrl = MouthCtrl('COM11')


    ctrl.mouthUpperUpLeft     = 0.24   # 左上嘴唇  0.24
    ctrl.mouthUpperUpRight    = 0.24   # 右上嘴唇  0.24
    ctrl.mouthLowerDownLeft   = 0.2   # 左下嘴唇  0.2
    ctrl.mouthLowerDownRight  = 0.2   # 右下嘴唇  0.2
    
    ctrl.mouthCornerUpLeft    = 0.23   # 左上角  0.23
    ctrl.mouthCornerUpRight   = 0.23   # 右上角  0.23
    ctrl.mouthCornerDownLeft  = 0.5   # 左下角  0.5
    ctrl.mouthCornerDownRight = 0.5   # 右下角  0.5

    ctrl.jawOpenLeft         = 0.01   # 0.01
    ctrl.jawOpenRight        = 0.01   # 0.01

    ctrl.jawBackLeft          = 0.5   # 0.5  左前 [0.01 - 0.5 - 0.99] 右后
    ctrl.jawBackRight         = 0.5   # 0.5  左后 [0.01 - 0.5 - 0.99] 右前

    print(ctrl.msgs)
    ctrl.send()
    print(ctrl.msgs)
