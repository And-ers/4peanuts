import sys
import PyQt6.QtWidgets as widgets
from PyQt6.QtGui import QFont, QIntValidator, QIcon, QAction
from PyQt6.QtCore import Qt, QSize, QObject
from qt_material import apply_stylesheet
import os
from datetime import datetime

# ICONS FROM FUGUE ICONS BY YUSUKE KAMIYAMANE AT https://p.yusukekamiyamane.com/

CATEGORY_WIDTH = 150
PRICE_WIDTH = 80
AMOUNT_WIDTH = 80
SELL_COUNT_WIDTH = 80

class invItemWidget(widgets.QWidget):

    categories = ['-']
    sources = ['-']
    deals = {
        '-' : None
        }

    @classmethod
    def add_category(self, name):
        invItemWidget.categories.append(name)
        invItemWidget.categories.sort()
        invItemWidget.deals.update({name : None})

    @classmethod
    def add_source(self, name):
        invItemWidget.sources.append(name)
        invItemWidget.sources.sort()

    def __init__(self, name = 'New Product', category = '-', source = '-', price = 0.0, count = 0, parent_window = None):
        super(invItemWidget, self).__init__()
        self.product_name = name
        self.product_category = category
        self.product_source = source
        self.price = price
        self.inv_count = count
        self.parent_window = parent_window

        self.name_box = widgets.QLineEdit(self.product_name)
        self.category_box = widgets.QComboBox()
        self.category_box.addItems(invItemWidget.categories)
        self.category_box.setFixedWidth(CATEGORY_WIDTH)
        self.category_box.setInsertPolicy(widgets.QComboBox.InsertPolicy.InsertAlphabetically)
        self.category_box.setCurrentIndex([self.category_box.itemText(i) for i in range(self.category_box.count())].index(self.product_category))
        self.source_box = widgets.QComboBox()
        self.source_box.addItems(invItemWidget.sources)
        self.source_box.setFixedWidth(CATEGORY_WIDTH)
        self.source_box.setInsertPolicy(widgets.QComboBox.InsertPolicy.InsertAlphabetically)
        self.source_box.setCurrentIndex([self.source_box.itemText(i) for i in range(self.source_box.count())].index(self.product_source))
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
        self.sellCountBox.valueChanged.connect(parent_window.display_sell_price)

        self.category_box.currentTextChanged.connect(self.updateCategory)
        self.source_box.currentTextChanged.connect(self.updateSource)
        self.amountBox.editingFinished.connect(self.updateAmount)
        self.name_box.editingFinished.connect(self.setName)
        self.price_box.editingFinished.connect(self.setPrice)

        self.hbox = widgets.QHBoxLayout()
        self.hbox.addWidget(self.name_box)
        self.hbox.addWidget(self.category_box)
        self.hbox.addWidget(self.source_box)
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

    def updateSource(self, name):
        self.product_source = name

    def __str__(self):
        return ','.join([self.product_name, self.product_category, self. product_source, str(self.price), str(self.inv_count)])

class CustomDialog(widgets.QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setWindowTitle("Configure deals...")

        self.control_boxes = []

        self.overallLayout = widgets.QVBoxLayout()
        self.inputContainer = widgets.QWidget()
        self.inputLayout = widgets.QHBoxLayout()
        self.catDropBox = widgets.QComboBox()
        self.catDropBox.addItems(invItemWidget.categories)

        self.dealDropBox = widgets.QComboBox()
        self.dealDropBox.addItems(['-', 'BOGO', 'BULK'])
        self.dealDropBox.currentTextChanged.connect(self.show_deal_controls)

        self.blankSpacer = widgets.QSpacerItem(1,1,widgets.QSizePolicy.Policy.Expanding,widgets.QSizePolicy.Policy.Minimum)

        self.BOGOContainer = widgets.QWidget()
        self.BOGOControls = widgets.QHBoxLayout()
        self.BOGOLabel1 = widgets.QLabel('Buy ')
        self.BOGOField1 = widgets.QSpinBox()
        self.BOGOField1.setFixedWidth(30)
        self.BOGOField1.setButtonSymbols(widgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.BOGOLabel2 = widgets.QLabel(', get ')
        self.BOGOField2 = widgets.QSpinBox()
        self.BOGOField2.setFixedWidth(30)
        self.BOGOField2.setButtonSymbols(widgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.BOGOControls.addWidget(self.BOGOLabel1)
        self.BOGOControls.addWidget(self.BOGOField1)
        self.BOGOControls.addWidget(self.BOGOLabel2)
        self.BOGOControls.addWidget(self.BOGOField2)
        self.BOGOContainer.setLayout(self.BOGOControls)

        self.BULKContainer = widgets.QWidget()
        self.BULKControls = widgets.QHBoxLayout()
        self.BULKLabel1 = widgets.QLabel('Buy ')
        self.BULKField1 = widgets.QSpinBox()
        self.BULKField1.setFixedWidth(30)
        self.BULKField1.setButtonSymbols(widgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.BULKLabel2 = widgets.QLabel(' for $')
        self.BULKField2 = widgets.QSpinBox()
        self.BULKField2.setFixedWidth(30)
        self.BULKField2.setButtonSymbols(widgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.BULKControls.addWidget(self.BULKLabel1)
        self.BULKControls.addWidget(self.BULKField1)
        self.BULKControls.addWidget(self.BULKLabel2)
        self.BULKControls.addWidget(self.BULKField2)
        self.BULKContainer.setLayout(self.BULKControls)

        buttons = widgets.QDialogButtonBox.StandardButton.Save | widgets.QDialogButtonBox.StandardButton.Cancel

        self.buttonBox = widgets.QDialogButtonBox(buttons)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.accepted.connect(self.saveDeal)
        self.buttonBox.rejected.connect(self.reject)

        self.inputLayout.addWidget(self.catDropBox)
        self.inputLayout.addWidget(self.dealDropBox)
        self.inputLayout.addSpacerItem(self.blankSpacer)
        self.inputLayout.addWidget(self.BOGOContainer)
        self.inputLayout.addWidget(self.BULKContainer)
        self.BOGOContainer.setVisible(False)
        self.BULKContainer.setVisible(False)
        self.inputContainer.setLayout(self.inputLayout)
        self.overallLayout.addWidget(self.inputContainer)
        self.overallLayout.addWidget(self.buttonBox)
        self.setLayout(self.overallLayout)

    def show_deal_controls(self):
        for box in self.control_boxes:
            box.setVisible(False)
        selection = self.dealDropBox.currentText()
        if selection == 'BOGO':
            for box in self.control_boxes:
                box.setVisible(False)
            self.BOGOContainer.setVisible(True)
        elif selection == 'BULK':
            for box in self.control_boxes:
                box.setVisible(False)
            self.BULKContainer.setVisible(True)

    def saveDeal(self):
        category = self.catDropBox.currentText()
        deal = self.dealDropBox.currentText()
        if deal == 'NONE':
            invItemWidget.deals.update({category : None})
        elif deal == 'BOGO':
            invItemWidget.deals.update({category : ('BOGO', self.BOGOField1.value(), self.BOGOField2.value())})
        elif deal == 'BULK':
            invItemWidget.deals.update({category : ('BULK', self.BULKField1.value(), self.BULKField2.value())})
        self.accept()


class MainWindow(widgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('PyQt Inventory Management System')
        self.setGeometry(100, 100, 1920, 1200)

        self.setStyleSheet("QLineEdit, QComboBox, QSpinBox { color: white }")

        self.sources = {'-': None}
        self.items = []
        self.total_profit = 0.0

        # File menu toolbar.

        button_action = QAction(QIcon("icons/disk.png"), "&Save...", self)
        button_action.setStatusTip("Save inventory to .txt file")
        button_action.triggered.connect(self.save_to_file)
        button_action.setCheckable(True)

        button_action2 = QAction(QIcon("icons/folder-open.png"), "&Open...", self)
        button_action2.setStatusTip("Open items from .txt file")
        button_action2.triggered.connect(self.open_from_file)
        button_action2.setCheckable(True)

        self.setStatusBar(widgets.QStatusBar(self))

        menu = self.menuBar()

        file_menu = menu.addMenu("&File")
        file_menu.addAction(button_action)
        file_menu.addAction(button_action2)
        file_menu.addSeparator()

        # Dock for adding and configuring items and deals.

        self.addingDock = widgets.QDockWidget('Item Control')
        self.addingDock.setFeatures(widgets.QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.addingDock)

        self.addingMenu = widgets.QWidget()
        self.addingMenuLayout = widgets.QVBoxLayout()

        self.addItemButton = widgets.QPushButton('New Item')
        self.addItemButton.clicked.connect(self.add_item)
        self.addCategoryBox = widgets.QLineEdit(self, placeholderText = 'Add new category...')
        self.addCategoryButton = widgets.QPushButton('Add')
        self.addCategoryButton.clicked.connect(self.add_new_category)
        self.configureDealsButton = widgets.QPushButton('Configure deals...')
        self.configureDealsButton.clicked.connect(self.open_deal_dialog)

        self.addingMenuLayout.addWidget(self.addItemButton)
        self.addingMenuLayout.addWidget(self.addCategoryBox)
        self.addingMenuLayout.addWidget(self.addCategoryButton)
        self.addingMenuLayout.addSpacerItem(widgets.QSpacerItem(1,1,widgets.QSizePolicy.Policy.Minimum, widgets.QSizePolicy.Policy.Expanding))
        
        self.sellPriceLabel = widgets.QLabel("Sales Price:   $ --.--")
        self.profitLabel = widgets.QLabel("Today's Profit:   $ --.--")

        self.sellButton = widgets.QPushButton('Sell')
        self.sellButton.clicked.connect(self.sale_update_inventory)
        self.addingMenuLayout.addWidget(self.sellPriceLabel)
        self.addingMenuLayout.addWidget(self.profitLabel)
        self.addingMenuLayout.addWidget(self.sellButton)
        self.addingMenuLayout.addWidget(self.configureDealsButton)

        self.addingMenu.setLayout(self.addingMenuLayout)
        self.addingDock.setWidget(self.addingMenu)

        # Creation of dock that stores features for stock source control.

        self.sourceDock = widgets.QDockWidget('Stock Sources')
        self.sourceDock.setFeatures(widgets.QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.sourceDock)

        self.sourcePanel = widgets.QWidget()
        self.sourcePanelLayout = widgets.QVBoxLayout()
        self.addSourceBox = widgets.QLineEdit(self, placeholderText = 'Add new source...')
        self.addSourceButton = widgets.QPushButton('Add')
        self.addSourceButton.clicked.connect(self.add_new_source)
        self.sourcePanelLayout.addWidget(self.addSourceBox)
        self.sourcePanelLayout.addWidget(self.addSourceButton)

        self.sourceScroll = widgets.QScrollArea()
        self.sourceScroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.sourceScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.sourceScroll.setWidgetResizable(True)
        self.sourceScrollLayout = widgets.QVBoxLayout()
        self.sourceScrollLayout.addSpacerItem(widgets.QSpacerItem(1,1,widgets.QSizePolicy.Policy.Minimum, widgets.QSizePolicy.Policy.Expanding))
        self.sourceScroll.setLayout(self.sourceScrollLayout)
        self.sourcePanelLayout.addWidget(self.sourceScroll)
        self.sourcePanel.setLayout(self.sourcePanelLayout)
        self.sourceDock.setWidget(self.sourcePanel)

        # Setup of inner item panel.

        self.itemPanel = widgets.QWidget()
        self.itemPanelLayout = widgets.QVBoxLayout()
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
        SRC_LABEL = widgets.QLabel('Source')
        SRC_LABEL.setFixedWidth(CATEGORY_WIDTH)
        SRC_LABEL.setAlignment(Qt.AlignmentFlag.AlignCenter)
        headersLayout.addWidget(SRC_LABEL)
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

    def update_display(self):
        for item in self.items:
            item.hide()
            if self.searchbar.text().lower() in item.product_name.lower() and item.product_source == '-':
                item.show()
            if self.searchbar.text().lower() in item.product_name.lower() and self.sources[item.product_source] is not None:
                    if self.sources[item.product_source].isChecked():
                        item.show()

    def add_item(self, pad = None, name = 'New Product', category = '-', source = '-', price = 0.0, count = 0, parent_window = None):
        new_item = invItemWidget(name = name, category = category, source = source, price = price, count = count, parent_window = self)
        self.items.append(new_item)
        self.itemPanelLayout.insertWidget(self.itemPanelLayout.count()-1, new_item)
        self.itemPanel.setLayout(self.itemPanelLayout)

    def add_new_category(self, name = None):
        if isinstance(name, str):
            new_category = name
        else:
            new_category = self.addCategoryBox.text()
        if new_category != '' and new_category not in invItemWidget.categories:
            invItemWidget.add_category(new_category)
            for item in self.items:
                item.category_box.addItem(new_category)
        self.addCategoryBox.clear()

    def add_new_source(self, name = None):
        if isinstance(name, str):
            new_source = name
        else:
            new_source = self.addSourceBox.text()
        if new_source != '' and new_source not in invItemWidget.sources:
            invItemWidget.add_source(new_source)
            for item in self.items:
                item.source_box.addItem(new_source)
            source_check = widgets.QCheckBox(new_source, self)
            source_check.setChecked(True)
            source_check.stateChanged.connect(self.update_display)
            self.sources.update({new_source: source_check})
            self.sourceScrollLayout.insertWidget(self.sourceScrollLayout.count()-1, source_check)
        self.addSourceBox.clear()

    def calculate_sales_price(self, sales):
        sales_price = 0
        cat_lists = dict()
        for cat in invItemWidget.categories:
            cat_list = [sale['price'] for sale in sales if sale['category'] == cat]
            cat_list.sort()
            if cat_list != []:
                cat_lists.update({cat : cat_list})
        for cat in cat_lists.keys():
            deal = invItemWidget.deals[cat]
            if deal is not None:
                num_bought = len(cat_lists[cat])
                if deal[0] == 'BOGO':
                    times = (num_bought // (deal[1]+deal[2])) * deal[2]
                    for i in range(times):
                        cat_lists[cat].pop(0)
                elif deal[0] == 'BULK':
                    times = (num_bought // (deal[1]+deal[2]))
                    for i in range(times):
                        for j in range(deal[1]):
                            cat_lists[cat].pop(0)
                        cat_lists[cat].append(deal[2])
                else:
                    pass
        sales_price = sum([sum(cat) for cat in cat_lists.values()])
        return sales_price
    
    def display_sell_price(self):
        sales = []
        for item in self.items:
            sale = {
            'category': item.product_category,
            'price': item.price,
        }
            num_sold = item.sellCountBox.value()
            sales += [sale] * num_sold
        self.sellPriceLabel.setText(f'Sales Price:   ${self.calculate_sales_price(sales):.2f}')

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

    def open_deal_dialog(self):
        dlg = CustomDialog(self)
        dlg.exec()
    
    def save_to_file(self):
        filename = './saves/4peanuts-' + datetime.now().strftime("%Y_%m_%d-%H_%M_%S") + '-save.fpn'
        with open(filename, 'w+') as f:
            f.write('$ CATEGORIES\n')
            f.writelines([cat + '\n' for cat in invItemWidget.categories if cat != '-'])
            f.write('$ SOURCES\n')
            f.writelines([src + '\n' for src in invItemWidget.sources if src != '-'])
            f.write('$ DEALS\n')
            f.writelines([deal + ':' + invItemWidget.deals[deal] + '\n' for deal in invItemWidget.deals.keys() if invItemWidget.deals[deal] is not None])
            f.write('$ ITEMS\n')
            f.writelines([str(item) + '\n' for item in self.items])
            

    def open_from_file(self):
        print('Function open_from_file not implemented.')
        filename, ok = widgets.QFileDialog.getOpenFileName(
            self,
            "Select a File", 
            ".\\saves\\", 
            "4Peanuts (*.fpn)"
        )
        if filename:
            with open(filename, 'r') as f:
                f.readline()
                nextline = f.readline().strip('\n')
                while nextline[0] != '$':
                    self.add_new_category(nextline)
                    nextline = f.readline().strip('\n')
                nextline = f.readline().strip('\n')
                while nextline[0] != '$':
                    self.add_new_source(nextline)
                    nextline = f.readline().strip('\n')
                nextline = f.readline().strip('\n')
                while nextline[0] != '$':
                    cat, deal = nextline.split(':')
                    invItemWidget.deals.update({cat: deal})
                    nextline = f.readline().strip('\n')
                nextline = f.readline().strip('\n')
                while nextline != '':
                    name, category, source, price, count = nextline.split(',')
                    self.add_item(name = name, category = category, source = source, price = float(price), count = int(count), parent_window = self)
                    nextline = f.readline().strip('\n')
        
if __name__ == '__main__':
    app = widgets.QApplication(sys.argv)

    # create the main window
    window = MainWindow()
    apply_stylesheet(app, theme='dark_blue.xml')

    # start the event loop
    sys.exit(app.exec())