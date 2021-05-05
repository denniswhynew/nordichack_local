from guizero import App, Text, PushButton, Box
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
import time

#define values
PWM_PIN = 18
#SPEED_SENSE_PIN = 17
#SAFETY_SENSE_PIN = 27
INCLINE_UP_PIN = 20
INCLINE_DOWN_PIN = 21
#INCLINE_SENSE_PIN = 16
speed = 0   #run speed
Hour = 0    #run timer Hour
Minute = 0  #run timer Minute
Second = 0  #run timer Second
isStart = False
MULTIPLY = 7
DISTANCE = 0
tiktok = False
BTN_font_size = 20
#end of define values

#control run speed
def set_speed(sp):
    global speed
    prev_speed = speed
    if sp == 1 and speed <= 12:
        speed = speed+1
    elif sp == -1 and speed >=1:
        speed = speed-1
    else:
        speed = sp
    if speed >= 13:
        speed = 13
    elif speed <= 0:
        speed = 0
    if speed == 0:
        B_start.cancel(timer)
        isStart = False
    if prev_speed == 0 and speed > 0:
        B_start.repeat(500, timer)
    writepwm()

def start_run():
    global speed, app, Hour, Minute, Second, DISTANCE
    if speed == 0:
        motor.start(0)
        speed = 2
        writepwm()
        isStart = True
        Hour = 0
        Minute = 0
        Second = 0
        DISTANCE = 0
        B_start.repeat(500, timer)
    else:
        pass

def stop_run():
    global speed
    speed = 0
    writepwm()
    #motor.stop()
    B_start.cancel(timer)
    #chan_list = [PWM_PIN, INCLINE_UP_PIN, INCLINE_DOWN_PIN]
    #GPIO.cleanup(chan_list)

def pause_loop():
    pass

def incline(direction):
    global INCLINE_DOWN_PIN
    global INCLINE_UP_PIN
    if direction == 1:
        GPIO.output(INCLINE_DOWN_PIN, 0)
        GPIO.output(INCLINE_UP_PIN, 1)
    elif direction == 0:
        GPIO.output(INCLINE_UP_PIN, 0)
        GPIO.output(INCLINE_DOWN_PIN, 0)
    elif direction == -1:
        GPIO.output(INCLINE_UP_PIN, 0)
        GPIO.output(INCLINE_DOWN_PIN, 1)

def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(PWM_PIN, GPIO.OUT)   # motor pwm output
    GPIO.setup(SPEED_SENSE_PIN, GPIO.IN)   # speed pwm input
    GPIO.setup(SAFETY_SENSE_PIN, GPIO.IN)   # safety key input
    GPIO.setup(INCLINE_UP_PIN, GPIO.OUT, initial = GPIO.LOW)   # incline up output
    GPIO.setup(INCLINE_DOWN_PIN, GPIO.OUT, initial = GPIO.LOW)   # incline down output
    GPIO.setup(INCLINE_SENSE_PIN, GPIO.IN)   # incline sensor input

def writepwm():
    realspeed = speed * MULTIPLY
    if realspeed < 0.0 or realspeed > 91.0:
        if realspeed > 91:
            realspeed = 91
        elif realspeed < 0:
            realspeed = 0
        motor.ChangeDutyCycle(realspeed)
    elif realspeed-0.0 < 1e-3:
        motor.ChangeDutyCycle(0)
    else:
        motor.ChangeDutyCycle(realspeed)
    #add sleep
    text_speed.value = str(speed)+" km/h"

def timer():
    global Hour, Minute, Second, DISTANCE, tiktok
    if tiktok == True:
        Second = Second + 1
    if Second % 60 == 0 and Second != 0:
        Second = 0
        Minute += 1
    if Minute % 60 == 0 and Minute != 0:
        Hour += 1
    text_time.value = str(Hour) + " h:" + str(Minute) + " m:" + str(Second) + " s"

    if Hour > 24:
        text_time.value = "You Run Over 24HR WTF?"

    DISTANCE += (speed * 700)/60/60
    output_speed = f"{DISTANCE:.1f}"
    text_distance.value = str(output_speed) + " m"

    tiktok = not tiktok
#def shutdown()
#def readSpeedFrequency()

init()
motor = GPIO.PWM(PWM_PIN, 20)   # 20Hz
motor.start(0)

app = App(title="Nordichack", layout = "grid", width = 800) #when_close = shutdown()
#app.full_screen = True
welcome_message = Text(app, text = "Welcome to Nordichack!", size = 30, grid = [1,0,2,1], height = 2, width = 29, align = "top")
welcome_message.font = "Digital-7"
box_mid_upper = Box(app, border = 2, grid = [1,1,2,3])
#start mid upper area
MUH = 3
MUW = 20
MU_font = "Digital-7"
text_speed = Text(box_mid_upper, text = "0 km/h", size = 40, font = MU_font, height = MUH, width = MUW)
text_time = Text(box_mid_upper, text = "0 h:0 m:0 s", size = 40, font = MU_font, height = MUH, width = MUW)
text_distance = Text(box_mid_upper, text = "0 m", size = 40, font = MU_font, height = MUH, width = MUW)
#end mid upper area

box_mid_lower = Box(app, layout = "grid", border = 2, grid = [1,4,2,2])
#start mid lower area
MLH = 2
MLW = 5
MLBFS = BTN_font_size

B_decrease_speed = PushButton(box_mid_lower, command = lambda: set_speed(-1), text = "<<", grid = [0,0], height = MLH, width = MLW)
B_stop = PushButton(box_mid_lower, command = stop_run, text = "STOP", grid = [1,0], height = MLH, width = MLW)
B_start = PushButton(box_mid_lower, command = start_run, text = "START", grid = [2,0], height = MLH, width = MLW)
B_increase_speed = PushButton(box_mid_lower, command = lambda: set_speed(1), text = ">>", grid = [3,0], height = MLH, width = MLW)

B_start.bg = "green"
B_stop.bg = "red"
MLBTN = [B_decrease_speed, B_stop, B_start, B_increase_speed]
for btn in MLBTN:
    btn.text_size = MLBFS
#end mid lower area

box_right = Box(app, layout = "grid", border = 2, height = "fill", grid = [3,0,1,6])
#start right area
RH = 1
RW = 5
RBFS = BTN_font_size+4
Rpady = 12

B12= PushButton(box_right, command = lambda: set_speed(12), text = "12", grid = [0,0], height = RH, width = RW, pady = Rpady)
B10= PushButton(box_right, command = lambda: set_speed(10), text = "10", grid = [0,1], height = RH, width = RW, pady = Rpady)
B8 = PushButton(box_right, command = lambda: set_speed(8), text = "8", grid = [0,2], height = RH, width = RW, pady = Rpady)
B6 = PushButton(box_right, command = lambda: set_speed(6), text = "6", grid = [0,3], height = RH, width = RW, pady = Rpady)
B4 = PushButton(box_right, command = lambda: set_speed(4), text = "4", grid = [0,4], height = RH, width = RW, pady = Rpady)
B2 = PushButton(box_right, command = lambda: set_speed(2), text = "2", grid = [0,5], height = RH, width = RW, pady = Rpady)

RBTN = [B12, B10, B8, B6, B4, B2]
for btn in RBTN:
    btn.text_size = RBFS
#end right area

box_left = Box(app, layout = "grid", border = 2, height = "fill", grid = [0,0,1,6])
#start left area
LH = 3
LW = 5
LBFS = BTN_font_size+4

B_rise = PushButton(box_left, command = lambda: incline(1), text = "↑", grid = [0,0], height = LH, width = LW)
B_stop_incline = PushButton(box_left, command = lambda: incline(0), text = "□", grid = [0,1], height = LH, width = LW)
B_decline = PushButton(box_left, command = lambda: incline(-1), text = "↓", grid = [0,2], height = LH, width = LW)

B_stop_incline.bg = "red"
LBTN = [B_rise, B_stop_incline, B_decline]
for btn in LBTN:
    btn.text_size = LBFS
#end left area

app.display()
