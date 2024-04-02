import sys
import PyQt6.QtWidgets as widgets
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class invItemWidget(widgets.QWidget):

    categories = ['-']

    @classmethod
    def add_category(self, name):
        invItemWidget.categories.append(name)
        invItemWidget.categories.sort()

    def __init__(self):
        super(invItemWidget, self).__init__()

        self.product_name = 'New Product'
        self.product_category = '-'
        self.price = 0.0
        self.inv_count = 0

        self.name_box = widgets.QLineEdit(self.product_name)
        self.category_box = widgets.QComboBox()
        self.category_box.addItems(invItemWidget.categories)
        self.category_box.setFixedWidth(100)
        self.price_box = widgets.QLineEdit(str(self.price))
        self.price_box.setFixedWidth(50)

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
        self.addCategoryButton.clicked.connect(self.add_new_category)

        self.addingMenuLayout.addWidget(self.addItemButton)
        self.addingMenuLayout.addWidget(self.addCategoryBox)
        self.addingMenuLayout.addWidget(self.addCategoryButton)

        self.addingMenu.setLayout(self.addingMenuLayout)
        self.addingDock.setWidget(self.addingMenu)

        #spacer = widgets.QSpacerItem(1, 1, widgets.QSizePolicy.Policy.Minimum, widgets.QSizePolicy.Policy.Expanding)
        #self.itemPanelLayout.addItem(spacer)
        #self.itemPanel.setLayout(self.itemPanelLayout)

        self.itemPanelLayout.addSpacerItem(widgets.QSpacerItem(1,1,widgets.QSizePolicy.Policy.Minimum, widgets.QSizePolicy.Policy.Expanding))
        self.itemPanel.setLayout(self.itemPanelLayout)

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
        self.itemPanelLayout.insertWidget(self.itemPanelLayout.count()-1, new_item)
        self.itemPanel.setLayout(self.itemPanelLayout)

    def add_new_category(self):
        new_category = self.addCategoryBox.text()
        if new_category != '':
            invItemWidget.add_category(new_category)
            for item in self.items:
                item.category_box.addItem(new_category)

if __name__ == '__main__':
    app = widgets.QApplication(sys.argv)

    # create the main window
    window = MainWindow()

    # start the event loop
    sys.exit(app.exec())