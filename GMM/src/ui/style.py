from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QWidget,
    QListWidget,
    QListWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QHeaderView,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QPlainTextEdit,
    QLabel,
    QTabWidget,
    QCompleter
)
from PySide6.QtGui import (
    QIcon,
    QSyntaxHighlighter,
    QTextFormat,
    QTextCharFormat,
    QColor,
    QFont,
    QFontMetricsF,
    QPalette,
    QTextCursor,
    QPainter
)
from PySide6.QtCore import (
    Qt,
    QRegularExpression,
    QStringListModel,
    QSize,
    QRect
)

def badd(self, *widgets):
    for widget in widgets:
        if isinstance(widget, tuple):
            self._layout.addWidget(*widget)
        else:
            self._layout.addWidget(widget)

def bput(self, target, name):
        target[name] = self
        return self
    
class HBox(QWidget):
    def __init__(self, *widgets):
        super().__init__()

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.add(*widgets)
    
    def __getattr__(self, name):
        return getattr(self._layout, name)

    add = badd
    put = bput
    
class VBox(QWidget):
    def __init__(self, *widgets):
        super().__init__()

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.add(*widgets)
    
    def __getattr__(self, name):
        return getattr(self._layout, name)

    add = badd
    put = bput

class Widget(QWidget):
    def __init__(self, caption, widget):
        super().__init__()

        self._widget = widget
        self._layout = QHBoxLayout(self)

        if caption != "":
            self._label = QLabel(caption)
            self._layout.addWidget(self._label)
            
        self._layout.addWidget(self._widget)
    
    def __getattr__(self, name):
        return getattr(self._widget, name)
    
    put = bput

class Label(Widget):
    def __init__(self, *args, caption=""):
        label = QLabel(*args)

        super().__init__(caption, label)

    @property
    def text(self):
        return self._widget.text()
    
    @text.setter
    def text(self, value):
        return self._widget.setText(str(value))

class Button(Widget):
    def __init__(self, *args, caption=""):
        pushbutton = QPushButton(*args)

        super().__init__(caption, pushbutton)

class Input(Widget):
    def __init__(self, *args, caption=""):
        lineedit = QLineEdit(*args)

        super().__init__(caption, lineedit)
    
    @property
    def text(self):
        return self._widget.text()
    
    @text.setter
    def text(self, value):
        return self._widget.setText(str(value))

class ListItem(QListWidgetItem):
    def __init__(self, name, data):
        super().__init__(name)

        self.set(data)
    
    def get(self):
        return self.data(Qt.UserRole)
    
    def set(self, data):
        return self.setData(Qt.UserRole, data)
    
    def disable(self, disabled):
        font = self.font()
        font.setItalic(disabled)
        self.setFont(font)

class List(Widget):
    def __init__(self, *args, caption=""):
        listwidget = QListWidget(*args)

        super().__init__(caption, listwidget)

    def add(self, name, data, disabled=False):
        item = ListItem(name, data)
        if disabled: item.disable(True)

        return self._widget.addItem(item)
    
class DictItem(QTreeWidgetItem):
    def __init__(self, name, data):
        super().__init__([name])

        self.set(data)
    
    def get(self):
        return self.data(0, Qt.UserRole)
    
    def set(self, data):
        return self.setData(0, Qt.UserRole, data)
    
    def disable(self, disabled):
        font = self.font()
        font.setItalic(disabled)
        self.setFont(font)

class Dict(Widget):
    def __init__(self, labels, *args, caption=""):
        treewidget = QTreeWidget(*args)
        treewidget.setColumnCount(len(labels))
        treewidget.setHeaderLabels(labels)

        treewidget.header().setStretchLastSection(False)
        treewidget.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        treewidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        super().__init__(caption, treewidget)
    
    def add(self, name, data, widget, disabled=False):
        item = DictItem(name, data)
        if disabled: item.disable(True)

        self._widget.addTopLevelItem(item)

        return self._widget.setItemWidget(item, 1, widget)

class TabBox(Widget):
    def __init__(self, *widgets, caption=""):
        tabwidget = QTabWidget()

        for widgetdata in widgets:
            tabwidget.addTab(widgetdata[1], widgetdata[0])

        super().__init__(caption, tabwidget)