# 7
import os
import sys

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QLineEdit, QPushButton

SCREEN_SIZE = [600, 450]
hg = 0.05
dlt = hg / 10
geocoder_request = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=ИсторическиймузейМоскваКраснаяПлощадь1&format=json"


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.latitude = 58.971889
        self.longitude = 53.410387
        self.spn = hg
        self.dlt = self.spn / 10
        self.metks = []
        self.type = 'map'
        self.getImage()
        self.initUI()

    def getImage(self):
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={self.latitude},{self.longitude}&spn={self.spn},{self.spn}&l={self.type}"
        if self.metks:
            map_request += '&pt='
            map_request += '~'.join(self.metks)
        response = requests.get(map_request)

        if not response:
            print("Error executing request:")
            print(map_request)
            print("Http status:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Write the received image to a file.
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Map display')
        # Image
        self.pixmap = QPixmap(self.map_file)
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)
        self.button = QPushButton(self)
        self.button.setHidden(True)
        self.button.setText('Сброс')
        self.button.setStyleSheet("background-color: red")
        self.button.clicked.connect(self.reset)
        self.button.move(10, SCREEN_SIZE[1]-30)
        self.adress = QLineEdit(self)
        self.adress.move(100, 0)
        self.adress.textChanged[str].connect(self.onChanged)

    def reset(self):
        self.metks.remove(self.metks[-1])
        self.button.setEnabled(False)
        self.getImage()
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

    def onChanged(self, text):
        self.adress.setText(text)
        self.adress.adjustSize()

    def closeEvent(self, event):
        os.remove(self.map_file)

    def get_pos(self, text):
        geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={text}&format=json"
        response = requests.get(geocoder_request)
        if response:
            json_response = response.json()

            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            # Полный адрес топонима:
            toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
            # Координаты центра топонима:
            toponym_coodrinates = toponym["Point"]["pos"]
            # Печатаем извлечённые из ответа поля:
            print(toponym_address, "имеет координаты:", toponym_coodrinates)
            self.latitude, self.longitude = float(toponym_coodrinates.split()[0]), float(toponym_coodrinates.split()[1])
            self.spn = 0.02
            if f"{self.latitude},{self.longitude},pm2blm" not in self.metks:
                self.metks.append(f"{self.latitude},{self.longitude},pm2blm")
        else:
            print("Ошибка выполнения запроса:")
            print(geocoder_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter and self.adress.isEnabled():
            if self.adress.text():
                self.button.setHidden(False)
                self.button.setEnabled(True)
                self.get_pos(self.adress.text())
            self.adress.setEnabled(False)
        elif event.key() == Qt.Key_Enter and not self.adress.isEnabled():
            self.adress.setEnabled(True)
        elif event.key() == Qt.Key_PageUp and self.spn < 26:
            if self.spn <= 1:
                self.spn += 0.08
            else:
                self.spn += 4
            self.dlt = self.spn / 10
            # print(self.spn)
        elif event.key() == Qt.Key_PageDown:
            if self.spn <= 1 and self.spn - 0.01 > 0:
                self.spn -= 0.01
            elif self.spn - 4 > 0:
                self.spn -= 4
            # print(self.spn)
            self.dlt = self.spn / 10

        elif event.key() == Qt.Key_Q:
            self.type = 'map'
        elif event.key() == Qt.Key_W:
            self.type = 'sat'
        elif event.key() == Qt.Key_E:
            self.type = 'skl'
        elif event.key() == Qt.Key_Up:
            self.longitude += self.dlt
            self.longitude = self.longitude % 90
        elif event.key() == Qt.Key_Down:
            self.longitude -= self.dlt
            self.longitude = self.longitude % 90
        elif event.key() == Qt.Key_Right:
            self.latitude += self.dlt
            self.latitude = self.latitude % 180
        elif event.key() == Qt.Key_Left:
            self.latitude -= self.dlt
            self.latitude = self.latitude % 180
        else:
            super().keyPressEvent(event)

        self.getImage()
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
