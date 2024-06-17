import os
import subprocess
import sys
import psutil
import psycopg2
# from PyQt6 import *
# from PyQt6.QtGui import *
# from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from ViewWindowUI import Ui_MainWindow
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
# path_terminal = passage('runpsql.bat', disk_paths)
# print(path_terminal)
# PC
# D:\programs\ASQL\PostgreSQL\16\scripts\runpsql.bat
# Ноут
# D:\ASQL\PostgreSQL\16\scripts\runpsql.bat


item_tabl_name = {'Адрес клиентов': 'adres_client', 'Адрес филиалов': 'adres_filial', 'Клиенты': 'client', 'Филиалы': 'filial', 'Ключи': 'keys', 'Операции': 'operations_schet', 'Счета': 'schet', 'Состояния (счетов)': 'state_schet', 'Состояния (заявок)': 'state_zayavka', 'Тип (операций)': 'type_operation', 'Тип (счетов)': 'type_schet', 'Валюты': 'valut', 'Заявки': 'zayavka'}
items_table = ['Адрес клиентов', 'Адрес филиалов', 'Клиенты', 'Филиалы', 'Ключи', 'Операции', 'Счета', 'Состояния (счетов)', 'Состояния (заявок)', 'Тип (операций)', 'Тип (счетов)', 'Валюты', 'Заявки']
query_text = {'Получить список всех зарегистрированных в системе клиентов, имеющих задолженность по кредиту': """SELECT c.* FROM client c JOIN schet s ON c.id_client = s.id_client WHERE s.summ != 0;""",
              'Проверить статус заявки на кредит для определённого клиента': """SELECT z.*, sz.sost AS status_zayavki FROM zayavka z JOIN state_zayavka sz ON z.id_state_zayavka = sz.id_state_zayavka WHERE z.id_client = 1;""",
              'Посмотреть все заявки на кредит ожидающие одобрения': """SELECT z.* FROM zayavka z WHERE z.id_state_zayavka = 7;""",
              'Проверить историю выдачи кредитов для конкретного клиента': """SELECT s.* FROM schet s WHERE s.id_client = 1;""",
              'Получить список всех открытых кредитов': """SELECT s.* FROM schet s WHERE s.id_state_schet = 1;""",
              'Посмотреть список отказанных заявок на кредит': """SELECT z.* FROM zayavka z WHERE (z.id_state_zayavka = 6 OR z.id_state_zayavka = 9);""",
              'Получить общую сумму всех открытых кредитов': """SELECT SUM(s.summ) AS total_open_credit_sum FROM schet s WHERE s.id_state_schet = 1;""",
              'Проверить текущий баланс по кредитным счетам клиента': """SELECT s.id_schet, s.summ FROM schet s WHERE s.id_client = 1;"""
              }


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
    def __init__(self, connection):
        self.dialog = QDialog(parent=None)
        self.dialog.setWindowTitle("Table")
        self.layout = QVBoxLayout()
        self.table = QTableWidget()
        self.layout.addWidget(self.table)
        self.dialog.setLayout(self.layout)
        self.conn = connection

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


class DeleteDialog:
    def __init__(self, conn=None, table_name=None):
        self.dialog = QDialog(parent=None)
        self.conn = conn
        self.table_name = table_name
        layout = QVBoxLayout()
        self.column_combobox = QComboBox(self.dialog)
        self.load_columns()
        layout.addWidget(self.column_combobox)
        self.value_edit = QLineEdit(self.dialog)
        self.value_edit.setPlaceholderText("Значение для удаления")
        layout.addWidget(self.value_edit)
        self.delete_button = QPushButton("Выполнить", self.dialog)
        self.delete_button.clicked.connect(self.delete_record)
        layout.addWidget(self.delete_button)
        self.dialog.setLayout(layout)

    def load_columns(self):
        curs = self.conn.cursor()
        curs.execute(f"""SELECT column_name FROM information_schema.columns WHERE table_name = '{self.table_name}'""")
        columns = [column[0] for column in curs.fetchall()]
        self.column_combobox.addItems(columns)

    def delete_record(self):
        column = self.column_combobox.currentText()
        value = self.value_edit.text()

        if not value:
            QMessageBox.warning(self.dialog, "Внимание", "Введите значение.")
            return

        try:
            query = f"DELETE FROM {self.table_name} WHERE {column} = %s"
            curs = self.conn.cursor()
            curs.execute(query, (value,))
            self.conn.commit()
            QMessageBox.information(self.dialog, "Успешно", "Удаление выполнено.")
            self.dialog.accept()
        except Exception as e:
            QMessageBox.critical(self.dialog, "Error", str(e))

    def exec_(self):
        self.dialog.exec()


class VievWindow(QMainWindow):
    def __init__(self, conn, table_name, sign):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.conn = conn
        self.table_name = table_name
        self.sign = sign
        self.test()

    def test(self):
        if self.sign == 1:
            self.load_table()
            self.ui.pushButton.clicked.connect(self.insert_data)
        elif self.sign == 2:
            self.load_columns()
            self.ui.pushButton.clicked.connect(self.update_record)
        else:
            print('err')

    def load_table(self):
        curs = self.conn.cursor()
        curs.execute(f"""SELECT column_name FROM information_schema.columns WHERE table_name = '{self.table_name}'""")
        self.columns_name = [column[0] for column in curs.fetchall()]

        self.ui.tableWidget.setColumnCount(len(self.columns_name))
        self.ui.tableWidget.setHorizontalHeaderLabels(self.columns_name)
        self.ui.tableWidget.setRowCount(1)

    def insert_data(self):
        row_data = []
        for column in range(len(self.columns_name)):
            item = self.ui.tableWidget.item(0, column)
            row_data.append(item.text() if item else '')

        placeholders = ', '.join(['%s'] * len(self.columns_name))
        columns = ', '.join(self.columns_name)

        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        curs = self.conn.cursor()
        curs.execute(query, row_data)
        self.conn.commit()

    def load_columns(self):
        curs = self.conn.cursor()
        curs.execute(f"SELECT * FROM {self.table_name}")
        self.rows = curs.fetchall()

        curs.execute(f"""SELECT column_name FROM information_schema.columns WHERE table_name = '{self.table_name}'""")
        self.columns_name = [column[0] for column in curs.fetchall()]

        self.ui.tableWidget.setColumnCount(len(self.columns_name))
        self.ui.tableWidget.setHorizontalHeaderLabels(self.columns_name)
        self.ui.tableWidget.setRowCount(len(self.rows))

        for row_idx, row_data in enumerate(self.rows):
            for col_idx, cell_data in enumerate(row_data):
                self.ui.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(cell_data)))

    def update_record(self):
        try:
            curs = self.conn.cursor()

            for row_idx in range(len(self.rows)):
                row_data = []
                for column in range(len(self.columns_name)):
                    item = self.ui.tableWidget.item(row_idx, column)
                    row_data.append(item.text() if item else '')

                set_clause = ', '.join([f"{col} = %s" for col in self.columns_name])
                query = f"UPDATE {self.table_name} SET {set_clause} WHERE {self.columns_name[0]} = %s"
                curs.execute(query, row_data + [self.rows[row_idx][0]])

            self.conn.commit()
            QMessageBox.information(self, "Выполено", "Данные обновлены.")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class UserWind(QMainWindow):
    def __init__(self, connection):
        super().__init__()
        self.ui = Ui_UserWindow()
        self.ui.setupUi(self)

        self.conn = connection

        self.ui.PB_Schet.clicked.connect(self.qSchet)
        self.ui.PB_Info.clicked.connect(self.qInfo)
        self.ui.PB_Oper.clicked.connect(self.qOper)

    def qSchet(self):
        data = self.GetSchet()
        dialog = TableDialog(self.conn)
        dialog.set_data(data)
        dialog.exec_()

    def qInfo(self):
        data = self.GetInfo()
        dialog = TableDialog(self.conn)
        dialog.set_data(data)
        dialog.exec_()

    def qOper(self):
        data = self.GetOper()
        dialog = TableDialog(self.conn)
        dialog.set_data(data)
        dialog.exec_()

    def GetSchet(self):
        return self.DataFromDB("SELECT * FROM schet")

    def GetInfo(self):
        return self.DataFromDB("SELECT * FROM operations_schet")

    def GetOper(self):
        return self.DataFromDB("SELECT * FROM client")

    def DataFromDB(self, query):
        cursor = self.conn.cursor()
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
        self.ui.comboBox.addItems(items_table)

    def open_terminal(self):
        subprocess.Popen(('start', rf'D:\ASQL\PostgreSQL\16\scripts\runpsql.bat'), shell=True)

    def open_table(self):
        text = self.ui.comboBox.currentText()
        val = item_tabl_name[f'{text}']
        data = self.DataFromDB(f"""SELECT * FROM {val};""")
        dialog = TableDialog(self.conn)
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

        self.conn = connection

        self.ui.CB_Table.addItems(items_table)
        items_querry = ['Получить список всех зарегистрированных в системе клиентов, имеющих задолженность по кредиту', 'Проверить статус заявки на кредит для определённого клиента', 'Посмотреть все заявки на кредит ожидающие одобрения', 'Проверить историю выдачи кредитов для конкретного клиента', 'Получить список всех открытых кредитов', 'Посмотреть список отказанных заявок на кредит', 'Получить общую сумму всех открытых кредитов', 'Проверить текущий баланс по кредитным счетам клиента']
        self.ui.CB_Querry.addItems(items_querry)
        self.ui.PB_Add.clicked.connect(self.add_data_bd)
        self.ui.PB_Update.clicked.connect(self.update_data_bd)
        self.ui.PB_Delete.clicked.connect(self.delete_data_bd)
        self.ui.PB_Open.clicked.connect(self.open_table)
        self.ui.PB_Ex_Querry.clicked.connect(self.Ex_Qery)

    def add_data_bd(self):
        text = self.ui.CB_Table.currentText()
        val = item_tabl_name[f'{text}']
        self.view_window = VievWindow(self.conn, val, sign=1)
        self.view_window.show()

    def update_data_bd(self):
        text = self.ui.CB_Table.currentText()
        val = item_tabl_name[f'{text}']
        self.view_window = VievWindow(self.conn, val, sign=2)
        self.view_window.show()


    def delete_data_bd(self):
        text = self.ui.CB_Table.currentText()
        val = item_tabl_name[f'{text}']
        delete_dialog = DeleteDialog(conn=self.conn, table_name=val)
        delete_dialog.exec_()

    def open_table(self):
        text = self.ui.CB_Table.currentText()
        val = item_tabl_name[f'{text}']
        data = self.DataFromDB(f"""SELECT * FROM {val};""")
        dialog = TableDialog(self.conn)
        dialog.set_data(data)
        dialog.exec_()

    def Ex_Qery(self):
        # QMessageBox.information(self, "", "Будет добаdлено позже")
        text = self.ui.CB_Querry.currentText()
        val = query_text[f'{text}']
        data = self.DataFromDB(f"""{val}""")
        dialog = TableDialog(self.conn)
        dialog.set_data(data)
        dialog.exec_()

    def DataFromDB(self, query):
        cursor = self.conn.cursor()
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
        self.conn = None
        self.act_win = None

    def login(self):
        uname = self.ui.LE_Login.text()
        passw = self.ui.LE_Password.text()

        self.conn = con_bd(uname, passw)

        role = aut_user(self.conn, uname)
        if role == 'cliet':
            self.act_win = UserWind(self.conn)
            self.act_win.show()
            self.close()
        elif role == 'administrator':
            self.act_win = AdminWind(self.conn)
            self.act_win.show()
            self.close()
        elif role == 'menedjer':
            self.act_win = ManajerWind(self.conn)
            self.act_win.show()
            self.close()
        else:
            QMessageBox.warning(self, 'Error', 'Invalid role')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = Authorization()
    login_window.show()
    sys.exit(app.exec())
