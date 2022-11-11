import sys
import wmi
import speedtest
import subprocess

from user_exceptions import NoFileName
from PyQt5 import QtCore, uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("design.ui", self)
        self.connect_buttons()
        self.setWindowIcon(QIcon("icon.png"))
        self.setWindowTitle("Показометр скорости интернета и параметров компьютера")

        self.total_hardware_list = []
        self.total_internet_list = []
        self.hardware_filename = ""
        self.internet_filename = ""
    
    def connect_buttons(self):
        self.display_hardware_btn.clicked.connect(self.display_hardware)
        self.write_hardware_btn.clicked.connect(self.write_hardware)
        self.choose_all_hardware_btn.clicked.connect(self.choose_all_hardware)
        self.display_internet_btn.clicked.connect(self.display_internet)
        self.write_internet_btn.clicked.connect(self.write_internet)
        self.choose_all_internet_btn.clicked.connect(self.choose_all_internet)
    
    def display_hardware(self):
        self.hardware_error_label.setText("")
        self.set_hardware_list()
        self.hardware_listwidget.clear()
        self.hardware_listwidget.addItems(self.total_hardware_list)

    def write_hardware(self):
        self.hardware_error_label.setText("")
        self.hardware_error_label.setStyleSheet("color: red")
        self.hardware_filename = self.hardware_filename_lineedit.text()

        if not self.hardware_filename:
            self.hardware_error_label.setText("Введите имя файла!")
            return
        try:
            if not self.hardware_filename:
                raise NoFileName

            if len(self.hardware_filename.split(".")) == 1:
                self.hardware_filename += ".txt"
            elif len(self.hardware_filename.split(".")) == 1 and\
                    not self.hardware_filename.split(".")[1]:
                self.hardware_filename += "txt"
            
            with open(self.hardware_filename, 'w') as text_file:
                self.set_hardware_list()

                for parameter in self.total_hardware_list:
                    text_file.write(parameter + "\n")
                
                self.hardware_error_label.setStyleSheet("color: green")
                self.hardware_error_label.setText("Готово!")
        except NoFileName:
            self.hardware_error_label.setText("Вы забыли написать имя файла!")

    def choose_all_hardware(self):
        self.manufacturer_box.setChecked(True)
        self.pc_model_box.setChecked(True)
        self.os_name_box.setChecked(True)
        self.os_version_box.setChecked(True)
        self.cpu_name_box.setChecked(True)
        self.ram_box.setChecked(True)
        self.gpu_box.setChecked(True)

    def display_internet(self):
        self.internet_error_label.setText("")
        self.set_internet_list()
        self.internet_listwidget.clear()
        self.internet_listwidget.addItems(self.total_internet_list)

    def write_internet(self):
        self.internet_error_label.setText("")
        self.internet_error_label.setStyleSheet("color: red")
        self.internet_filename = self.internet_filename_lineedit.text()
        
        try:
            if not self.internet_filename:
                raise NoFileName
            
            if len(self.internet_filename.split(".")) == 1:
                self.internet_filename += ".txt"
            elif len(self.internet_filename.split(".")) == 2 and\
                    not self.internet_filename.split(".")[1]:
                self.internet_filename += "txt"
            
            with open(self.internet_filename, "w") as text_file:
                self.set_internet_list()

                for parameter in self.total_internet_list:
                    text_file.write(parameter + "\n")
                
                self.internet_error_label.setStyleSheet("color: green")
                self.internet_error_label.setText("Готово!")
        except NoFileName:
            self.internet_error_label.setText("Вы забыли написать имя файла!")
            
    def choose_all_internet(self):
        self.ping_box.setChecked(True)
        self.upload_box.setChecked(True)
        self.download_box.setChecked(True)

    def set_hardware_list(self):
        self.total_hardware_list = []
        computer = wmi.WMI()

        computer_info = computer.Win32_ComputerSystem()[0]
        os_info = computer.Win32_OperatingSystem()[0]

        if self.manufacturer_box.checkState():
            self.total_hardware_list.append(f"Производитель: {computer_info.Manufacturer}")

        if self.pc_model_box.checkState():
            self.total_hardware_list.append(f"Модель: {computer_info.Model}")
        
        if self.os_name_box.checkState():
            os_name = os_info.Name.encode("utf-8").split(b"|")[0].decode()
            self.total_hardware_list.append(f"Имя ОС: {os_name}")
        
        if self.os_version_box.checkState():
            os_version = ' '.join([os_info.Version, os_info.BuildNumber])
            self.total_hardware_list.append(f"Версия ОС: {os_version}")
        
        if self.cpu_name_box.checkState():
            cpu_info = computer.Win32_Processor()[0].Name
            self.total_hardware_list.append(f"Название процессора: {cpu_info}")
        
        if self.ram_box.checkState():
            ram = round(float(os_info.TotalVisibleMemorySize) / 1024 / 1024, 2)
            self.total_hardware_list.append(f"Объем ОЗУ: {ram}")
        
        if self.gpu_box.checkState():
            gpu_info = computer.Win32_VideoController()

            if len(gpu_info) > 1:
                for i, card in enumerate(gpu_info, 1):
                    self.total_hardware_list.append(f"Видеокарта номер {i}: {card.Name}")
            else:
                self.total_hardware_list.append(gpu_info.Name)

    def set_internet_list(self):
        self.total_internet_list = []

        st = speedtest.Speedtest()

        if self.ping_box.checkState():
            ping = subprocess.run(["ping", "-n", "1", "yandex.ru"],
                              stdout=subprocess.PIPE, encoding="CP866")
            ping = parse_ping(ping.stdout)
            self.total_internet_list.append("Ping: " + ping)
        
        if self.upload_box.checkState():
            upload_speed = "Скорость загрузки: " + make_readable_size(st.upload())
            self.total_internet_list.append(upload_speed)
        
        if self.download_box.checkState():
            download_speed = "Скорость скачивания: " + make_readable_size(st.download())
            self.total_internet_list.append(download_speed)


def make_readable_size(n_bytes):
    sizes = ["B", "KB", "MB", "GB", "TB"]
    ind = 0

    while n_bytes > 1024 and ind <= 4:
        n_bytes /= 1024
        ind += 1
    n_bytes = round(n_bytes, 2)
    return f"{n_bytes} {sizes[ind]}"


def parse_ping(ping):
    ping = ping.split("время=")[1]
    result = ""

    for s in ping:
        if s == "м":
            break
        else:
            result += s
    return result + "мс"


if __name__ == '__main__':
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
