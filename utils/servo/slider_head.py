import tkinter as tk
from tkinter import Scale, Button, HORIZONTAL

# from utils.servo.MouthCtrlKit_v2 import MouthCtrl
from MouthCtrlKit_v2 import MouthCtrl

ctrl = MouthCtrl('/dev/ttyACM0')


class ServoControlApp:
    def __init__(self, master):
        self.master = master
        master.title("Servo Control Panel")

        self.servo_values = {
            "mouthUpperUpLeft": tk.DoubleVar(),
            "mouthUpperUpRight": tk.DoubleVar(),
            "mouthLowerDownLeft": tk.DoubleVar(),
            "mouthLowerDownRight": tk.DoubleVar(),
            "mouthCornerUpLeft": tk.DoubleVar(),
            "mouthCornerUpRight": tk.DoubleVar(),
            "mouthCornerDownLeft": tk.DoubleVar(),
            "mouthCornerDownRight": tk.DoubleVar(),
            "jawOpenLeft": tk.DoubleVar(),
            "jawOpenRight": tk.DoubleVar(),
            "jawBackLeft": tk.DoubleVar(),
            "jawBackRight": tk.DoubleVar()
        }

        row = 0
        for servo, var in self.servo_values.items():
            Scale(master, from_=0, to=1, orient=HORIZONTAL, resolution=0.01, length=300，label=servo, variable=var,
                  command=self.update_servo).grid(row=row, column=0, sticky="ew")
            row += 1

        Button(master, text="Reset All", command=self.reset_all).grid(row=row, column=0, sticky="ew")

    def update_servo(self, event=None):
        # Update servo control object and send command
        ctrl.mouthUpperUpLeft     = self.servo_values["mouthUpperUpLeft"].get()
        ctrl.mouthUpperUpRight    = self.servo_values["mouthUpperUpRight"].get()
        ctrl.mouthLowerDownLeft   = self.servo_values["mouthLowerDownLeft"].get()
        ctrl.mouthLowerDownRight  = self.servo_values["mouthLowerDownRight"].get()
        
        ctrl.mouthCornerUpLeft    = self.servo_values["mouthCornerUpLeft"].get()
        ctrl.mouthCornerUpRight   = self.servo_values["mouthCornerUpRight"].get()
        ctrl.mouthCornerDownLeft  = self.servo_values["mouthCornerDownLeft"].get()
        ctrl.mouthCornerDownRight = self.servo_values["mouthCornerDownRight"].get()

        ctrl.jawOpenLeft          = self.servo_values["jawOpenLeft"].get()
        ctrl.jawOpenRight         = self.servo_values["jawOpenRight"].get()
        
        ctrl.jawBackLeft          = self.servo_values["jawBackLeft"].get()
        ctrl.jawBackRight         = self.servo_values["jawBackRight"].get()

        ctrl.send()

    def reset_all(self):
        reset_list = [0.24, 0.24, 0.2, 0.2, 0.23, 0.23, 0.5, 0.5, 0.01, 0.01, 0.5, 0.5]
        for var in self.servo_values.values():
            # var.set(0)
            var.set(reset_list.pop(0))
        self.update_servo()

if __name__ == "__main__":
    root = tk.Tk()
    app = ServoControlApp(root)


    root.mainloop()
