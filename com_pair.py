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
        self.WritingPort = serial.Serial(port, timeout=1)
        self.ReadingPort = serial.Serial(port, timeout=1)
        read_thread = threading.Thread(target=self.read, name="reader", args=[func])
        self.need_to_read = True
        read_thread.start()

    def write(self, data):
        message = data.encode("ascii")
        message = START_BYTE + message + END_BYTE
        for current in message:
            while not self.check_channel():  # Ожидание освобождения канала
                print("Канал занят.")
                sleep(0.1)
            try:
                self.WritingPort.write([current])
            except serial.SerialException:
                print("You write the wrong byte: '{}', baka!".format(bytes([current])))
            print(chr(current))
            sleep(COLLISION_WINDOW)
            attempts_counter = 0
            while not self.check_collision():
                self.WritingPort.write(JAM_BYTE)
                attempts_counter += 1
                if attempts_counter > 11:
                    raise TimeoutError
                time_to_wait = random.random() * SLOT_TIME * (2 ** min(attempts_counter, 10))
                print('Коллизия. Генерация случайного числа в интервале 0 - {}. Ожидание {} секунд.'.format(
                    SLOT_TIME * 2 ** min(attempts_counter, 10), time_to_wait))
                sleep(time_to_wait)
                self.WritingPort.write([current])

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
                if first_byte == START_BYTE:
                    transmission_started = True
                elif first_byte == END_BYTE:
                    transmission_finished = True
                elif transmission_started:
                    message += first_byte
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
        if datetime.now().microsecond % 2:
            return False
        else:
            return True