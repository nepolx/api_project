import os
import sys

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

SCREEN_SIZE = [600, 450]
hg = 25
dlt = hg / 10


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.latitude = 58.971889
        self.longitude = 53.410387
        self.getImage()
        self.initUI()

    def getImage(self):
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={self.latitude},{self.longitude}&spn={hg},{hg}&l=map"
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

    def closeEvent(self, event):
        os.remove(self.map_file)

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Up:
            self.longitude += dlt
            self.longitude = self.longitude % 90
        elif event.key() == Qt.Key_Down:
            self.longitude -= dlt
            self.longitude = self.longitude % 90
        elif event.key() == Qt.Key_Right:
            self.latitude += dlt
            self.latitude = self.latitude % 180
        elif event.key() == Qt.Key_Left:
            self.latitude -= dlt
            self.latitude = self.latitude % 180
        else:
            super().keyPressEvent(event)

        self.getImage()
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
