import sys
from PyQt6.QtWidgets import QApplication, QTableView
from mgr.core.testdata import MyModel

def run():
    app = QApplication(sys.argv)
    tableview = QTableView()
    myModel = MyModel()
    tableview.setModel(myModel)
    tableview.show()
    return app.exec()

if __name__ == "__main__":
    run()