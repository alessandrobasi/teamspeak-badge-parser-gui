
from PyQt5 import uic
from PyQt5.Qt import QApplication, QMainWindow
import sys
import re
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtGui import QIcon, QPixmap
import requests
import os
from time import time
from shutil import rmtree
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.badges = []
        self.getFile("list")

        self.changeScreen("mainWin.ui", self.mainWin)

    def changeScreen(self, fileUi, nextFunct=""):
        self.__nextFunct = nextFunct
        uic.loadUi(fileUi, self)
        self.show()
        if self.__nextFunct != "":
            self.__nextFunct()

    def getFile(self, local=None):
        if not os.path.exists("cache"):
            os.mkdir("cache")

        if local and (not os.path.exists(local) or (time() - os.path.getmtime(local)) > 604800):
            r = requests.get("https://badges-content.teamspeak.com/list")
            if r.status_code == 200:
                with open("list", "wb") as f:
                    f.write(r.content)

        with open("list", "r", encoding="ansi") as f:
            text = f.read()
        regex = r"^\$(?P<headid>[\w\d-]+).(.|\n)(?P<nome>.+)..(?P<url>https://[\w\-\.\/]+)..(?P<desc>\w.*)\(.+$"
        matches = re.finditer(regex, text, re.UNICODE | re.MULTILINE)
        for _, match in enumerate(matches, start=1):
            #print([match.group(i) for i in [1, 3, 4, 5]])
            # 1: UUID
            # 3: Nome
            # 4: url
            # 5: desc (ANSI) TODO: portarlo a utf-8
            self.badges.append([str(match.group(i)) for i in [1, 3, 4, 5]])

    def getBadgeIcon(self, codeid, url, tipo="_64"):
        if not os.path.isfile("cache/"+codeid+tipo+".png"):
            url = url.replace("\"", "")
            r = requests.get(url+tipo+".png")
            if r.status_code == 200:
                with open("cache/"+codeid+tipo+".png", "wb") as f:
                    f.write(r.content)
            else:
                return ""

        return "cache/"+codeid+tipo+".png"

    def showBadgesInfo(self):
        uuid, nome, url, desc = self.tabellaBages.selectedItems()[
            0].data(Qt.UserRole)
        self.iconaBadge.setPixmap(QPixmap(self.getBadgeIcon(uuid, url, "_64")))
        self.nomeBadge.setText(nome)
        self.descBadge.setText(desc)

        self.uuidText.setText(uuid)

        self.svgUrl.setText("SVG: <a href='"+url+".svg"+"'>"+url+".svg"+"</a>")
        self.detailsSvgUrl.setText(
            "Details SVG: <a href='"+url+"_details.svg"+"'>"+url+"_details.svg"+"</a>")
        self.detailsPngUrl.setText(
            "Details PNG: <a href='"+url+"_64.png"+"'>"+url+"_64.png"+"</a>")
        self.pngUrl.setText("PNG: <a href='"+url +
                            "_16.png"+"'>"+url+"_16.png"+"</a>")

    def clearCache(self):
        os.remove("list")
        rmtree("cache", ignore_errors=True)
        os.mkdir("cache")
        app.quit()

    def mainWin(self):
        self.statusBar.showMessage(str(len(self.badges))+" medaglie")
        self.tabellaBages.setRowCount(len(self.badges))
        self.clearCacheBtn.clicked.connect(self.clearCache)
        # badge[ X ]
        # 0: UUID
        # 1: Nome
        # 2: url
        # 3: desc (ANSI) TODO: portarlo a utf-8
        for row, badge in enumerate(self.badges):
            uuid, nome, url, _ = badge
            item = QTableWidgetItem(
                QIcon(self.getBadgeIcon(uuid, url, "_64")), nome)
            item.setData(Qt.UserRole, badge)
            self.tabellaBages.setItem(row, 0, item)
        self.tabellaBages.itemSelectionChanged.connect(self.showBadgesInfo)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
