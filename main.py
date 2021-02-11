import sys
from io import BytesIO
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
# Этот класс поможет нам сделать картинку из потока байт

import requests
from PIL import Image


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("main_ui.ui", self)
        pixmap = QPixmap("main_pic.png")
        self.setWindowTitle("MAP")
        self.main_picture.setPixmap(pixmap)


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


def get_maps(coord1, coord2, delta):
    map_params = {
        "ll": ",".join([coord1, coord2]),
        "spn": delta,
        "l": "map",
        "pt": ",".join([coord1, coord2, "pmwtm1"])
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    # ... и выполняем запрос
    response = requests.get(map_api_server, params=map_params)

    return response.content


def get_spn(adress):
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
    adress = "Москва Кремль"
    toponym_longitude, toponym_lattitude = get_coord(adress)

    delta = get_spn(adress)

    image_map = get_maps(toponym_longitude, toponym_lattitude, delta)

    image = Image.open(BytesIO(image_map))
    image.save("main_pic.png")
    # Создадим картинку
    # и тут же ее покажем встроенным просмотрщиком операционной системы
    QT_window = MainWindow()
    QT_window.show()
    sys.exit(app.exec())

