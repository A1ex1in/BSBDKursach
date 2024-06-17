import os
import sys
import PyQt6
import psutil
import psycopg2
import itertools
import subprocess
from PyQt6 import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from AdminWindowUI import Ui_AdminWind
from UserWindowUI import Ui_UserWindow
from VievWindowUI import Ui_VievWindow
from ManajerWindowUI import Ui_ManajerWindow
from UpdateInsertWindowUI import Ui_UpdateInsert
from AutorizationWindowUI import Ui_Autorizations


# def passage(name, paths):
#     for path in paths:
#         for root, dirs, files in os.walk(path):
#             if name in files:
#                 return os.path.join(root, name)
#
#
# disks = psutil.disk_partitions()
# disk_paths = [disk.device for disk in disks]
# path_terminal = passage('runpsql.bat', disk_paths)
# print(path_terminal)
# PC
# D:\programs\ASQL\PostgreSQL\16\scripts\runpsql.bat
# Ноут
# D:\ASQL\PostgreSQL\16\scripts\runpsql.bat
path_bat = [r'D:\programs\ASQL\PostgreSQL\16\scripts\runpsql.bat',r'D:\ASQL\PostgreSQL\16\scripts\runpsql.bat']
table_name_key = {'Адрес клиентов': 'adres_client', 'Адрес филиалов': 'adres_filial', 'Клиенты': 'client', 'Филиалы': 'filial', 'Ключи': 'keys', 'Операции': 'operations_schet', 'Счета': 'schet', 'Состояния (счетов)': 'state_schet', 'Состояния (заявок)': 'state_zayavka', 'Тип (операций)': 'type_operation', 'Тип (счетов)': 'type_schet', 'Валюты': 'valut', 'Заявки': 'zayavka'}
name_table = ['Адрес клиентов', 'Адрес филиалов', 'Клиенты', 'Филиалы', 'Ключи', 'Операции', 'Счета', 'Состояния (счетов)', 'Состояния (заявок)', 'Тип (операций)', 'Тип (счетов)', 'Валюты', 'Заявки']
query_text_key = {'Получить список всех зарегистрированных в системе клиентов, имеющих задолженность по кредиту': """SELECT c.* FROM client c JOIN schet s ON c.id_client = s.id_client WHERE s.summ != 0;""", 'Проверить статус заявки на кредит для определённого клиента': """SELECT z.*, sz.sost AS status_zayavki FROM zayavka z JOIN state_zayavka sz ON z.id_state_zayavka = sz.id_state_zayavka WHERE z.id_client = 1;""", 'Посмотреть все заявки на кредит ожидающие одобрения': """SELECT z.* FROM zayavka z WHERE z.id_state_zayavka = 7;""", 'Проверить историю выдачи кредитов для конкретного клиента': """SELECT s.* FROM schet s WHERE s.id_client = 1;""", 'Получить список всех открытых кредитов': """SELECT s.* FROM schet s WHERE s.id_state_schet = 1;""", 'Посмотреть список отказанных заявок на кредит': """SELECT z.* FROM zayavka z WHERE (z.id_state_zayavka = 6 OR z.id_state_zayavka = 9);""", 'Получить общую сумму всех открытых кредитов': """SELECT SUM(s.summ) AS total_open_credit_sum FROM schet s WHERE s.id_state_schet = 1;""", 'Проверить текущий баланс по кредитным счетам клиента': """SELECT s.id_schet, s.summ FROM schet s WHERE s.id_client = 1;"""}
name_query = ['Получить список всех зарегистрированных в системе клиентов, имеющих задолженность по кредиту', 'Проверить статус заявки на кредит для определённого клиента', 'Посмотреть все заявки на кредит ожидающие одобрения', 'Проверить историю выдачи кредитов для конкретного клиента', 'Получить список всех открытых кредитов', 'Посмотреть список отказанных заявок на кредит', 'Получить общую сумму всех открытых кредитов', 'Проверить текущий баланс по кредитным счетам клиента']
role_list = ['cliet', 'administrator', 'menedjer']


def main():
    try:
        app = QApplication(sys.argv)
        login_window = Login()
        login_window.show()
        sys.exit(app.exec())
    except Exception as e:
        QMessageBox.critical(None, 'Error', str(e))


def ConnectionBD(uname, passw):
    try:
        con = psycopg2.connect(dbname='bank', user=uname, password=passw, host='localhost')
        return con
    except Exception as e:
        QMessageBox.critical(None, 'Error', str(e))


def UserRole(conn, uname):
    try:
        curs = conn.cursor()
        r = None
        for i in role_list:
            curs.execute(f"""SELECT rolname FROM pg_roles WHERE pg_has_role(rolname, '{i}', 'member') and rolname = '{uname}';""")
            res = curs.fetchone()
            if res is not None:
                r = i
                break
        curs.close()
        return r
    except Exception as e:
        QMessageBox.critical(None, 'Error', str(e))


def SetDataDB(connection, query):
    try:
        curs = connection.cursor()
        curs.execute(query)
        d = curs.fetchall()
        curs.close()
        return d
    except Exception as e:
        QMessageBox.critical(None, 'Error', str(e))


def GetHeadTable(connection, tableName):
    try:
        conn = connection
        curs = conn.cursor()
        v = tableName
        curs.execute(f"""SELECT column_name FROM information_schema.columns WHERE table_name = '{v}'""")
        h = [column[0] for column in curs.fetchall()]
        return h
    except Exception as e:
        QMessageBox.critical(None, 'Error', str(e))


class Login(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Autorizations()
        self.ui.setupUi(self)
        self.ui.PB_Login.clicked.connect(self.log)
        self.conn = None
        self.wind = None

    def log(self):
        uname = self.ui.LE_Login.text()
        passw = self.ui.LE_Password.text()
        self.conn = ConnectionBD(uname, passw)
        try:
            if UserRole(self.conn, uname) == role_list[0]:
                self.wind = Client(self.conn, self)
                self.wind.show()
                self.hide()
            elif UserRole(self.conn, uname) == role_list[1]:
                self.wind = Admin(self.conn, self)
                self.wind.show()
                self.hide()
            elif UserRole(self.conn, uname) == role_list[2]:
                self.wind = Sotrud(self.conn, self)
                self.wind.show()
                self.hide()
            else:
                QMessageBox.warning(None, 'Error', 'Нет роли.')
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))


class Admin(QMainWindow):
    def __init__(self, connection, parent=None):
        super().__init__(parent)
        self.ui = Ui_AdminWind()
        self.ui.setupUi(self)
        self.conn = connection

        self.ui.pushButton.clicked.connect(self.OpenTerminal)
        self.ui.pushButton_2.clicked.connect(self.OpenTable)
        self.ui.comboBox.addItems(name_table)

    def OpenTerminal(self):
        try:
            subprocess.Popen(('start', fr'D:\programs\ASQL\PostgreSQL\16\scripts\runpsql.bat'), shell=True)
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))

    def OpenTable(self):
        try:
            t = self.ui.comboBox.currentText()
            v = table_name_key[f'{t}']
            d = SetDataDB(self.conn, f"""SELECT * FROM {v};""")
            h = GetHeadTable(self.conn, v)
            self.TableWindow = VievWindow(h, d, self)
            self.TableWindow.show()
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))

    def closeEvent(self, event):
        try:
            self.parent().show()
            event.accept()
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))


class Sotrud(QMainWindow):
    def __init__(self, connection, parent=None):
        super().__init__(parent)
        self.ui = Ui_ManajerWindow()
        self.ui.setupUi(self)
        self.conn = connection

        self.ui.CB_L.addItems(name_table)
        self.ui.CB_R.addItems(name_table)
        self.ui.CB_Query.addItems(name_query)

        # self.ui.PB_L1.clicked.connect()
        self.ui.PB_L2.clicked.connect(lambda: self.LoadTable(1))

        # self.ui.PB_R1.clicked.connect()
        self.ui.PB_R2.clicked.connect(lambda: self.LoadTable(2))

        self.ui.PB_Query_Execute.clicked.connect(self.QueryExecute)

        self.ui.PB_L_Inser.clicked.connect(lambda: self.Insert(1))
        self.ui.PB_L_Update.clicked.connect(lambda: self.Update(1))
        self.ui.PB_L_Delete.clicked.connect(lambda: self.Delete(1))

        self.ui.PB_R_Insert.clicked.connect(lambda: self.Insert(2))
        self.ui.PB_R_Update.clicked.connect(lambda: self.Update(2))
        self.ui.PB_R_Delete.clicked.connect(lambda: self.Delete(2))

    def LoadTable(self, IndexPB):
        try:
            if IndexPB == 1:
                t = self.ui.CB_L.currentText()
                v = table_name_key[f'{t}']
                d = SetDataDB(self.conn, f"""SELECT * FROM {v};""")
                h = GetHeadTable(self.conn, v)
                self.ui.TW_L.setRowCount(len(d))
                self.ui.TW_L.setColumnCount(len(h))
                self.ui.TW_L.setHorizontalHeaderLabels(h)
                for row_idx, row_data in enumerate(d):
                    for col_idx, col_data in enumerate(row_data):
                        self.ui.TW_L.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
            elif IndexPB == 2:
                t = self.ui.CB_R.currentText()
                v = table_name_key[f'{t}']
                d = SetDataDB(self.conn, f"""SELECT * FROM {v};""")
                h = GetHeadTable(self.conn, v)
                self.ui.TW_R.setRowCount(len(d))
                self.ui.TW_R.setColumnCount(len(h))
                self.ui.TW_R.setHorizontalHeaderLabels(h)
                for row_idx, row_data in enumerate(d):
                    for col_idx, col_data in enumerate(row_data):
                        self.ui.TW_R.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))

    def QueryExecute(self):
        try:
            pass
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))

    def Insert(self, IndexPB):
        try:
            if IndexPB == 1:
                text = self.ui.CB_L.currentText()
                val = table_name_key[f'{text}']
                self.win = UpdateInsert(self.conn, val, sign=1)
                self.win.show()
            elif IndexPB == 2:
                text = self.ui.CB_R.currentText()
                val = table_name_key[f'{text}']
                self.win = UpdateInsert(self.conn, val, sign=1)
                self.win.show()
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))

    def Update(self, IndexPB):
        try:
            if IndexPB == 1:
                pass
            elif IndexPB == 2:
                pass
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))

    def Delete(self, IndexPB):
        try:
            if IndexPB == 1:
                pass
            elif IndexPB == 2:
                pass
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))

    def closeEvent(self, event):
        try:
            self.parent().show()
            event.accept()
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))


class Client(QMainWindow):
    def __init__(self, connection, parent=None):
        super().__init__(parent)
        self.ui = Ui_UserWindow()
        self.ui.setupUi(self)
        self.conn = connection
        self.ui.PB_Oper.clicked.connect(self.GetOper)
        self.ui.PB_Info.clicked.connect(self.GetInfo)
        self.ui.PB_Schet.clicked.connect(self.GetSchet)

    def GetOper(self):
        try:
            d = SetDataDB(self.conn, """SELECT * FROM operations_schet;""")
            h = GetHeadTable(self.conn, 'operations_schet')
            self.TableWindow = VievWindow(h, d, self)
            self.TableWindow.show()
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))


    def GetInfo(self):
        try:
            d = SetDataDB(self.conn, """SELECT * FROM client;""")
            h = GetHeadTable(self.conn, 'client')
            self.TableWindow = VievWindow(h, d, self)
            self.TableWindow.show()
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))


    def GetSchet(self):
        try:
            d = SetDataDB(self.conn, """SELECT * FROM schet;""")
            h = GetHeadTable(self.conn, 'client')
            self.TableWindow = VievWindow(h, d, self)
            self.TableWindow.show()
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))

    def closeEvent(self, event):
        try:
            self.parent().show()
            event.accept()
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))


class VievWindow(QMainWindow):
    def __init__(self, tabHead, data, parent=None):
        super().__init__(parent)
        self.ui = Ui_VievWindow()
        self.ui.setupUi(self)
        self.table_head = tabHead
        self.data = data
        self.set_data(self.table_head, self.data)

    def set_data(self, colnames, data):
        try:
            self.ui.tableWidget.setRowCount(len(data))
            self.ui.tableWidget.setColumnCount(len(colnames))
            self.ui.tableWidget.setHorizontalHeaderLabels(colnames)
            for row_idx, row_data in enumerate(data):
                for col_idx, col_data in enumerate(row_data):
                    self.ui.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))

    def closeEvent(self, event):
        try:
            self.parent().show()
            event.accept()
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))


class UpdateInsert(QMainWindow):
    def __init__(self, connection, tabName, sign):
        super().__init__()
        self.ui = Ui_UpdateInsert
        self.ui.setupUi(self)
        self.conn = connection
        self.tabName = tabName
        self.sign = sign
        self.test()

    def test(self):
        try:
            if self.sign == 1:
                self.load_to_insert()
                self.ui.pushButton.clicked.connect(self.insert_data)
            elif self.sign == 2:
                self.load_to_update()
                self.ui.pushButton.clicked.connect(self.update_data)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def load_to_update(self):
        try:
            pass
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))

    def load_to_insert(self):
        try:
            self.columns_name = GetHeadTable(self.conn, self.tabName)
            self.ui.tableWidget.setColumnCount(len(self.columns_name))
            self.ui.tableWidget.setHorizontalHeaderLabels(self.columns_name)
            self.ui.tableWidget.setRowCount(1)
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))

    def update_data(self):
        try:
            pass
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))

    def insert_data(self):
        try:
            row = []
            for column in range(len(self.columns_name)):
                item = self.ui.tableWidget.item(0, column)
                row_data.append(item.text() if item else '')
            placeholders = ', '.join(['%s'] * len(self.columns_name))
            columns = ', '.join(self.columns_name)
            query = f"INSERT INTO {self.tabName} ({columns}) VALUES ({placeholders})"
            curs = self.conn.cursor()
            curs.execute(query, row_data)
            self.conn.commit()
            QMessageBox.information(self, "Выполено", "Данные обновлены.")
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))

    def closeEvent(self, event):
        try:
            self.parent().show()
            event.accept()
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))


if __name__ == '__main__':
    main()
