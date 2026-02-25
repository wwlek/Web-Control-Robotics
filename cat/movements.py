from machine import I2C
import time
from pca9685 import PCA9685Driver

# =========================
# CONFIG
# =========================
cat_id = "CAT_01"
pwm = PCA9685Driver(scl_pin=5, sda_pin=4, i2c_freq=400000)
pwm.set_pwm_frequency(50)
PWM_MIN = 0.5
PWM_MAX = 2.5

print("I2C devices found:", pwm.i2c.scan())

# =========================
# CHANNEL MAPPING
# =========================
FL_UPPER = 0
FL_LOWER = 4
FR_UPPER = 1
FR_LOWER = 5
BL_UPPER = 2
BL_LOWER = 6
BR_UPPER = 3
BR_LOWER = 7

# =========================
# CUSTOM ANGLES PER LEG PER PHASE
# Edit any value freely — each channel is fully independent
# STAND  = resting position
# LIFT   = leg swings forward and knee bends up
# PUSH   = leg pushes back
# =========================

# --- FRONT LEFT (channels 0 + 4) ---
FL_SH_STAND = 90
FL_SH_LIFT  = 110
FL_SH_PUSH  = 70
FL_KN_STAND = 150
FL_KN_LIFT  = 80
FL_KN_PUSH  = 120

# --- FRONT RIGHT (channels 1 + 5) ---
FR_SH_STAND = 90
FR_SH_LIFT  = 110
FR_SH_PUSH  = 70
FR_KN_STAND = 30
FR_KN_LIFT  = 80
FR_KN_PUSH  = 120

# --- BACK LEFT (channels 2 + 6) ---
BL_SH_STAND = 70  # adjust until it matches FR position
BL_SH_LIFT  = 60    # mirrored from front
BL_SH_PUSH  = 70   # mirrored from front
BL_KN_STAND = 150   # adjust until it matches FR knee
BL_KN_LIFT  = 100   # mirrored from front
BL_KN_PUSH  = 20  # mirrored from front

# --- BACK RIGHT (channels 3 + 7) ---
BR_SH_STAND = 110    # adjust until it matches FL position
BR_SH_LIFT  = 60    # mirrored from front
BR_SH_PUSH  = 70   # mirrored from front
BR_KN_STAND = 30    # reduced as requested
BR_KN_LIFT  = 80   # mirrored from front
BR_KN_PUSH  = 20    # mirrored from front

# =========================
# MOVEMENT SETTINGS
# =========================
STEP_DELAY  = 0.008  # delay between each degree (lower = faster)
SMOOTH_STEP = 2      # degrees per tick (higher = faster but less smooth)
PAUSE       = 0.25   # pause between phases

# =========================
# MOVE FOUR SERVOS SIMULTANEOUSLY
# =========================
def move_four(ch1, cur1, t1, ch2, cur2, t2, ch3, cur3, t3, ch4, cur4, t4):
    steps1 = list(range(cur1, t1, SMOOTH_STEP if t1 > cur1 else -SMOOTH_STEP))
    steps2 = list(range(cur2, t2, SMOOTH_STEP if t2 > cur2 else -SMOOTH_STEP))
    steps3 = list(range(cur3, t3, SMOOTH_STEP if t3 > cur3 else -SMOOTH_STEP))
    steps4 = list(range(cur4, t4, SMOOTH_STEP if t4 > cur4 else -SMOOTH_STEP))
    max_steps = max(len(steps1), len(steps2), len(steps3), len(steps4))
    for i in range(max_steps):
        if i < len(steps1): pwm.servo_set_angle_custom(ch1, steps1[i], PWM_MIN, PWM_MAX)
        if i < len(steps2): pwm.servo_set_angle_custom(ch2, steps2[i], PWM_MIN, PWM_MAX)
        if i < len(steps3): pwm.servo_set_angle_custom(ch3, steps3[i], PWM_MIN, PWM_MAX)
        if i < len(steps4): pwm.servo_set_angle_custom(ch4, steps4[i], PWM_MIN, PWM_MAX)
        time.sleep(STEP_DELAY)
    pwm.servo_set_angle_custom(ch1, t1, PWM_MIN, PWM_MAX)
    pwm.servo_set_angle_custom(ch2, t2, PWM_MIN, PWM_MAX)
    pwm.servo_set_angle_custom(ch3, t3, PWM_MIN, PWM_MAX)
    pwm.servo_set_angle_custom(ch4, t4, PWM_MIN, PWM_MAX)

# =========================
# SERVO CLASS
# =========================
class Servo:
    def __init__(self, driver, channel, stand_angle):
        self.driver      = driver
        self.channel     = channel
        self.stand_angle = stand_angle
        self.current     = stand_angle

    def move_smooth(self, target):
        step = SMOOTH_STEP if target > self.current else -SMOOTH_STEP
        for a in range(self.current, target, step):
            self.driver.servo_set_angle_custom(self.channel, a, PWM_MIN, PWM_MAX)
            time.sleep(STEP_DELAY)
        self.driver.servo_set_angle_custom(self.channel, target, PWM_MIN, PWM_MAX)
        self.current = target

    def move_to(self, target):
        self.driver.servo_set_angle_custom(self.channel, target, PWM_MIN, PWM_MAX)
        self.current = target

# =========================
# ROBOT CAT
# =========================
class RobotCat:
    def __init__(self, driver):
        self.FL_sh = Servo(driver, FL_UPPER, FL_SH_STAND)
        self.FL_kn = Servo(driver, FL_LOWER, FL_KN_STAND)
        self.FR_sh = Servo(driver, FR_UPPER, FR_SH_STAND)
        self.FR_kn = Servo(driver, FR_LOWER, FR_KN_STAND)
        self.BL_sh = Servo(driver, BL_UPPER, BL_SH_STAND)
        self.BL_kn = Servo(driver, BL_LOWER, BL_KN_STAND)
        self.BR_sh = Servo(driver, BR_UPPER, BR_SH_STAND)
        self.BR_kn = Servo(driver, BR_LOWER, BR_KN_STAND)

        self.all_servos = [
            self.FL_sh, self.FL_kn,
            self.FR_sh, self.FR_kn,
            self.BL_sh, self.BL_kn,
            self.BR_sh, self.BR_kn
        ]

    # ---------------------
    # STARTUP
    # ---------------------
    def startup(self):
        print(cat_id, "Snapping all to 90...")
        for s in self.all_servos:
            s.move_to(90)
        time.sleep(0.5)
        print(cat_id, "Easing into stand...")
        # Knees first for stability
        self.FL_kn.move_smooth(FL_KN_STAND)
        self.FR_kn.move_smooth(FR_KN_STAND)
        self.BL_kn.move_smooth(BL_KN_STAND)
        self.BR_kn.move_smooth(BR_KN_STAND)
        time.sleep(0.2)
        # Then shoulders
        self.FL_sh.move_smooth(FL_SH_STAND)
        self.FR_sh.move_smooth(FR_SH_STAND)
        self.BL_sh.move_smooth(BL_SH_STAND)
        self.BR_sh.move_smooth(BR_SH_STAND)
        time.sleep(0.3)
        print(cat_id, "Ready.")

    # ---------------------
    # STAND
    # ---------------------
    def stand(self):
        self.FL_kn.move_smooth(FL_KN_STAND)
        self.FR_kn.move_smooth(FR_KN_STAND)
        self.BL_kn.move_smooth(BL_KN_STAND)
        self.BR_kn.move_smooth(BR_KN_STAND)
        self.FL_sh.move_smooth(FL_SH_STAND)
        self.FR_sh.move_smooth(FR_SH_STAND)
        self.BL_sh.move_smooth(BL_SH_STAND)
        self.BR_sh.move_smooth(BR_SH_STAND)
        time.sleep(0.2)

    # ---------------------
    # STOP
    # ---------------------
    def stop(self):
        print(cat_id, "STOP")
        self.stand()

    # ---------------------
    # STEP PAIR — each leg uses its own custom angles
    # ---------------------
    def _step_pair(self,
                   sh_a, kn_a, sh_a_lift, kn_a_lift, sh_a_push, kn_a_push, sh_a_stand, kn_a_stand,
                   sh_b, kn_b, sh_b_lift, kn_b_lift, sh_b_push, kn_b_push, sh_b_stand, kn_b_stand):

        # Phase 1 — LIFT both legs simultaneously
        move_four(
            sh_a.channel, sh_a.current, sh_a_lift,
            kn_a.channel, kn_a.current, kn_a_lift,
            sh_b.channel, sh_b.current, sh_b_lift,
            kn_b.channel, kn_b.current, kn_b_lift
        )
        sh_a.current = sh_a_lift; kn_a.current = kn_a_lift
        sh_b.current = sh_b_lift; kn_b.current = kn_b_lift
        time.sleep(PAUSE)

        # Phase 2 — PUSH both legs simultaneously
        move_four(
            sh_a.channel, sh_a.current, sh_a_push,
            kn_a.channel, kn_a.current, kn_a_push,
            sh_b.channel, sh_b.current, sh_b_push,
            kn_b.channel, kn_b.current, kn_b_push
        )
        sh_a.current = sh_a_push; kn_a.current = kn_a_push
        sh_b.current = sh_b_push; kn_b.current = kn_b_push
        time.sleep(PAUSE)

        # Phase 3 — RETURN to stand
        move_four(
            sh_a.channel, sh_a.current, sh_a_stand,
            kn_a.channel, kn_a.current, kn_a_stand,
            sh_b.channel, sh_b.current, sh_b_stand,
            kn_b.channel, kn_b.current, kn_b_stand
        )
        sh_a.current = sh_a_stand; kn_a.current = kn_a_stand
        sh_b.current = sh_b_stand; kn_b.current = kn_b_stand
        time.sleep(PAUSE)

    # ---------------------
    # FORWARD STEP
    # Pair A: FL + BR
    # Pair B: FR + BL
    # ---------------------
    def forward_step(self):
        # FL + BR
        self._step_pair(
            self.FL_sh, self.FL_kn,
            FL_SH_LIFT, FL_KN_LIFT, FL_SH_PUSH, FL_KN_PUSH, FL_SH_STAND, FL_KN_STAND,
            self.BR_sh, self.BR_kn,
            BR_SH_LIFT, BR_KN_LIFT, BR_SH_PUSH, BR_KN_PUSH, BR_SH_STAND, BR_KN_STAND
        )
        # FR + BL
        self._step_pair(
            self.FR_sh, self.FR_kn,
            FR_SH_LIFT, FR_KN_LIFT, FR_SH_PUSH, FR_KN_PUSH, FR_SH_STAND, FR_KN_STAND,
            self.BL_sh, self.BL_kn,
            BL_SH_LIFT, BL_KN_LIFT, BL_SH_PUSH, BL_KN_PUSH, BL_SH_STAND, BL_KN_STAND
        )

    # ---------------------
    # WALK FORWARD
    # ---------------------
    def walk_forward(self, steps=6):
        print(cat_id, "WALKING FORWARD", steps, "steps")
        for i in range(steps):
            print(cat_id, "step", i + 1, "/", steps)
            self.forward_step()
        print(cat_id, "WALK COMPLETE")
        self.stand()

    # ---------------------
    # LEFT
    # ---------------------
    def left_step(self):
        print(cat_id, "LEFT")
        self._step_pair(
            self.FL_sh, self.FL_kn,
            FL_SH_LIFT, FL_KN_LIFT, FL_SH_PUSH, FL_KN_PUSH, FL_SH_STAND, FL_KN_STAND,
            self.BL_sh, self.BL_kn,
            BL_SH_LIFT, BL_KN_LIFT, BL_SH_PUSH, BL_KN_PUSH, BL_SH_STAND, BL_KN_STAND
        )

    # ---------------------
    # RIGHT
    # ---------------------
    def right_step(self):
        print(cat_id, "RIGHT")
        self._step_pair(
            self.FR_sh, self.FR_kn,
            FR_SH_LIFT, FR_KN_LIFT, FR_SH_PUSH, FR_KN_PUSH, FR_SH_STAND, FR_KN_STAND,
            self.BR_sh, self.BR_kn,
            BR_SH_LIFT, BR_KN_LIFT, BR_SH_PUSH, BR_KN_PUSH, BR_SH_STAND, BR_KN_STAND
        )

    # ---------------------
    # DANCE
    # ---------------------
    def dance_step(self):
        print(cat_id, "DANCE")
        for _ in range(2):
            self._step_pair(
                self.FL_sh, self.FL_kn,
                FL_SH_LIFT, FL_KN_LIFT, FL_SH_PUSH, FL_KN_PUSH, FL_SH_STAND, FL_KN_STAND,
                self.BR_sh, self.BR_kn,
                BR_SH_LIFT, BR_KN_LIFT, BR_SH_PUSH, BR_KN_PUSH, BR_SH_STAND, BR_KN_STAND
            )
            self._step_pair(
                self.FR_sh, self.FR_kn,
                FR_SH_LIFT, FR_KN_LIFT, FR_SH_PUSH, FR_KN_PUSH, FR_SH_STAND, FR_KN_STAND,
                self.BL_sh, self.BL_kn,
                BL_SH_LIFT, BL_KN_LIFT, BL_SH_PUSH, BL_KN_PUSH, BL_SH_STAND, BL_KN_STAND
            )
        self.stand()

    # ---------------------
    # CALIBRATE — test one channel at a time
    # ---------------------
    def calibrate(self):
        print("--- CALIBRATION MODE ---")
        print("Format: ch <channel> <angle>  e.g. 'ch 2 100'")
        print("Type 'exit' to leave calibration")
        while True:
            cmd = input("cal>> ").strip().lower()
            if cmd == "exit":
                break
            parts = cmd.split()
            if len(parts) == 3 and parts[0] == "ch":
                try:
                    ch    = int(parts[1])
                    angle = int(parts[2])
                    pwm.servo_set_angle_custom(ch, angle, PWM_MIN, PWM_MAX)
                    print(f"Channel {ch} -> {angle} degrees")
                except:
                    print("Invalid input. Try: ch 2 100")
            else:
                print("Format: ch <channel> <angle>  e.g. 'ch 2 100'")

# =========================
# START
# =========================
cat = RobotCat(pwm)
cat.startup()
print("Commands: forward [steps] | left | right | dance | stop | calibrate")

while True:
    cmd = input(">> ").strip().lower()
    if cmd.startswith("forward"):
        parts = cmd.split()
        steps = int(parts[1]) if len(parts) > 1 else 6
        cat.walk_forward(steps=steps)
    elif cmd == "left":
        cat.left_step()
    elif cmd == "right":
        cat.right_step()
    elif cmd == "dance":
        cat.dance_step()
    elif cmd == "stop":
        cat.stop()
    elif cmd == "calibrate":
        cat.calibrate()
    else:
        print("Unknown command. Try: forward [steps] | left | right | dance | stop | calibrate")
