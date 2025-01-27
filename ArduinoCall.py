import serial
import serial.tools.list_ports
from time import sleep


class ArduinoMessenger:

    def __init__(self):
        self.__ESC_Character = bytes.fromhex("1B") # byte value of Esc
        self.__start_timer = 5
        self.__port_is_active = False
        self.__active_port_name = ""

        self.__serial_port = None # active serial port

        # Getting the list of available Serial ports
        self.ports = list(serial.tools.list_ports.comports())
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.disactivate_port()

    def __send_msg(self, message: str):
        if (self.__port_is_active is False or self.__serial_port is None):
            # print("Error, port is not active!\n")
            return
        self.__serial_port.write(message.encode() + self.__ESC_Character)
        self.__serial_port.flushInput()

    def __wait_for_responce(self):
        if (self.__port_is_active is False or self.__serial_port is None):
            # print("Error, port is not active!\n")
            return
        # Reading the response from Arduino via the Serial port
        response = self.__serial_port.readline()
        # Decoding the response from bytes to a string using UTF-8
        decoded_response = response.decode('utf-8')
        print(decoded_response)
        
    def show_avaliable_ports(self):
        if (len(self.ports) == 0):
            print(f"Доступных COM-портов не обнаружено!")
        # Print info about each port
        for port in self.ports:
            print(f"Порт: {port.device}")
            print(f"Описание: {port.description}")
            print(f"Производитель: {port.manufacturer}\n")

    def is_port_active(self):
        return self.__port_is_active
    
    def get_active_port_name(self):
        return self.__active_port_name

    def set_active_port(self, port_name: str):
        # Close port
        if (self.__port_is_active and self.__serial_port is not None):
            self.__serial_port.close()
        self.__port_is_active = False
        
        # Open serial port
        self.__serial_port = serial.Serial(port_name, 9600)
        sleep(self.__start_timer)

        self.__port_is_active = True
        self.__active_port_name = port_name
        return True
    
    def disactivate_port(self):
        if (self.__port_is_active and self.__serial_port is not None):
            self.__serial_port.close()
        self.__port_is_active = False

    def aim_on_satellite(self, az: float, ugol_mesta: float):
        message = f"A{az}U{ugol_mesta}"
        self.__send_msg(message)
        # self.__wait_for_responce()
