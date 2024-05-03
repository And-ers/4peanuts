import sys
import PyQt6.QtWidgets as widgets
from PyQt6.QtGui import QFont, QIntValidator, QIcon, QAction, QPalette
from PyQt6.QtCore import Qt, QSize, QObject, QEvent
from qt_material import apply_stylesheet
import os
from datetime import datetime
from ast import literal_eval

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.figure import Figure

# .png ICONS FROM FUGUE ICONS BY YUSUKE KAMIYAMANE AT https://p.yusukekamiyamane.com/
# .svg ICONS FROM PYTHONGUIS.COM AT https://www.pythonguis.com/tutorials/custom-title-bar-pyqt6/

#################################################
# Width constants to describe the size of the
# inner labels and boxes for each item.

CATEGORY_WIDTH = 150
PRICE_WIDTH = 80
AMOUNT_WIDTH = 80
SELL_COUNT_WIDTH = 80

import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
halfHourFmt = mdates.DateFormatter('%H:%M')
halfHourLoc = mdates.MinuteLocator([0,30])


import seaborn as sns
sns.set_theme()

#################################################
#
#   class invItemWidget:
#   
#   Class that represents an item object.
#   Item categories, sources, and deals for
#   each category are stored as class variables.
#   
#   Each invItemWidget has the name, category,
#   source, price, and count of the item it
#   represents, and displays them all within
#   the main scroll area.

class invItemWidget(widgets.QWidget):

    categories = ['-']
    sources = ['-']
    deals = {
        '-' : None
        }

    # Add a new category to the class

    @classmethod
    def add_category(self, name):
        invItemWidget.categories.append(name)
        invItemWidget.categories.sort()
        invItemWidget.deals.update({name : None})

    # Add a new inventory source to the class

    @classmethod
    def add_source(self, name):
        invItemWidget.sources.append(name)
        invItemWidget.sources.sort()

    # Initializer to create a new invItemWidget

    def __init__(self, name = 'New Product', category = '-', source = '-', price = 0.0, count = 0, parent_window = None):
        super(invItemWidget, self).__init__()
        self.product_name = name
        self.product_category = category
        self.product_source = source
        self.price = price
        self.inv_count = count
        self.parent_window = parent_window
        
        ### CREATION OF REPRESENTATIVE LABELS AND FIELDS

        # Field (LineEdit) that contains the name of the product

        self.name_box = widgets.QLineEdit(self.product_name)

        # Field (ComboBox) that contains the category the product falls under

        self.category_box = widgets.QComboBox()
        self.category_box.addItems(invItemWidget.categories)
        self.category_box.setFixedWidth(CATEGORY_WIDTH)
        self.category_box.setInsertPolicy(widgets.QComboBox.InsertPolicy.InsertAlphabetically)
        self.category_box.setCurrentIndex([self.category_box.itemText(i) for i in range(self.category_box.count())].index(self.product_category))

        # Field (ComboBox) that contains the source where the item originates

        self.source_box = widgets.QComboBox()
        self.source_box.addItems(invItemWidget.sources)
        self.source_box.setFixedWidth(CATEGORY_WIDTH)
        self.source_box.setInsertPolicy(widgets.QComboBox.InsertPolicy.InsertAlphabetically)
        self.source_box.setCurrentIndex([self.source_box.itemText(i) for i in range(self.source_box.count())].index(self.product_source))
        
        # Field (LineEdit) that contains the price of the item
        
        self.price_box = widgets.QLineEdit(str(self.price))
        self.price_box.setFixedWidth(PRICE_WIDTH)

        # Field (SpinBox) that contains the stock count of the item

        self.amountBox = widgets.QSpinBox()
        self.amountBox.setButtonSymbols(widgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.amountBox.setRange(0,999)
        self.amountBox.setFixedWidth(AMOUNT_WIDTH)
        self.amountBox.setValue(self.inv_count)

        # Field (SpinBox) that contains the amount of the item to sell

        self.sellCountBox = widgets.QSpinBox()
        self.sellCountBox.setButtonSymbols(widgets.QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.sellCountBox.setRange(0,self.inv_count)
        self.sellCountBox.setFixedWidth(SELL_COUNT_WIDTH)

        # Connect all of the above fields to the functions that update the inventory

        self.category_box.currentTextChanged.connect(self.updateCategory)
        self.source_box.currentTextChanged.connect(self.updateSource)
        self.amountBox.editingFinished.connect(self.updateAmount)
        self.name_box.editingFinished.connect(self.setName)
        self.price_box.editingFinished.connect(self.setPrice)
        self.sellCountBox.valueChanged.connect(parent_window.display_sell_price)

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

class DealsDialog(widgets.QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setWindowTitle("Configure deals...")
        self.resize(600,400)

        self.control_boxes = []

        self.nonlabelContainer = widgets.QWidget()
        self.nonlabelLayout = widgets.QVBoxLayout()
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
        self.BOGOField1.setFixedWidth(60)
        self.BOGOField1.setButtonSymbols(widgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.BOGOLabel2 = widgets.QLabel(', get ')
        self.BOGOField2 = widgets.QSpinBox()
        self.BOGOField2.setFixedWidth(60)
        self.BOGOField2.setButtonSymbols(widgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.BOGOControls.addWidget(self.BOGOLabel1)
        self.BOGOControls.addWidget(self.BOGOField1)
        self.BOGOControls.addWidget(self.BOGOLabel2)
        self.BOGOControls.addWidget(self.BOGOField2)
        self.BOGOContainer.setLayout(self.BOGOControls)
        self.control_boxes.append(self.BOGOContainer)

        self.BULKContainer = widgets.QWidget()
        self.BULKControls = widgets.QHBoxLayout()
        self.BULKLabel1 = widgets.QLabel('Buy ')
        self.BULKField1 = widgets.QSpinBox()
        self.BULKField1.setFixedWidth(60)
        self.BULKField1.setButtonSymbols(widgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.BULKLabel2 = widgets.QLabel(' for $')
        self.BULKField2 = widgets.QDoubleSpinBox()
        self.BULKField2.setDecimals(2)
        self.BULKField2.setFixedWidth(60)
        self.BULKField2.setButtonSymbols(widgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.BULKControls.addWidget(self.BULKLabel1)
        self.BULKControls.addWidget(self.BULKField1)
        self.BULKControls.addWidget(self.BULKLabel2)
        self.BULKControls.addWidget(self.BULKField2)
        self.BULKContainer.setLayout(self.BULKControls)
        self.control_boxes.append(self.BULKContainer)

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
        self.inputContainer.setFixedHeight(100)
        self.nonlabelLayout.addWidget(self.inputContainer)
        self.nonlabelLayout.addWidget(self.buttonBox)
        self.nonlabelContainer.setLayout(self.nonlabelLayout)

        self.dealLabels = widgets.QScrollArea()
        self.dealLabels.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.dealLabels.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.dealLabels.setWidgetResizable(True)
        self.dealLabelsLayout = widgets.QVBoxLayout()
        for category in invItemWidget.categories:
            if invItemWidget.deals[category] is not None:
                self.dealLabelsLayout.addWidget(self.create_deal_entry(category))
        self.dealLabels.setLayout(self.dealLabelsLayout)
        self.dealLabelsLayout.addSpacerItem(widgets.QSpacerItem(1,1,widgets.QSizePolicy.Policy.Minimum, widgets.QSizePolicy.Policy.Expanding))

        self.overallLayout = widgets.QVBoxLayout()
        self.overallLayout.addWidget(self.dealLabels)
        self.overallLayout.addWidget(self.nonlabelContainer)
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

    def create_deal_entry(self, category):
        cat_label = widgets.QLabel(category)
        deal = invItemWidget.deals[category]
        deal_type = deal[0]
        deal_string = ''
        if deal_type == 'BOGO':
            deal_string = 'Buy ' + str(deal[1]) + ' get ' + str(deal[2]) + ' free'
        if deal_type == 'BULK':
            deal_string = 'Get ' + str(deal[1]) + ' for $' + str(deal[2])
        deal_label = widgets.QLabel(deal_string)
        deal_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        dealEntry = widgets.QWidget()
        dealEntryLayout = widgets.QHBoxLayout()
        dealEntryLayout.addWidget(cat_label)
        dealEntryLayout.addWidget(deal_label)
        dealEntry.setLayout(dealEntryLayout)
        return dealEntry
        

class CustomTitleBar(widgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)
        self.setStyleSheet('background-color: rgb(35,38,41);')
        self.initial_pos = None
        title_bar_layout = widgets.QHBoxLayout(self)
        title_bar_layout.setContentsMargins(1, 1, 1, 1)
        title_bar_layout.setSpacing(2)
        self.title = widgets.QLabel(f"{self.__class__.__name__}", self)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet(
            """
        QLabel { font-size: 12pt; margin-left: 48px; }
        """
        )

        if title := parent.windowTitle():
            self.title.setText(title)
        title_bar_layout.addWidget(self.title)
        # Min button
        self.min_button = widgets.QToolButton(self)
        min_icon = QIcon()
        min_icon.addFile(".\\icons\\min.svg")
        self.min_button.setIcon(min_icon)
        self.min_button.clicked.connect(self.window().showMinimized)

        # Max button
        self.max_button = widgets.QToolButton(self)
        max_icon = QIcon()
        max_icon.addFile(".\\icons\\max.svg")
        self.max_button.setIcon(max_icon)
        self.max_button.clicked.connect(self.window().showMaximized)

        # Close button
        self.close_button = widgets.QToolButton(self)
        close_icon = QIcon()
        close_icon.addFile(".\\icons\\close.svg")  # Close has only a single state.
        self.close_button.setIcon(close_icon)
        self.close_button.clicked.connect(self.window().close)

        # Normal button
        self.normal_button = widgets.QToolButton(self)
        normal_icon = QIcon()
        normal_icon.addFile(".\\icons\\normal.svg")
        self.normal_button.setIcon(normal_icon)
        self.normal_button.clicked.connect(self.window().showNormal)
        self.normal_button.setVisible(False)
        # Add buttons
        buttons = [
            self.min_button,
            self.normal_button,
            self.max_button,
            self.close_button,
        ]
        for button in buttons:
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedSize(QSize(24, 24))
            button.setStyleSheet(
                """QToolButton {
                    border: none;
                    padding: 2px;
                }
                """
            )
            title_bar_layout.addWidget(button)

    def window_state_changed(self, state):
        if state == Qt.WindowState.WindowMaximized:
            self.normal_button.setVisible(True)
            self.max_button.setVisible(False)
        else:
            self.normal_button.setVisible(False)
            self.max_button.setVisible(True)

class DataDialog(widgets.QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setWindowTitle("Chart Sales Data")
        self.resize(900,700)

        # Get data

        # Overall window layout

        data_window_layout = widgets.QVBoxLayout()

        # Label for date

        self.data_date_label = widgets.QLabel("Select a log file to chart.")
        self.data_date_label.setStyleSheet("font-size: 20px; qproperty-alignment: AlignCenter; font-weight: bold")
        #self.data_date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.data_date_label.setFixedHeight(50)
        data_window_layout.addWidget(self.data_date_label)

        # Charts

        self.customers_over_time = FigureCanvas(Figure(figsize=(3, 3), dpi=80, tight_layout = True))
        self.items_over_time = FigureCanvas(Figure(figsize=(3,3), dpi=80, tight_layout = True))
        self.profit_over_time = FigureCanvas(Figure(figsize=(3, 3), dpi=80, tight_layout = True))
        self.num_items_sold = FigureCanvas(Figure(figsize=(3, 3), dpi=80, tight_layout = True))

        # Chart layout

        chart_container = widgets.QWidget()
        chart_container_layout = widgets.QGridLayout()
        chart_container_layout.addWidget(self.customers_over_time, 0, 0)
        chart_container_layout.addWidget(self.items_over_time, 0, 1)
        chart_container_layout.addWidget(self.profit_over_time, 1, 0)
        chart_container_layout.addWidget(self.num_items_sold, 1, 1)
        chart_container.setLayout(chart_container_layout)
        data_window_layout.addWidget(chart_container)

        # Button to open data from file

        open_data_button = widgets.QPushButton("Open Data Log")
        open_data_button.setFixedWidth(200)
        open_data_button.clicked.connect(self.read_file_data)
        data_window_layout.addWidget(open_data_button, alignment = Qt.AlignmentFlag.AlignRight)

        # Set overall window layout

        self.setLayout(data_window_layout)

    def read_file_data(self):
        filename, ok = widgets.QFileDialog.getOpenFileName(
            self,
            "Select a File", 
            ".\\logs\\", 
            "Text File (*.txt)"
        )
        if filename:
            self.data_date_label.setText("Sales data for " + filename[-14:-4])
            with open(filename, 'r') as f:
                data_points = f.readlines()
                cot_points = dict()
                iot_points = dict()
                total_profit = 0
                pot_points = dict()
                itemsold_points = dict()
                for datum in data_points:
                    if datum[0] == '$':
                        profit, time, items = datum.split(' ')[1:4]
                        profit, items = float(profit), int(items)
                        total_profit += profit

                        # Data for customers/items/profits over time

                        if int(time[3:5]) >= 30:
                            min = '30'
                        else:
                            min = '00'
                        round_time_str = time[0:2] + ':' + min
                        pot_points.update({ round_time_str : total_profit })
                        if round_time_str in cot_points.keys():
                            cot_points.update({ round_time_str : cot_points[round_time_str]+1 })
                            iot_points.update({ round_time_str : iot_points[round_time_str]+items })
                        else:
                            cot_points.update({ round_time_str : 1 })
                            iot_points.update({ round_time_str : items })
                    else:
                        item_name, item_cat = datum.replace('\n','').split(';')
                        item_title = item_name + '\n(' + item_cat + ')'
                        if item_title in itemsold_points.keys():
                            itemsold_points.update({ item_title : itemsold_points[item_title]+1 })
                        else:
                            itemsold_points.update({ item_title : 1 })

                rounded_times = [(datetime.strptime(time_str, '%H:%M')) for time_str in cot_points.keys()]

                # Plot customers over time
            
                cot_axes = self.customers_over_time.figure.add_subplot()
                cot_y = [cot_points[time_str] for time_str in cot_points.keys()]
                cot_axes.xaxis.set_major_formatter(halfHourFmt)
                cot_axes.xaxis.set_major_locator(halfHourLoc)
                cot_axes.yaxis.set_major_locator(MaxNLocator(integer=True))
                self.customers_over_time.figure.autofmt_xdate(rotation=70, ha='center')
                cot_axes.bar(rounded_times, cot_y, width=0.02, color='mediumturquoise')
                cot_axes.set_title('Customers Over Time')
                cot_axes.set_xlabel('Time', labelpad=15)
                cot_axes.set_ylabel('No. Customers', labelpad=15)
                self.customers_over_time.draw()

                # Plot items sold over time

                iot_axes = self.items_over_time.figure.add_subplot()
                iot_y = [iot_points[time_str] for time_str in iot_points.keys()]
                iot_axes.xaxis.set_major_formatter(halfHourFmt)
                iot_axes.xaxis.set_major_locator(halfHourLoc)
                iot_axes.yaxis.set_major_locator(MaxNLocator(integer=True))
                self.items_over_time.figure.autofmt_xdate(rotation=70, ha='center')
                iot_axes.bar(rounded_times, iot_y, width=0.02, color='mediumspringgreen')
                iot_axes.set_title('Items Sold Over Time')
                iot_axes.set_xlabel('Time', labelpad=15)
                iot_axes.set_ylabel('No. Items Sold', labelpad=15)
                self.items_over_time.draw()

                # Plot profit over time

                pot_axes = self.profit_over_time.figure.add_subplot()
                pot_y = [pot_points[time_str] for time_str in pot_points.keys()]
                pot_axes.xaxis.set_major_formatter(halfHourFmt)
                pot_axes.xaxis.set_major_locator(halfHourLoc)
                pot_axes.yaxis.set_major_formatter('${x:3.2f}')
                pot_axes.yaxis.set_major_locator(MaxNLocator(integer=True))
                self.profit_over_time.figure.autofmt_xdate(rotation=70, ha='center')
                pot_axes.plot(rounded_times, pot_y, color='gold')
                pot_axes.set_title('Cumulative Profit Over Time')
                pot_axes.set_xlabel('Time', labelpad=15)
                pot_axes.set_ylabel('Total Profit', labelpad=15)
                self.profit_over_time.draw()

                # Plot number of each item sold

                itemsold_axes = self.num_items_sold.figure.add_subplot()
                itemsold_x = list(itemsold_points.keys())
                itemsold_y = [itemsold_points[key] for key in itemsold_x]
                itemsold_axes.barh(itemsold_x, itemsold_y, color='salmon')
                itemsold_axes.xaxis.set_major_locator(MaxNLocator(integer=True))
                itemsold_axes.set_xticklabels(itemsold_axes.get_xticklabels(), ha='center')
                itemsold_axes.set_yticklabels(itemsold_axes.get_yticklabels(), ha='center')
                itemsold_axes.tick_params(axis='y', which='major', pad=20)
                itemsold_axes.set_title('Sales by Item')
                itemsold_axes.set_xlabel('No. Sold', labelpad=15)
                itemsold_axes.set_ylabel('Item and Category', labelpad=15)
                self.num_items_sold.draw()

class MainWindow(widgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_pos = None

        self.setWindowTitle('4Peanuts Small Inventory Management')
        self.resize(1280, 800)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { color: white }")

        self.title_bar = CustomTitleBar(self)

        self.sources = {'-': None}
        self.items = []
        self.total_profit = 0.0

        # Dock for adding and configuring items and deals.

        self.addingMenu = widgets.QWidget()
        self.addingMenuLayout = widgets.QVBoxLayout()

        self.addItemButton = widgets.QPushButton('New Item')
        self.addItemButton.clicked.connect(self.add_item)
        self.addCategoryBox = widgets.QLineEdit(self, placeholderText = 'Add new category...')
        self.addCategoryButton = widgets.QPushButton('Add')
        self.addCategoryButton.clicked.connect(self.add_new_category)

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

        self.addingMenu.setLayout(self.addingMenuLayout)

        # Creation of dock that stores features for stock source control.

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

        # File menu toolbar

        button_action = QAction(QIcon("icons/disk.png"), "&Save...", self)
        button_action.setStatusTip("Save inventory to .txt file")
        button_action.triggered.connect(self.save_to_file)
        button_action.setCheckable(True)

        button_action2 = QAction(QIcon("icons/folder-open.png"), "&Open...", self)
        button_action2.setStatusTip("Open items from .txt file")
        button_action2.triggered.connect(self.open_from_file)
        button_action2.setCheckable(True)

        self.setStatusBar(widgets.QStatusBar(self))

        self.menu = widgets.QMenuBar()
        file_menu = self.menu.addMenu("&File")
        file_menu.addAction(button_action)
        file_menu.addAction(button_action2)
        file_menu.addSeparator()

        # Settings menu toolbar

        deals_action = QAction(QIcon("icons/smiley-money.png"), "&Configure Deals...", self)
        deals_action.setStatusTip("View and add deals")
        deals_action.triggered.connect(self.open_deal_dialog)
        deals_action.setCheckable(True)

        settings_menu = self.menu.addMenu("&Settings")
        settings_menu.addAction(deals_action)
        settings_menu.addSeparator()

        # Data menu toolbar

        chart_data_action = QAction(QIcon("icons/chart.png"), "&Chart Data", self)
        chart_data_action.setStatusTip("Create charts from daily logs")
        chart_data_action.triggered.connect(self.open_data_dialog)
        chart_data_action.setCheckable(True)

        data_menu = self.menu.addMenu("&Data")
        data_menu.addAction(chart_data_action)
        data_menu.addSeparator()

        # Container for main app

        itemContainer = widgets.QWidget()
        itemContainerLayout = widgets.QVBoxLayout()
        itemContainerLayout.addWidget(self.searchbar)
        itemContainerLayout.addWidget(headers)
        itemContainerLayout.addWidget(self.scroller)
        itemContainer.setLayout(itemContainerLayout)

        lowerContainer = widgets.QWidget()
        lowerContainerLayout = widgets.QHBoxLayout()
        self.addingMenu.setFixedWidth(200)
        self.sourcePanel.setFixedWidth(200)
        lowerContainerLayout.addWidget(self.addingMenu)
        lowerContainerLayout.addWidget(itemContainer)
        lowerContainerLayout.addWidget(self.sourcePanel)
        lowerContainer.setLayout(lowerContainerLayout)

        overallContainer = widgets.QWidget()
        overallLayout = widgets.QVBoxLayout()
        overallLayout.addWidget(self.title_bar)
        overallLayout.addWidget(self.menu)
        overallLayout.addWidget(lowerContainer)
        overallContainer.setLayout(overallLayout)

        self.setCentralWidget(overallContainer)

        self.setVisible(True)

    def update_display(self):
        for item in self.items:
            item.setVisible(False)
            if self.searchbar.text().lower() in item.product_name.lower() and item.product_source == '-':
                item.setVisible(True)
            if self.searchbar.text().lower() in item.product_name.lower() and self.sources[item.product_source] is not None:
                    if self.sources[item.product_source].isChecked():
                        item.setVisible(True)

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
                    times = num_bought // deal[1]
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
        sales_stat_info = []
        for item in self.items:
            sale, num_sold = item.complete_sale()
            sales += [sale] * num_sold
            sale_copy = sale.copy()
            sale_copy.update({'item' : item.product_name})
            sales_stat_info += [sale_copy] * num_sold
        sale_amount = self.calculate_sales_price(sales)
        self.increase_profit(sale_amount)
        self.update_lifetime_stats(sales_stat_info)
        self.update_daily_stats(sales_stat_info, sale_amount)

    def increase_profit(self, amount):
        self.total_profit += amount
        self.profitLabel.setText(f"Today's Profit: ${self.total_profit:.2f}")

    def open_deal_dialog(self):
        dlg = DealsDialog(self)
        dlg.exec()
    
    def save_to_file(self):
        filename, ok = widgets.QFileDialog.getSaveFileName(self,"Save File",".\\saves\\","4Peanuts (*.fpn)")
        with open(filename, 'w+') as f:
            f.write('$ CATEGORIES\n')
            f.writelines([cat + '\n' for cat in invItemWidget.categories if cat != '-'])
            f.write('$ SOURCES\n')
            f.writelines([src + '\n' for src in invItemWidget.sources if src != '-'])
            f.write('$ DEALS\n')
            f.writelines([str(category) + ':' + str(invItemWidget.deals[category]) + '\n' for category in invItemWidget.deals.keys() if invItemWidget.deals[category] is not None])
            f.write('$ ITEMS\n')
            f.writelines([str(item) + '\n' for item in self.items])
            

    def open_from_file(self):
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
                    deal = literal_eval(deal)
                    invItemWidget.deals.update({cat: deal})
                    nextline = f.readline().strip('\n')
                nextline = f.readline().strip('\n')
                while nextline != '':
                    name, category, source, price, count = nextline.split(',')
                    self.add_item(name = name, category = category, source = source, price = float(price), count = int(count), parent_window = self)
                    nextline = f.readline().strip('\n')

    def update_lifetime_stats(self, sales):
        if not os.path.exists('./logs/lifetime-logs'):
            open('./logs/lifetime-logs', 'x')
        with open('./logs/lifetime-logs', 'r') as f:
            data_lines = f.readlines()
            if not data_lines:
                item_tags, lifetime_sales = [], []
            else:
                item_tags, lifetime_sales = [line.split('#')[0].strip() for line in data_lines], [line.split('#')[1].strip() for line in data_lines]
            for sale in sales:
                item_tag = '[' + sale['category'] + '] ' + sale['item']
                if item_tag in item_tags:
                    lifetime_sales[item_tags.index(item_tag)] = str(int(lifetime_sales[item_tags.index(item_tag)]) + 1)
                else:
                    item_tags.append(item_tag)
                    lifetime_sales.append('1')
        with open('./logs/lifetime-logs', 'w') as f:
            for ind in range(len(item_tags)):
                f.write(item_tags[ind] + ' #' + lifetime_sales[ind] + '\n')
        return
    
    def update_daily_stats(self, sales, amount):
        log_name = './logs/daily-log-' + str(datetime.now().date()) + '.txt'
        with open(log_name, 'a+') as f:
            sale_time = str(datetime.now().time()).split('.')[0]
            f.write('$SALE: ' + str(amount) + ' ' + str(sale_time) + ' ' + str(len(sales)) + ' ITEMS \n')
            for sale in sales:
                f.write(sale['item'] + ';' + sale['category'] + '\n')
        return
    
    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            self.title_bar.window_state_changed(self.windowState())
        super().changeEvent(event)
        event.accept()

    def window_state_changed(self, state):
        self.normal_button.setVisible(state == Qt.WindowState.WindowMaximized)
        self.max_button.setVisible(state != Qt.WindowState.WindowMaximized)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.initial_pos = event.position().toPoint()
        super().mousePressEvent(event)
        event.accept()

    def mouseMoveEvent(self, event):
        if self.initial_pos is not None:
            delta = event.position().toPoint() - self.initial_pos
            self.window().move(
                self.window().x() + delta.x(),
                self.window().y() + delta.y(),
            )
        super().mouseMoveEvent(event)
        event.accept()

    def mouseReleaseEvent(self, event):
        self.initial_pos = None
        super().mouseReleaseEvent(event)
        event.accept()

    def open_data_dialog(self):
        dlg = DataDialog(self)
        dlg.exec()
        
if __name__ == '__main__':
    app = widgets.QApplication(sys.argv)

    # create the main window
    window = MainWindow()
    apply_stylesheet(app, theme='dark_blue.xml')

    # start the event loop
    sys.exit(app.exec())