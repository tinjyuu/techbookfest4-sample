#!/usr/bin/sudo python
# -*- coding: utf-8 -*-
import PCA9685
import time
import logging
import firestore_helper
import threading
import signal

FRONT_LEFT_HIP = 0
FRONT_RIGHT_HIP = 1
FRONT_LEFT_LEG = 2
FRONT_RIGHT_LEG = 3
BACK_LEFT_HIP = 4
BACK_RIGHT_HIP = 5
BACK_LEFT_LEG = 6
BACK_RIGHT_LEG = 7

logger = logging.getLogger(__name__)


class SG90(object):

    def __init__(self, channel, zero_offset=0):
        self.m_channel = channel
        self.m_zero_offset = zero_offset
        self.m_pwm = PCA9685.PCA9685(address=0x40)
        self.m_pwm.set_pwm_freq(60)

    def setpos(self, pos):
        pulse = (650 - 150) * pos / 180 + 150 + self.m_zero_offset
        self.m_pwm.set_pwm(self.m_channel, 0, int(pulse))

    def cleanup(self):
        self.m_pwm.software_reset()


class OreKame(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        for i in range(1, 9):
            logger.debug(i)
        self.servos = []
        self.running = False
        self.fh = firestore_helper.FireStoreHelper()
        self.fh.start()
        self.finish = False

    def start_servo(self):
        self.servos = [SG90(channel=i) for i in range(1, 9)]
        self.servos[BACK_LEFT_HIP].m_zero_offset = -50
        self.servos[FRONT_LEFT_LEG].m_zero_offset = -40
        self.servos[BACK_RIGHT_LEG].m_zero_offset = -50
        time.sleep(1)
        self.running = True
        self.all_setpos([90, 90, 90, 90, 90, 90, 90, 90])

    def all_setpos(self, pos_list, wait=0.1):
        for s, p in zip(self.servos, pos_list):
            s.setpos(int(p))
        time.sleep(wait)

    def cleanup(self):

        logger.info("cleanup")
        for s in self.servos:
            s.cleanup()

    def walk(self):
        yield self.all_setpos([90, 45, 90, 90, 90, 135, 90, 90], wait=0.5)
        yield self.all_setpos([90, 135, 90, 45, 90, 135, 90, 90], wait=0.5)
        yield self.all_setpos([135, 90, 90, 90, 90, 90, 90, 90], wait=0.5)
        yield self.all_setpos([135, 90, 90, 90, 45, 90, 45, 90], wait=0.5)
        yield self.all_setpos([135, 90, 90, 90, 45, 90, 90, 90], wait=0.5)
        yield self.all_setpos([60, 90, 135, 90, 45, 90, 90, 90], wait=0.5)

    def run(self):
        yield self.all_setpos([90, 45, 90, 90, 90, 135, 90, 90])
        yield self.all_setpos([90, 135, 90, 45, 90, 135, 90, 90])
        yield self.all_setpos([135, 90, 90, 90, 90, 90, 90, 90])
        yield self.all_setpos([135, 90, 90, 90, 45, 90, 45, 90])
        yield self.all_setpos([135, 90, 90, 90, 45, 90, 90, 90])
        yield self.all_setpos([60, 90, 135, 90, 45, 90, 90, 90])

    def shake_arm(self):
        yield self.all_setpos([90, 90, 160, 90, 90, 90, 90, 90], wait=0.5)
        yield self.all_setpos([115, 90, 160, 90, 90, 90, 90, 90], wait=0.5)
        yield self.all_setpos([80, 90, 160, 90, 90, 90, 90, 90], wait=0.5)

    def loop(self):
        while self.fh.status == "run":

            if self.fh.command == "walk":
                for _ in self.walk():
                    if self.fh.command != "walk":
                        break
            elif self.fh.command == "run":
                for _ in self.run():
                    if self.fh.command != "run":
                        break
            elif self.fh.command == "shake_arm":
                for _ in self.shake_arm():
                    if self.fh.command != "shake_arm":
                        break
            else:
                self.all_setpos([90, 90, 90, 90, 90, 90, 90, 90])
        self.finish = True

    def signal_handler(self, number, frame):
        self.fh.running = False
        self.cleanup()
        logger.info("exit")


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    ore = OreKame()
    signal.signal(signal.SIGINT, ore.signal_handler)
    signal.signal(signal.SIGTERM, ore.signal_handler)

    logger.info("start")
    while ore.fh.running:
        if ore.running:
            ore.loop()
            ore.running = False
            ore.cleanup()
        elif ore.fh.status == "run":
            ore.start_servo()
        else:
            time.sleep(1)


if __name__ == '__main__':
    main()
