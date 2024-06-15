import sys
import psycopg2
# from PyQt6 import *
# from PyQt6.QtGui import *
# from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from AdminWindowUI import Ui_AdminWind
from AutorizationWindowUI import Ui_Autorizations
from UserWindowUI import Ui_UserWindow
from ManajerWindowUI import Ui_Manajer


def con_bd(uname, passw):
    try:
        con = psycopg2.connect(dbname='test', user=uname, password=passw, host='localhost')
        return con
    except psycopg2.Error as e:
        print(f"Error:{e}")


def aut_user(conn, username):
    values = ('cliet', 'administrator', 'menedjer')

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
    def __init__(self, connection):
        super().__init__()
        self.ui = Ui_AdminWind()
        self.ui.setupUi(self)

        self.connection = connection


class ManajerWind(QMainWindow):
    def __init__(self, connection):
        super().__init__()
        self.ui = Ui_Manajer()
        self.ui.setupUi(self)

        self.connection = connection


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
