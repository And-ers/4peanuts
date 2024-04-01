import sys
import PyQt6.QtWidgets as widgets
from PyQt6.QtGui import QFont

class invItemWidget(widgets.QWidget):

    product_types = []

    @classmethod
    def add_product_type(name):
        invItemWidget.product_types.append(name)
        invItemWidget.product_types = invItemWidget.product_types.sorted()

    def __init__(self):
        super(invItemWidget, self).__init__()

        self.product_name = 'New Product'
        self.product_type = None
        self.price = 0.0
        self.inv_count = 0

        self.name_box = widgets.QLineEdit(self.product_name)
        self.type_box = widgets.QComboBox()
        self.type_box.addItems(invItemWidget.product_types)
        self.price_box = widgets.QLineEdit(str(self.price))

        self.name_box.editingFinished.connect(self.setName)
        self.name_box.editingFinished.connect(self.setPrice)

        self.hbox = widgets.QHBoxLayout()
        self.hbox.addWidget(self.name_box)
        self.hbox.addWidget(self.type_box)
        self.hbox.addWidget(self.price_box)

    def setName(self):
        self.product_name = self.name_box.text()
    
    def setPrice(self, price):
        self.price = float(self.price_box.text())


class MainWindow(widgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('PyQt Label Widget')
        self.setGeometry(100, 100, 320, 210)

        # create a QLabel widget
        testBox = invItemWidget()

        # place the widget on the window
        layout = widgets.QVBoxLayout()
        layout.addWidget(testBox)
        self.setLayout(layout)

        # show the window
        self.show()


if __name__ == '__main__':
    app = widgets.QApplication(sys.argv)

    # create the main window
    window = MainWindow()

    # start the event loop
    sys.exit(app.exec())