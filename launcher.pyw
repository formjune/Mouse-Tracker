import pip


# install modules
for module in "pip", "numpy", "PyQt5", "opencv-python":
    pip.main(["install", module])


if __name__ == "__main__":
    import sys
    from PyQt5.Qt import *
    from MainWindow import MainWindow
    app = QApplication([])
    a = MainWindow()
    a.show()
    sys.exit(app.exec())
