import tkinter as tk
from tkinter import Scale, Button, HORIZONTAL

# from utils.servo.HeadCtrlKit_v2 import HeadCtrl
from HeadCtrlKit_v2 import HeadCtrl

ctrl = HeadCtrl('/dev/ttyACM1')


class ServoControlApp:
    def __init__(self, master):
        self.master = master
        master.title("Servo Control Panel")

        self.servo_values = {
            "left_blink": tk.DoubleVar(),
            "left_eye_erect": tk.DoubleVar(),
            "left_eye_level": tk.DoubleVar(),
            "left_eyebrow_erect": tk.DoubleVar(),
            "left_eyebrow_level": tk.DoubleVar(),
            "right_blink": tk.DoubleVar(),
            "right_eye_erect": tk.DoubleVar(),
            "right_eye_level": tk.DoubleVar(),
            "right_eyebrow_erect": tk.DoubleVar(),
            "right_eyebrow_level": tk.DoubleVar(),
            "head_dian": tk.DoubleVar(),
            "head_yao": tk.DoubleVar(),
            "head_bai": tk.DoubleVar()
        }

        row = 0
        for servo, var in self.servo_values.items():
            Scale(master, from_=0, to=1, orient=HORIZONTAL, resolution=0.01, label=servo, variable=var,
                  command=self.update_servo).grid(row=row, column=0, sticky="ew")
            row += 1

        Button(master, text="Reset All", command=self.reset_all).grid(row=row, column=0, sticky="ew")

    def update_servo(self, event=None):
        # Set all servo control values
        for servo, var in self.servo_values.items():
            setattr(ctrl, servo, var.get())

        # Send updated values to the servo controller
        ctrl.send()

    def reset_all(self):
        reset_list = [0.47, 0.5, 0.5, 0.01, 0.01, 0.47, 0.5, 0.5, 0.01, 0.99, 0.53, 0.5, 0.5]
        for var in self.servo_values.values():
            # var.set(0)
            var.set(reset_list.pop(0))
        self.update_servo()

if __name__ == "__main__":
    root = tk.Tk()
    app = ServoControlApp(root)
    root.mainloop()
