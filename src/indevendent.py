import sys
import PyQt6.QtWidgets as widgets
from PyQt6.QtGui import QFont, QIntValidator
from PyQt6.QtCore import Qt

CATEGORY_WIDTH = 200
PRICE_WIDTH = 50
AMOUNT_WIDTH = 50
SELL_COUNT_WIDTH = 50

class invItemWidget(widgets.QWidget):

    categories = ['-']
    deals = {
        '-' : None
        }

    @classmethod
    def add_category(self, name):
        invItemWidget.categories.append(name)
        invItemWidget.categories.sort()
        invItemWidget.deals.update({name : None})

    def __init__(self, name = 'New Product', category = '-', price = 0.0, count = 0, parent_window = None):
        super(invItemWidget, self).__init__()
        self.product_name = name
        self.product_category = category
        self.price = price
        self.inv_count = count
        self.parent_window = parent_window

        self.name_box = widgets.QLineEdit(self.product_name)
        self.category_box = widgets.QComboBox()
        self.category_box.addItems(invItemWidget.categories)
        self.category_box.setFixedWidth(CATEGORY_WIDTH)
        self.category_box.setInsertPolicy(widgets.QComboBox.InsertPolicy.InsertAlphabetically)
        self.price_box = widgets.QLineEdit(str(self.price))
        self.price_box.setFixedWidth(PRICE_WIDTH)
        self.amountBox = widgets.QSpinBox()
        self.amountBox.setButtonSymbols(widgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.amountBox.setRange(0,999)
        self.amountBox.setFixedWidth(AMOUNT_WIDTH)
        self.sellCountBox = widgets.QSpinBox()
        self.sellCountBox.setButtonSymbols(widgets.QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.sellCountBox.setRange(0,self.inv_count)
        self.sellCountBox.setFixedWidth(SELL_COUNT_WIDTH)

        self.category_box.currentTextChanged.connect(self.updateCategory)
        self.amountBox.editingFinished.connect(self.updateAmount)
        self.name_box.editingFinished.connect(self.setName)
        self.price_box.editingFinished.connect(self.setPrice)

        self.hbox = widgets.QHBoxLayout()
        self.hbox.addWidget(self.name_box)
        self.hbox.addWidget(self.category_box)
        self.hbox.addWidget(self.amountBox)
        self.hbox.addWidget(self.price_box)
        self.hbox.addWidget(self.sellCountBox)

        self.setLayout(self.hbox)

    def setName(self):
        self.product_name = self.name_box.text()
    
    def setPrice(self):
        self.price = float(self.price_box.text())

    def show(self):
        for w in [self, self.name_box, self.category_box, self.price_box, self.sellCountBox]:
            w.setVisible(True)

    def hide(self):
        for w in [self, self.name_box, self.category_box, self.price_box, self.sellCountBox]:
            w.setVisible(False)
    
    def updateAmount(self):
        self.inv_count = self.amountBox.value()
        self.sellCountBox.setRange(0,self.inv_count)

    def complete_sale(self):
        number_sold = self.sellCountBox.value()
        new_amount = self.amountBox.value() - number_sold
        self.sellCountBox.setValue(0)
        self.amountBox.setValue(new_amount)
        self.updateAmount()
        sale = {
            'category': self.product_category,
            'price': self.price,
        }
        return sale, number_sold
    
    def updateCategory(self, name):
        self.product_category = name

class CustomDialog(widgets.QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Configure deals...")
        self.setGeometry(width = 200, height = 100)

        self.layout = widgets.QHBoxLayout()
        self.catDropBox = widgets.QComboBox()
        self.catDropBox.addItems(invItemWidget.categories)

        self.dealDropBox = widgets.QComboBox()
        self.dealDropBox.addItems(['BOGO', 'BULK'])

        self.blankSpacer = widgets.QSpacerItem(1,1,widgets.QSizePolicy.Policy.Expanding,widgets.QSizePolicy.Policy.Minimum)

        self.layout.addWidget(self.catDropBox)
        self.setLayout(self.layout)

class MainWindow(widgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('PyQt Inventory Management System')
        self.setGeometry(100, 100, 900, 500)

        self.items = []
        self.total_profit = 0.0

        self.itemPanel = widgets.QWidget()
        self.itemPanelLayout = widgets.QVBoxLayout()

        self.addingDock = widgets.QDockWidget('Item Control')
        self.addingDock.setFeatures(widgets.QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.addingDock)

        self.addingMenu = widgets.QWidget()
        self.addingMenuLayout = widgets.QVBoxLayout()

        self.addItemButton = widgets.QPushButton('New Item')
        self.addItemButton.clicked.connect(self.add_blank_item)
        self.addCategoryBox = widgets.QLineEdit(self, placeholderText = 'Add new category...')
        self.addCategoryButton = widgets.QPushButton('Add')
        self.addCategoryButton.clicked.connect(self.add_new_category)
        self.configureDealsButton = widgets.QPushButton('Configure deals...')

        self.addingMenuLayout.addWidget(self.addItemButton)
        self.addingMenuLayout.addWidget(self.addCategoryBox)
        self.addingMenuLayout.addWidget(self.addCategoryButton)

        self.addingMenuLayout.addSpacerItem(widgets.QSpacerItem(1,1,widgets.QSizePolicy.Policy.Minimum, widgets.QSizePolicy.Policy.Expanding))
        self.profitLabel = widgets.QLabel("Today's Profit:   $ --.--")
        self.addingMenuLayout.addWidget(self.profitLabel)

        self.sellButton = widgets.QPushButton('Sell')
        self.sellButton.clicked.connect(self.sale_update_inventory)
        self.addingMenuLayout.addWidget(self.sellButton)

        self.addingMenu.setLayout(self.addingMenuLayout)
        self.addingDock.setWidget(self.addingMenu)

        self.itemPanelLayout.addSpacerItem(widgets.QSpacerItem(1,1,widgets.QSizePolicy.Policy.Minimum, widgets.QSizePolicy.Policy.Expanding))
        self.itemPanel.setLayout(self.itemPanelLayout)

        self.scroller = widgets.QScrollArea()
        self.scroller.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroller.setWidgetResizable(True)
        self.scroller.setWidget(self.itemPanel)

        self.searchbar = widgets.QLineEdit()
        self.searchbar.setPlaceholderText('Search items...')
        self.searchbar.textChanged.connect(self.update_display)

        headers = widgets.QWidget()
        headersLayout = widgets.QHBoxLayout()
        headersLayout.addSpacerItem(widgets.QSpacerItem(40,1))
        PROD_LABEL = widgets.QLabel('Product')
        PROD_LABEL.setAlignment(Qt.AlignmentFlag.AlignCenter)
        headersLayout.addWidget(PROD_LABEL)
        CAT_LABEL = widgets.QLabel('Category')
        CAT_LABEL.setFixedWidth(CATEGORY_WIDTH)
        CAT_LABEL.setAlignment(Qt.AlignmentFlag.AlignCenter)
        headersLayout.addWidget(CAT_LABEL)
        AMT_LABEL = widgets.QLabel('In Stock')
        AMT_LABEL.setFixedWidth(AMOUNT_WIDTH)
        AMT_LABEL.setAlignment(Qt.AlignmentFlag.AlignCenter)
        headersLayout.addWidget(AMT_LABEL)
        PRC_LABEL = widgets.QLabel('Price')
        PRC_LABEL.setFixedWidth(PRICE_WIDTH)
        PRC_LABEL.setAlignment(Qt.AlignmentFlag.AlignCenter)
        headersLayout.addWidget(PRC_LABEL)
        SELL_LABEL = widgets.QLabel('Sell')
        SELL_LABEL.setFixedWidth(SELL_COUNT_WIDTH)
        SELL_LABEL.setAlignment(Qt.AlignmentFlag.AlignCenter)
        headersLayout.addWidget(SELL_LABEL)
        headersLayout.addSpacerItem(widgets.QSpacerItem(30,1))
        headers.setLayout(headersLayout)

        container = widgets.QWidget()
        containerLayout = widgets.QVBoxLayout()
        containerLayout.addWidget(self.searchbar)
        containerLayout.addWidget(headers)
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
        new_item = invItemWidget(parent_window = self)
        self.items.append(new_item)
        self.itemPanelLayout.insertWidget(self.itemPanelLayout.count()-1, new_item)
        self.itemPanel.setLayout(self.itemPanelLayout)

    def add_new_category(self):
        new_category = self.addCategoryBox.text()
        if new_category != '' and new_category not in invItemWidget.categories:
            invItemWidget.add_category(new_category)
            for item in self.items:
                item.category_box.addItem(new_category)
        self.addCategoryBox.clear()

    def calculate_sales_price(self, sales):
        sales_price = 0
        cat_lists = dict()
        for cat in invItemWidget.categories:
            cat_list = [sale['price'] for sale in sales if sales['category'] == cat]
            cat_list.sort()
            if not cat_list.isEmpty():
                cat_lists.update({cat : cat_list})
        for cat in cat_lists.keys():
            deal = invItemWidget.deals[cat]
            if deal is not None:
                num_bought = cat.len()
                if deal[0] == 'BOGO':
                    times = (num_bought // deal[1]) * deal[2]
                    for i in range(times):
                        cat.remove(0)
                elif deal[0] == 'BULK':
                    times = (num_bought // deal[1])
                    for i in range(times):
                        for j in range(deal[1]):
                            cat.remove(0)
                        cat.append(deal[2])
                else:
                    pass
        sales_price = sum([sum(cat) for cat in cat_lists.values()])
        return sales_price

    def sale_update_inventory(self):
        sales = []
        for item in self.items:
            sale, num_sold = item.complete_sale()
            sales += [sale] * num_sold
        sale_amount = self.calculate_sales_price(sales)
        self.increase_profit(sale_amount)

    def increase_profit(self, amount):
        self.total_profit += amount
        self.profitLabel.setText(f"Today's Profit: ${self.total_profit:.2f}")

if __name__ == '__main__':
    app = widgets.QApplication(sys.argv)

    # create the main window
    window = MainWindow()

    # start the event loop
    sys.exit(app.exec())