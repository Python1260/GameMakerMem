from .style import (
    Qt,
    QWidget,
    Widget,
    QPlainTextEdit,

    QFontMetricsF,
    QFont,

    QSyntaxHighlighter,
    QTextCharFormat,
    QColor,
    QRegularExpression,
    QPalette,

    QCompleter,
    QStringListModel,
    QTextCursor,

    QPainter,
    QSize,
    QRect,
    QTextEdit,
    QTextFormat
)

def getfromfile(filename):
    with open(filename) as file:
        return [pair.split("=")[0] for pair in file.read().split("\n")]

class CodeEditor(Widget):
    def __init__(self, *args, caption=""):
        textedit = CodeEditorTextEdit(*args)
        textedit.setPlaceholderText("Code here...")

        super().__init__(caption, textedit)

        self.statements = ["var", "if", "else", "while", "for", "break", "continue", "function", "return", "repeat", "until", "do", "or", "and", "xor", "div", "mod", "switch", "case", "default", "with", "exit", "try", "catch", "finally"]
        self.constants = getfromfile("assets/data/constants.txt")
        self.functions = getfromfile("assets/data/functions.txt")

        self.highlighter = CodeEditorHighlighter(
            textedit.document(),
            {
                # Other variables
                "#B2B1FF": [r"\b[A-Za-z_][A-Za-z0-9_]*\b"],

                # Global variables
                "#FD7DFD": [(r"\bglobal\s*\.\s*([A-Za-z_][A-Za-z_0-9]*)", 1)],

                # Local variables
                "#FFF899": [(r"\bvar\s+([A-Za-z_][A-Za-z_0-9]*)", 1)],

                # Builtin variables
                "#58E55A": [],

                # Statements and functions
                "#FFB871": [r"\{", r"\}"] + self.statements + self.functions,

                # Numbers and constants
                "#FF8080": [r"(?<![A-Za-z_0-9])-?\d+(?:_\d+)*(?:\.\d+(?:_\d+)*)?(?![A-Za-z_0-9])"] + self.constants,

                # Strings
                "#FFFF00": [r"\"(?:\\.|[^\"\\])*\""],

                # Comments
                "#5B995B": [r"(//.*?$|/\*[\s\S]*?\*/|///.*?$)"]
            }
        )

        self.completer = CodeEditorCompleter(
            textedit,
            self.statements + self.constants + self.functions
        )
    
    def init(self, variables={}, functions={}, assets=[]):
        varnames = list(variables.keys())
        funcnames = list(functions.keys())

        script_assets = []
        other_assets = []

        for asset in assets:
            if asset[0] == "SCPT":
                script_assets.append(asset[2])
            else:
                other_assets.append(asset[2])

        self.highlighter.init({ "#58E55A": varnames, "#FFB871": funcnames + script_assets, "#FF8080": other_assets })
        self.completer.init(varnames + funcnames + script_assets + other_assets)

    @property
    def text(self):
        return self._widget.toPlainText()
    
    @text.setter
    def text(self, value):
        return self._widget.setPlainText(str(value))

class CodeEditorTextEdit(QPlainTextEdit):
    def __init__(self, *args):
        super().__init__(*args)

        font = QFont("JetBrains Mono, Consolas, Cascadia Code", 11)
        font.setFixedPitch(True)
        metrics = QFontMetricsF(font)

        self.setFont(font)
        self.setTabStopDistance(metrics.horizontalAdvance(" " * 4))

        palette = self.palette()
        palette.setColor(QPalette.Text, QColor("#C0C0C0"))
        palette.setColor(QPalette.Highlight, QColor("#264F78"))
        palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
        self.setPalette(palette)

        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.linearea = CodeEditorLineArea(self)

        self.blockCountChanged.connect(self.updateLineAreaWidth)
        self.updateRequest.connect(self.updateLineArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        self.updateLineAreaWidth(0)
        self.highlightCurrentLine()
    
    def keyPressEvent(self, event):
        editor = self.parentWidget()

        key = event.key()
        text = event.text()
        cursor = self.textCursor()

        if editor.completer.popup().isVisible():
            if key in (Qt.Key_Enter, Qt.Key_Return):
                index = editor.completer.popup().currentIndex()
                completion = index.data() if index.isValid() else editor.completer.currentCompletion()

                if completion:
                    editor.completer.insertCompletion(completion)
                editor.completer.popup().hide()
                return
        
        super().keyPressEvent(event)

        if text.isalnum() or text == "_":
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
            cursor.select(QTextCursor.WordUnderCursor)
            prefix = cursor.selectedText()

            editor.completer.setCompletionPrefix(prefix)

            if editor.completer.completionCount() > 0:
                rect = self.cursorRect()
                rect.setWidth(
                    editor.completer.popup().sizeHintForColumn(0) + editor.completer.popup().verticalScrollBar().sizeHint().width()
                )
                editor.completer.complete(rect)

                index = editor.completer.completionModel().index(0, 0)
                editor.completer.popup().setCurrentIndex(index)
            else:
                editor.completer.popup().hide()
            return

        if key != Qt.Key_Shift: editor.completer.popup().hide()
    
    def lineAreaWidth(self):
        digits = len(str(max(1, self.blockCount())))
        space = 10 + self.fontMetrics().horizontalAdvance("9") * digits

        return space
    
    def updateLineAreaWidth(self, _):
        self.setViewportMargins(
            self.lineAreaWidth(),
            0,
            0,
            0
        )
    
    def updateLineArea(self, rect, dy):
        if dy:
            self.linearea.scroll(0, dy)
        else:
            self.linearea.update(
                0,
                rect.y(),
                self.linearea.width(),
                rect.height()
            )
        
        if rect.contains(self.viewport().rect()):
            self.updateLineAreaWidth(0)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)

        rect = self.contentsRect()

        self.linearea.setGeometry(
            QRect(
                rect.left(),
                rect.top(),
                self.lineAreaWidth(),
                rect.height()
            )
        )
    
    def lineAreaPaintEvent(self, event):
        painter = QPainter(self.linearea)
        painter.setFont(self.font())

        painter.fillRect(
            event.rect(),
            QColor("#2D2D2D")
        )

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()

        top = int(
            self.blockBoundingGeometry(block)
            .translated(self.contentOffset())
            .top()
        )

        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)

                painter.setPen(QColor("#808080"))
                painter.drawText(
                    0,
                    top,
                    self.linearea.width() - 5,
                    self.fontMetrics().height(),
                    Qt.AlignRight,
                    number
                )

            block = block.next()

            top = bottom
            bottom = top + int(
                self.blockBoundingRect(block).height()
            )

            blockNumber += 1

    def highlightCurrentLine(self):
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            lineColor = QColor("#2a2a2a")

            selection.format.setBackground(lineColor)
            selection.format.setProperty(
                QTextFormat.FullWidthSelection,
                True
            )

            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()

            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)

class CodeEditorHighlighter(QSyntaxHighlighter):
    def __init__(self, document, keywords):
        super().__init__(document)

        self.enabled = True
        self.keywords = keywords
        self.keywords_initial = self.keywords.copy()

        self.keyword_formats = {}
        self.keyword_rules = {}
        self.keyword_groups = {}

        self.init()

    def init(self, kw={}):
        self.keywords = self.keywords_initial.copy()

        for key, value in kw.items():
            if key in self.keywords:
                value = list(set(self.keywords[key] + value))
            self.keywords[key] = value

        self.loadFormats()
        self.loadRules()
        self.loadGroups()
    
    def loadFormats(self):
        for color in self.keywords.keys():
            if color in self.keyword_formats: continue

            kformat = QTextCharFormat()
            kformat.setForeground(QColor(color))

            self.keyword_formats[color] = kformat
    
    def loadRules(self):
        for color, words in self.keywords.items():
            krules = self.keyword_rules[color] if color in self.keyword_rules else {}

            for word in words:
                strword = word if isinstance(word, str) else word[0]

                krule = QRegularExpression(rf"\b{strword}\b" if strword.isidentifier() else strword)
                krule.setPatternOptions(QRegularExpression.MultilineOption)
                
                krules[word] = krule

            self.keyword_rules[color] = krules
        
    def loadGroups(self):
        for color, words in self.keywords.items():
            kgroups = self.keyword_groups[color] if color in self.keyword_groups else {}

            for word in words:
                group = 0 if isinstance(word, str) else word[1]
                kgroups[word] = group

            self.keyword_groups[color] = kgroups
    
    def highlightBlock(self, text):
        if not self.enabled: return
        
        for color, words in self.keywords.items():
            kformat = self.keyword_formats[color]
            krules = self.keyword_rules[color]
            kgroups = self.keyword_groups[color]

            for word in words:
                pattern = krules[word]
                group = kgroups[word]

                iterator = pattern.globalMatch(text)
                
                while iterator.hasNext():
                    match = iterator.next()

                    self.setFormat(
                        match.capturedStart(group),
                        match.capturedLength(group),
                        kformat
                    )

class CodeEditorCompleter(QCompleter):
    def __init__(self, parent, words):
        super().__init__(parent)
        self.editor = parent

        self.stringModel = QStringListModel(words, self)
        self.setModel(self.stringModel)
    
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompletionMode(QCompleter.PopupCompletion)

        self.activated.connect(self.insertCompletion)

        self.setWidget(parent)
        self.popup().setStyleSheet("""
            QListView {
                font-family: Consolas, 'JetBrains Mono', monospace;
                font-size: 9pt;
                padding: 2px;
            }
            QListView::item {
                padding: 3px 5px;
            }
        """)

        self.words_initial = words.copy()

        self.init()

    def init(self, words=[]):
        words = list(set(self.words_initial + words))
        words.sort(key=lambda s : (len(s), s.lower()))

        self.stringModel.setStringList(words)
    
    def insertCompletion(self, completion):
        widget = self.widget()

        cursor = widget.textCursor()

        cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
        cursor.select(QTextCursor.WordUnderCursor)
        cursor.removeSelectedText()
        cursor.insertText(completion)
        
        widget.setTextCursor(cursor)
        widget.ensureCursorVisible()

class CodeEditorLineArea(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
    
    def sizeHint(self):
        return QSize(self.parentWidget().lineAreaWidth(), 0)
    
    def paintEvent(self, event):
        self.parentWidget().lineAreaPaintEvent(event)