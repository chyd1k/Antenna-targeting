from ArduinoCall import ArduinoMessenger
from SatellitesPositions import SatellitesManager

import sys
from time import sleep
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui  import QColor, QDoubleValidator


class TrackingThread(QThread):
    """
    Класс потока для выполнения отслеживания в фоновом режиме.
    """
    update_tracking = pyqtSignal()  # Сигнал для перерасчёта
    
    def __init__(self):
        super().__init__()
        self.tracking_mode = False  # Флаг для управления выполнением потока


    def run(self):
        """
        Основной метод потока. Здесь выполняется длительная операция.
        """
        while self.tracking_mode:
            self.update_tracking.emit()  # Отправляем обновление в интерфейс
            sleep(0.25)


# class AntennaDialog(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.initUI()

class AntennaDialog(QDialog):
    def __init__(self, parent = None):
        super(AntennaDialog, self).__init__(parent)
        self.initUI()

        # Текущее положение антенны
        self.running_aim_az = 0.
        self.running_aim_alt = 0.

        # Расположение точки, с которой ведется наблюдение
        self.local_position_lat = 55.903243
        self.local_position_lon = 37.641497

        self.latitude_input.setText(str(self.local_position_lat))
        self.longitude_input.setText(str(self.local_position_lon))

        self.__COM_PORTS = ['COM1', 'COM2', 'COM3', 'COM4', 'COM5']
        self.combo1.addItems(self.__COM_PORTS)
        
        # Создание ArduinoMessenger
        self.arduino_messenger = ArduinoMessenger()
        self.arduino_messenger.show_avaliable_ports()

        # Создание SatellitesManager
        self.satellites_manager = SatellitesManager()
        # satellites_manager.print_satellites_info()
        satellites_names = self.satellites_manager.get_satellites_names()
        self.combo2.setStyleSheet("""QComboBox QAbstractItemView {
        color: red;
        }
        QComboBox {
            color: rgb(255, 149, 0 );
        }""")
        self.combo2.addItems(satellites_names)

        # Словарь углов и дальности для каждого аппарата на момент запуска приложения
        self.az_alt_dist = {}
        for i in range(len(satellites_names)):
            az, alt, dist = self.satellites_manager.get_aim_degrees(satellites_names[i], self.local_position_lat, self.local_position_lon)
            self.az_alt_dist[i] = [az, alt, dist]
            if alt > 0:
                self.combo2.setItemData(i, QColor("green"), Qt.TextColorRole)
        self.update_aim_parameters(0)

        self.combo2.currentIndexChanged.connect(self.on_combo2_change)  # Подключение сигнала

        if (len(self.arduino_messenger.ports) == 0):
            msg_box = QMessageBox()
            msg_box.setText("Доступных COM-портов не обнаружено!")
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("Внимание!")
            msg_box.exec_()


    def initUI(self):
        # Установка заголовка и размера окна
        self.setWindowTitle('Управление антенной')
        self.setGeometry(100, 100, 400, 250)

        # Создание вертикального макета
        layout = QVBoxLayout()

        # Создание первого ComboBox с 3 вариантами
        self.combo1 = QComboBox(self)
        layout.addWidget(QLabel('Выберите COM-порт:'))
        layout.addWidget(self.combo1)

        self.combo2 = QComboBox(self)
        layout.addWidget(QLabel('Выберите КА:'))
        layout.addWidget(self.combo2)

        # Создание LineEdit для ввода широты
        self.latitude_input = QLineEdit(self)
        self.latitude_input.setPlaceholderText('Введите широту')

        # Установка валидатора для ввода только вещественных чисел
        validator = QDoubleValidator(-90.0, 90.0, 6)  # Ограничение по диапазону широты
        self.latitude_input.setValidator(validator)

        layout.addWidget(QLabel('Широта:'))
        layout.addWidget(self.latitude_input)

        # Подключение сигнала изменения текста к функции обновления переменной
        self.latitude_input.textChanged.connect(self.update_latitude)

        # Создание LineEdit для ввода долготы
        self.longitude_input = QLineEdit(self)
        self.longitude_input.setPlaceholderText('Введите долготу')

        # Установка валидатора для ввода только вещественных чисел
        validator2 = QDoubleValidator(-180.0, 180.0, 6)  # Ограничение по диапазону широты
        self.longitude_input.setValidator(validator2)

        layout.addWidget(QLabel('Долгота:'))
        layout.addWidget(self.longitude_input)

        # Подключение сигнала изменения текста к функции обновления переменной
        self.longitude_input.textChanged.connect(self.update_longitude)

        # Создание горизонтального макета для вывода значений
        output_layout = QHBoxLayout()

        # LineEdit для вывода азимута
        self.azimuth_output = QLineEdit(self)
        self.azimuth_output.setPlaceholderText('Азимут')
        # self.azimuth_output.setReadOnly(True)  # Делаем поле только для чтения
        self.azimuth_output.setAlignment(Qt.AlignLeft)
        output_layout.addWidget(QLabel('Азимут:'))
        output_layout.addWidget(self.azimuth_output)

        # LineEdit для вывода угла высоты
        self.elevation_output = QLineEdit(self)
        self.elevation_output.setPlaceholderText('Угол высоты')
        # self.elevation_output.setReadOnly(True)  # Делаем поле только для чтения
        self.elevation_output.setAlignment(Qt.AlignLeft)
        output_layout.addWidget(QLabel('Угол высоты:'))
        output_layout.addWidget(self.elevation_output)

        # LineEdit для вывода дистанции
        self.distance_output = QLineEdit(self)
        self.distance_output.setPlaceholderText('Дистанция')
        self.distance_output.setReadOnly(True)  # Делаем поле только для чтения
        self.distance_output.setAlignment(Qt.AlignLeft)
        output_layout.addWidget(QLabel('Дистанция:'))
        output_layout.addWidget(self.distance_output)

        # Добавляем горизонтальный макет в основной макет
        layout.addLayout(output_layout)

        # Создание горизонтального макета для кнопок "Обновить" и "Отслеживать"
        button_layout = QHBoxLayout()

        # Кнопка для подтверждения ввода
        self.refresh_button = QPushButton('Обновить', self)
        
        # Подключение сигнала clicked к функции обработчику
        self.refresh_button.clicked.connect(self.on_refresh)
        
        button_layout.addWidget(self.refresh_button)

        # Кнопка "Отслеживать"
        self.track_button = QPushButton('Отслеживать', self)
        
        # Подключение сигнала clicked к функции обработчику (можно создать отдельный метод)
        self.track_button.clicked.connect(self.on_track)
        
        button_layout.addWidget(self.track_button)

        # Добавляем горизонтальный макет кнопок в основной макет
        layout.addLayout(button_layout)

        # Установка макета в виджет
        self.setLayout(layout)

        # Инициализация потока отслеживания
        self.tracking_thread = TrackingThread()
        self.tracking_thread.update_tracking.connect(self.update_track)  # Подключаем сигнал

        self.user_aim = QPushButton('Ручная наводка', self)
        self.user_aim.clicked.connect(self.on_user_aim)
        layout.addWidget(self.user_aim)

    
    def closeEvent(self, event):
        """
        Обработка события закрытия окна.
        Здесь можно выполнить действия перед закрытием приложения.
        """
        self.tracking_thread.tracking_mode = False
        self.running_aim_az = 0.
        self.running_aim_alt = 0.
        self.arduino_messenger.aim_on_satellite(self.running_aim_az, self.running_aim_alt)
        event.accept()  # Принять событие закрытия


    def update_aim_parameters(self, ind: int):
        # Вывод результатов в соответствующие поля
        self.azimuth_output.setText(str(self.az_alt_dist[ind][0]))
        self.elevation_output.setText(str(self.az_alt_dist[ind][1]))
        self.distance_output.setText(str(self.az_alt_dist[ind][2]))

        self.azimuth_output.setCursorPosition(0)
        self.elevation_output.setCursorPosition(0)
        self.distance_output.setCursorPosition(0)


    def update_latitude(self):
        """
        Обновление переменной local_position_lat при изменении текста в latitude_input.
        """
        try:
            text_value = self.latitude_input.text()
            if text_value:  # Проверяем, что строка не пустая
                self.local_position_lat = float(text_value)  # Обновляем переменную на введенное значение
            else:
                self.local_position_lat = 0.0  # Если поле пустое, сбрасываем значение на ноль
                self.latitude_input.setText(str(self.local_position_lat))
        except ValueError:
            pass  # Игнорируем ошибки преобразования


    def update_longitude(self):
        """
        Обновление переменной local_position_lon при изменении текста в longitude_input.
        """
        try:
            text_value = self.longitude_input.text()
            if text_value:  # Проверяем, что строка не пустая
                self.local_position_lon = float(text_value)  # Обновляем переменную на введенное значение
            else:
                self.local_position_lon = 0.0  # Если поле пустое, сбрасываем значение на ноль
                self.longitude_input.setText(str(self.local_position_lon))
        except ValueError:
            pass  # Игнорируем ошибки преобразования


    def on_refresh(self):
        """
        Обработчик нажатия кнопки 'Обновить'.
        """
        ind = self.combo2.currentIndex()
        satellite_name = self.combo2.itemText(ind)
        az, alt, dist = self.satellites_manager.get_aim_degrees(satellite_name, self.local_position_lat, self.local_position_lon)
        self.az_alt_dist[ind] = [az, alt, dist]
        self.update_aim_parameters(ind)
    

    def on_combo2_change(self):
        """
        Обработчик изменения выбранного значения во втором ComboBox.
        """
        ind = self.combo2.currentIndex()
        # Вывод результатов в соответствующие поля
        self.update_aim_parameters(ind)


    def aim_start(self):
        # Текущее положение антенны
        self.running_aim_az = float(self.azimuth_output.text())
        self.running_aim_alt = float(self.elevation_output.text())
        self.arduino_messenger.aim_on_satellite(self.running_aim_az, self.running_aim_alt)


    def update_track(self):
        self.on_refresh()
        self.aim_start()

    
    def on_user_aim(self):
        if (len(self.arduino_messenger.ports) == 0):
            return
        
        port_name = self.__COM_PORTS[self.combo1.currentIndex()]
        if (self.arduino_messenger.is_port_active()):
            if (port_name != self.arduino_messenger.get_active_port_name()):
                self.arduino_messenger.disactivate_port()
                self.arduino_messenger.set_active_port(port_name)
        else:
            self.arduino_messenger.set_active_port(port_name)
        self.aim_start()


    def on_track(self):
        """
        Обработчик нажатия кнопки 'Отслеживать'.
        """
        self.combo1.setEnabled(self.tracking_thread.tracking_mode)
        self.combo2.setEnabled(self.tracking_thread.tracking_mode)
        self.latitude_input.setEnabled(self.tracking_thread.tracking_mode)
        self.longitude_input.setEnabled(self.tracking_thread.tracking_mode)

        if (self.tracking_thread.tracking_mode):
            self.tracking_thread.tracking_mode = False
            self.track_button.setText("Отслеживать")
            if (len(self.arduino_messenger.ports) != 0):
                self.arduino_messenger.disactivate_port()
            return

        self.track_button.setText("Остановить отслеживание")
        self.tracking_thread.tracking_mode = True
        if (len(self.arduino_messenger.ports) != 0):
            self.arduino_messenger.set_active_port(self.__COM_PORTS[self.combo1.currentIndex()])
        
        if not self.tracking_thread.isRunning():  # Проверяем, что поток не запущен уже
            self.tracking_thread.start()  # Запускаем поток



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AntennaDialog()
    ex.show()
    sys.exit(app.exec_())

# if __name__ == "__main__":
#     arduino_messenger = ArduinoMessenger()
#     if (len(arduino_messenger.ports)) == 0:
#         print("No avaliable ports found!\n")

#     arduino_messenger.set_active_port("COM3")

#     satellites_manager = SatellitesManager()
    
#     satellite_name = "KONDOR-FKA NO. 2"
#     local_position_lat = 55.903243
#     local_position_lon = 37.641497
    
#     az, al, dist = satellites_manager.get_aim_degrees(satellite_name, local_position_lat, local_position_lon)




    # # get list of satellites
    # active_satellites = []
    # # get list of avalible ports
    # avalible_ports = []

    # # interface
    # satellite_pos = get_satellite_pos() # 5
    # local_position_lat = get_local_position_lat() # 49.5
    # local_position_lon = get_local_position_lon() # 52.7

    # # interface
    # choosen_port = get_choosen_port()

    # # SatellitesPositions
    # az, ugol_mesta = get_aim_degrees(satellite_pos, local_position_lat, local_position_lon)

    # # Moove antenna
    # aim_on_satellite(az, ugol_mesta)
    


    # # getPorts()

    # # Открываем Serial порт ('COMX' замените на имя вашего порта)
    # ser = serial.Serial('COM3', 9600)
    # sleep(start_timer)

    # while True:
    #     str = input("Write your msg:\n")
    #     if str == "":
    #         break
    #     send_msg(str)
    #     wait_for_responce()
    # # Закрываем порт
    # ser.close()

    # #result = bytes.fromhex("1B")
    # #print("12345678910_".encode() + result)