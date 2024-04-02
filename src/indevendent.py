import sys
import PyQt6.QtWidgets as widgets
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class invItemWidget(widgets.QWidget):

    product_types = []

    @classmethod
    def add_product_type(name):
        invItemWidget.product_types.append(name)
        invItemWidget.product_types = invItemWidget.product_types.sorted()

    def __init__(self):
        super(invItemWidget, self).__init__()

        self.product_name = 'New Product'
        self.product_category = None
        self.price = 0.0
        self.inv_count = 0

        self.name_box = widgets.QLineEdit(self.product_name)
        self.category_box = widgets.QComboBox()
        self.category_box.addItems(invItemWidget.product_types)
        self.price_box = widgets.QLineEdit(str(self.price))

        self.name_box.editingFinished.connect(self.setName)
        self.price_box.editingFinished.connect(self.setPrice)

        self.hbox = widgets.QHBoxLayout()
        self.hbox.addWidget(self.name_box)
        self.hbox.addWidget(self.category_box)
        self.hbox.addWidget(self.price_box)

        self.setLayout(self.hbox)

    def setName(self):
        self.product_name = self.name_box.text()
    
    def setPrice(self):
        self.price = float(self.price_box.text())

    def show(self):
        for w in [self, self.name_box, self.category_box, self.price_box]:
            w.setVisible(True)

    def hide(self):
        for w in [self, self.name_box, self.category_box, self.price_box]:
            w.setVisible(False)


class MainWindow(widgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('PyQt Inventory Management System')
        self.setGeometry(100, 100, 600, 500)

        self.items = []

        self.itemPanel = widgets.QWidget()
        self.itemPanelLayout = widgets.QVBoxLayout()

        self.addingDock = widgets.QDockWidget('Item Control')
        self.addingDock.setFeatures(widgets.QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.addingDock)

        # create a QLabel widget
        #testBox = invItemWidget()

        self.addingMenu = widgets.QWidget()
        self.addingMenuLayout = widgets.QVBoxLayout()

        self.addItemButton = widgets.QPushButton('New Item')
        self.addItemButton.clicked.connect(self.add_blank_item)
        self.addCategoryBox = widgets.QLineEdit(self, placeholderText = 'Add new category...')
        self.addCategoryButton = widgets.QPushButton('Add')

        self.addingMenuLayout.addWidget(self.addItemButton)
        self.addingMenuLayout.addWidget(self.addCategoryBox)
        self.addingMenuLayout.addWidget(self.addCategoryButton)

        self.addingMenu.setLayout(self.addingMenuLayout)
        self.addingDock.setWidget(self.addingMenu)

        #spacer = widgets.QSpacerItem(1, 1, widgets.QSizePolicy.Policy.Minimum, widgets.QSizePolicy.Policy.Expanding)
        #layout.addItem(spacer)
        #self.controls.setLayout(self.controlsLayout)

        # Scroll Area Properties.
        self.scroller = widgets.QScrollArea()
        self.scroller.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroller.setWidgetResizable(True)
        self.scroller.setWidget(self.itemPanel)

        self.searchbar = widgets.QLineEdit()
        self.searchbar.textChanged.connect(self.update_display)

        container = widgets.QWidget()
        containerLayout = widgets.QVBoxLayout()
        containerLayout.addWidget(self.searchbar)
        containerLayout.addWidget(self.scroller)

        container.setLayout(containerLayout)
        self.setCentralWidget(container)

        self.show()

    def update_display(self, text):

        for item in self.items:
            if text.lower() in item.product_name.lower():
                item.show()
            else:
                item.hide()

    def add_blank_item(self):
        new_item = invItemWidget()
        self.items.append(new_item)
        self.itemPanelLayout.addWidget(new_item)
        self.itemPanel.setLayout(self.itemPanelLayout)

if __name__ == '__main__':
    app = widgets.QApplication(sys.argv)

    # create the main window
    window = MainWindow()

    # start the event loop
    sys.exit(app.exec())