import os
import subprocess
import sys
import psutil
import psycopg2
# from PyQt6 import *
# from PyQt6.QtGui import *
# from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from UserWindowUI import Ui_UserWindow
from AdminWindowUI import Ui_AdminWind
from ManajerWindowUI import Ui_Manajer
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
# i = passage('runpsql.bat', disk_paths)
# print(i)
# D:\programs\ASQL\PostgreSQL\16\scripts\runpsql.bat


def con_bd(uname, passw):
    try:
        con = psycopg2.connect(dbname='bank', user=uname, password=passw, host='localhost')
        return con
    except psycopg2.Error as e:
        print(f"Error:{e}")


def aut_user(conn, username):
    values = ('cliet', 'administrator', 'menedjer')
    role = None

    cursor = conn.cursor()
    for value in values:
        cursor.execute(f"SELECT rolname FROM pg_roles WHERE pg_has_role(rolname, '{value}', 'member') and rolname = '{username}';")
        result = cursor.fetchone()
        if result is not None:
            role = value
            break
    cursor.close()
    return role


class TableDialog:
    def __init__(self, parent=None):
        self.dialog = QDialog(parent)
        self.dialog.setWindowTitle("Table")
        self.layout = QVBoxLayout()

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.dialog.setLayout(self.layout)

    def set_data(self, data):
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(data[0]) if data else 0)
        for row_idx, row_data in enumerate(data):
            for col_idx, col_data in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

        width = self.table.verticalHeader().width() + self.table.horizontalHeader().length() + 50
        height = self.table.horizontalHeader().height() + self.table.verticalHeader().length() + 50
        self.dialog.resize(width, height)

    def exec_(self):
        self.dialog.exec()


class UserWind(QMainWindow):
    def __init__(self, connection):
        super().__init__()
        self.ui = Ui_UserWindow()
        self.ui.setupUi(self)

        self.connection = connection

        self.ui.PB_Schet.clicked.connect(self.qSchet)
        self.ui.PB_Info.clicked.connect(self.qInfo)
        self.ui.PB_Oper.clicked.connect(self.qOper)

    def qSchet(self):
        data = self.GetSchet()
        dialog = TableDialog()
        dialog.set_data(data)
        dialog.exec_()

    def qInfo(self):
        data = self.GetInfo()
        dialog = TableDialog()
        dialog.set_data(data)
        dialog.exec_()

    def qOper(self):
        data = self.GetOper()
        dialog = TableDialog()
        dialog.set_data(data)
        dialog.exec_()

    def GetSchet(self):
        return self.DataFromDB("SELECT * FROM schet")

    def GetInfo(self):
        return self.DataFromDB("SELECT * FROM operations_schet")

    def GetOper(self):
        return self.DataFromDB("SELECT * FROM client")

    def DataFromDB(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        return data


class AdminWind(QMainWindow):
    def __init__(self, connect):
        super().__init__()
        self.ui = Ui_AdminWind()
        self.ui.setupUi(self)

        self.conn = connect

        self.ui.pushButton.clicked.connect(self.open_terminal)
        self.ui.pushButton_2.clicked.connect(self.open_table)
        items = ['Адрес клиентов', 'Адрес филиалов', 'Клиенты', 'Филиалы', 'Ключи', 'Операции', 'Счета', 'Состояния (счетов)', 'Состояния (заявок)', 'Тип (операций)', 'Тип (счетов)', 'Валюты', 'Заявки']
        self.ui.comboBox.addItems(items)

    def open_terminal(self):
        subprocess.Popen(('start', rf'D:\programs\ASQL\PostgreSQL\16\scripts\runpsql.bat'), shell=True)

    def open_table(self):
        text = self.ui.comboBox.currentText()
        print(text)
        item = {'Адрес клиентов': 'adres_client', 'Адрес филиалов': 'adres_filial', 'Клиенты': 'client', 'Филиалы': 'filial', 'Ключи': 'keys', 'Операции': 'operations_schet', 'Счета': 'schet', 'Состояния (счетов)': 'state_schet', 'Состояния (заявок)': 'state_zayavka', 'Тип (операций)': 'type_operation', 'Тип (счетов)': 'type_schet', 'Валюты': 'valut', 'Заявки': 'zayavka'}
        val = item[f'{text}']
        print(type(val))
        print(val)
        data = self.DataFromDB(f"""SELECT * FROM {val};""")
        dialog = TableDialog()
        dialog.set_data(data)
        dialog.exec_()

    def DataFromDB(self, query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        return data


class ManajerWind(QMainWindow):
    def __init__(self, connection):
        super().__init__()
        self.ui = Ui_Manajer()
        self.ui.setupUi(self)

        self.connection = connection

        items_table = ['Адрес клиентов', 'Адрес филиалов', 'Клиенты', 'Филиалы', 'Ключи', 'Операции', 'Счета', 'Состояния (счетов)', 'Состояния (заявок)', 'Тип (операций)', 'Тип (счетов)', 'Валюты', 'Заявки']
        self.ui.CB_Table.addItems(items_table)
        items_querry = ['Получить список всех зарегистрированных в системе клиентов, имеющих задолженность по кредиту', 'Проверить статус заявки на кредит для определённого клиента', 'Посмотреть все заявки на кредит ожидающие одобрения', 'Проверить историю выдачи кредитов для конкретного клиента', 'Получить список всех открытых кредитов', 'Посмотреть список отказанных заявок на кредит', 'Получить общую сумму всех открытых кредитов', 'Проверить текущий баланс по кредитным счетам клиента']
        self.ui.CB_Querry.addItems(items_querry)
        self.ui.PB_Add.clicked.connect(self.add_data_bd)
        self.ui.PB_Update.clicked.connect(self.update_data_bd)
        self.ui.PB_Delete.clicked.connect(self.delete_data_bd)
        self.ui.PB_Open.clicked.connect(self.open_table)

    def add_data_bd(self):
        pass

    def update_data_bd(self):
        pass

    def delete_data_bd(self):
        pass

    def open_table(self):
        text = self.ui.CB_Table.currentText()
        item = {'Адрес клиентов': 'adres_client', 'Адрес филиалов': 'adres_filial', 'Клиенты': 'client', 'Филиалы': 'filial', 'Ключи': 'keys', 'Операции': 'operations_schet', 'Счета': 'schet', 'Состояния (счетов)': 'state_schet', 'Состояния (заявок)': 'state_zayavka', 'Тип (операций)': 'type_operation', 'Тип (счетов)': 'type_schet', 'Валюты': 'valut', 'Заявки': 'zayavka'}
        val = item[f'{text}']
        data = self.DataFromDB(f"""SELECT * FROM {val};""")
        dialog = TableDialog()
        dialog.set_data(data)
        dialog.exec_()

    def DataFromDB(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        return data


class Authorization(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Autorizations()
        self.ui.setupUi(self)

        self.ui.PB_Login.clicked.connect(self.login)
        self.connection = None
        self.act_win = None

    def login(self):
        uname = self.ui.LE_Login.text()
        passw = self.ui.LE_Password.text()

        self.connection = con_bd(uname, passw)

        role = aut_user(self.connection, uname)
        if role == 'cliet':
            self.act_win = UserWind(self.connection)
            self.act_win.show()
            self.close()
        elif role == 'administrator':
            self.act_win = AdminWind(self.connection)
            self.act_win.show()
            self.close()
        elif role == 'menedjer':
            self.act_win = ManajerWind(self.connection)
            self.act_win.show()
            self.close()
        else:
            QMessageBox.warning(self, 'Error', 'Invalid role')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = Authorization()
    login_window.show()
    sys.exit(app.exec())
