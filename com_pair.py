import serial
import threading
from datetime import datetime
from time import sleep
import random
COLLISION_WINDOW = 0.02
SLOT_TIME = 0.04
START_BYTE = b'\x01'
END_BYTE = b'\x04'
JAM_BYTE = b'\x02'


class PairOfPorts():
    def __init__(self, port, func=(lambda string: print(string))):
        self.WritingPort = serial.Serial(port, timeout=5)
        self.ReadingPort = serial.Serial(port, timeout=5)
        read_thread = threading.Thread(target=self.read, name="reader", args=[func])
        self.need_to_read = True
        read_thread.start()

    def write(self, data):
        message = data.encode("ascii")
        message = START_BYTE + message + END_BYTE
        attempts_counter = 0
        for current in message:
            while not self.check_channel():  # Ожидание освобождения канала
                print("Канал занят.")
                sleep(0.1)
            self.WritingPort.write(current)
            sleep(COLLISION_WINDOW)
            while not self.check_collision():
                print('X', end='')
                self.WritingPort.write(JAM_BYTE)
                attempts_counter += 1
                if attempts_counter > 11:
                    raise TimeoutError
                sleep(random.random() * (2 ** max(attempts_counter, 10)))
                self.WritingPort.write(current)

    def read(self, func=(lambda string: print(string))):
        while self.need_to_read:
            message = b''
            first_byte = self.ReadingPort.read(1)
            transmission_finished = False
            transmission_started = False
            if first_byte == b'':
                continue
            while not transmission_finished:
                second_byte = self.ReadingPort.read(1)
                while second_byte == JAM_BYTE:
                    first_byte = self.ReadingPort.read(1)
                    second_byte = self.ReadingPort.read(1)
                if transmission_started:
                    message += first_byte
                elif first_byte == START_BYTE:
                    transmission_started = True
                elif first_byte == END_BYTE:
                    transmission_finished = True
                first_byte = second_byte
            if len(message):
                func(message)

    def stop(self):
        self.need_to_read = False

    @staticmethod
    def check_channel():
        if datetime.now().second % 2:
            return False
        else:
            return True

    @staticmethod
    def check_collision():
        if datetime.now().second % 2:
            return False
        else:
            return True