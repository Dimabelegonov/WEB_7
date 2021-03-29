import sys
import os
from io import BytesIO
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPixmap
from PyQt5 import uic

import requests
from PIL import Image


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("main_ui.ui", self)
        self.setWindowTitle("MAP")
        self.z = 14
        self.d_x = 0.0
        self.d_y = 0.0
        self.map_1 = "map"
        self.address = "Кремль Москва"
        self.coord_flag = []
        self.get_map(new=True)
        self.change_map.buttonClicked.connect(self.change_)
        self.button_search.clicked.connect(self.search)

    def change_(self, button):
        if button.text() == "Схема":
            self.map_1 = "map"
            self.get_map()
        elif button.text() == "Спутник":
            self.map_1 = "sat"
            self.get_map()
        elif button.text() == "Гибрид":
            self.map_1 = "sat,skl"
            self.get_map()

    def search(self):
        self.address = self.text_search.text()
        self.get_map(new=True)

    def get_map(self, new=False):
        """Получаем изображение карты"""
        if new:
            self.d_x = 0.0
            self.d_y = 0.0
        toponym_longitude, toponym_lattitude = get_coord(self.address)
        toponym_lattitude = float(toponym_lattitude) + self.d_x
        toponym_longitude = float(toponym_longitude) + self.d_y
        if new:
            self.coord_flag = [toponym_longitude, toponym_lattitude]

        delta = get_spn(self.address)
        image_map = get_maps(toponym_longitude, toponym_lattitude, self.coord_flag, delta, self.z, self.map_1)
        image = Image.open(BytesIO(image_map))
        image.save("main_pic.png")
        # Создадим картинку
        # и тут же ее покажем встроенным просмотрщиком операционной системы
        self.show_map()

    def show_map(self):
        """Отрисовываем изображение"""
        pixmap = QPixmap("main_pic.png")
        self.main_picture.setPixmap(pixmap)

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_PageUp:
            self.z = min(17, self.z + 1)
            self.get_map()
        elif QKeyEvent.key() == Qt.Key_PageDown:
            self.z = max(0, self.z - 1)
            self.get_map()
        elif QKeyEvent.key() == Qt.Key_Right:
            self.d_y += 0.001
            self.get_map()
        elif QKeyEvent.key() == Qt.Key_Up:
            self.d_x += 0.001
            self.get_map()
        elif QKeyEvent.key() == Qt.Key_Left:
            self.d_y -= 0.001
            self.get_map()
        elif QKeyEvent.key() == Qt.Key_Down:
            self.d_x -= 0.001
            self.get_map()


def get_coord(adress):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": adress,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        # обработка ошибочной ситуации
        pass

    # Преобразуем ответ в json-объект
    json_response = response.json()
    # Получаем первый топоним из ответа геокодера.
    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и широта:
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    return toponym_longitude, toponym_lattitude


def get_maps(coord1, coord2, flag, delta, z, map_1):
    map_params = {
        "ll": ",".join([str(coord1), str(coord2)]),
        # "spn": delta,
        "z": str(z),
        "l": map_1,
        "pt": ",".join([str(flag[0]), str(flag[1]), "pmwtm1"])
    }
    map_api_server = "http://static-maps.yandex.ru/1.x/"
    # ... и выполняем запрос
    response = requests.get(map_api_server, params=map_params)

    return response.content


def get_spn(address):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": address,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        # обработка ошибочной ситуации
        pass

    # Преобразуем ответ в json-объект
    json_response = response.json()
    # Получаем первый топоним из ответа геокодера.
    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    toponym_spn = toponym["boundedBy"]["Envelope"]
    lx, ly = toponym_spn["lowerCorner"].split()
    # print(toponym_spn["lowerCorner"])
    ux, uy = toponym_spn["upperCorner"].split()
    # print(toponym_spn["upperCorner"])
    dx = abs(float(lx) - float(ux)) / 2
    dy = abs(float(ly) - float(uy)) / 2
    # print(dx, dy)
    return f"{dx},{dy}"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QT_window = MainWindow()
    QT_window.show()
    sys.exit(app.exec())
