from .style import (
    Qt,
    QWidget,
    QApplication,
    QFileDialog,
    QIcon,

    HBox,
    VBox,
    Label,
    Button,
    Input,
    List,
    Dict,

    TabBox
)
from .codeeditor import CodeEditor

class MainWindow(VBox):
    def __init__(self, app):
        super().__init__()

        self.app = app
        self.subwidgets = {}

        self.setWindowTitle(f"{self.app.name} v{self.app.version}")
        self.setWindowIcon(QIcon(self.app.icon))
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.resize(*self.app.size)

        self._layout.setContentsMargins(11, 11, 11, 11)

        self.closed = False

        self.add(
            VBox(
                Input("", caption="GameMaker process name or PID:").put(self.subwidgets, "attach_input"),
                Label("waiting...", caption="Status:").put(self.subwidgets, "attach_status"),
                Button("Attach").put(self.subwidgets, "attach_button")
            ),
            TabBox(
                ("Room", VBox(
                    HBox(
                        Label("... (id 0)", caption="Room:").put(self.subwidgets, "room_name"),
                        Label("0", caption="Width:").put(self.subwidgets, "room_width"),
                        Label("0", caption="Height:").put(self.subwidgets, "room_height"),
                        Label("False", caption="Persistent:").put(self.subwidgets, "room_persistent"),
                    ),
                    HBox(
                        Label("0", caption="Instance count:").put(self.subwidgets, "room_instancecount"),
                        Label("0", caption="Fps:").put(self.subwidgets, "room_speed")
                    ),
                    HBox(
                        Input("0", caption="Goto room id: ").put(self.subwidgets, "roomgoto_input"),
                        Button("Go").put(self.subwidgets, "roomgoto_button")
                    ),
                    Button("Refresh room data").put(self.subwidgets, "room_refresh")
                )),
                ("Instances", HBox(
                    VBox(
                        Label("Instances:"),
                        List().put(self.subwidgets, "instance_list"),
                        HBox(
                            Button("Refresh").put(self.subwidgets, "instance_refresh"),
                            Button("Destroy").put(self.subwidgets, "instance_destroy")
                        )
                    ),
                    VBox(
                        Label("Variables:"),
                        Dict(["Variable name", "Variable value"]).put(self.subwidgets, "variable_dict"),
                        Button("Refresh").put(self.subwidgets, "variable_refresh")
                    ),
                )),
                ("Executor", VBox(
                    CodeEditor().put(self.subwidgets, "execute_input"),
                    Button("Load from file").put(self.subwidgets, "execute_filechoose"),
                    Button("Execute").put(self.subwidgets, "execute_button"),
                    Label("...").put(self.subwidgets, "execute_status")
                ))
            )
        )
    
    def __getattr__(self, name):
        return self.subwidgets[name]

    def closeEvent(self, event):
        self.closed = True
        QApplication.quit()

        return super().closeEvent(event)
    
    def parse_widget(self, value, callback, editable=True):
        def parse(value):
            value = value.strip()

            if value == "": return None

            if value.lower() == "true":
                return True
            elif value.lower() == "false":
                return False
            elif value.lower() == "noone":
                return -4
            elif value.lower() == "undefined":
                return None

            if value.startswith("\"") and value.endswith("\""):
                return value[1:-1]
            
            try:
                return float(value)
            except:
                return None

        if editable:
            parsed = parse(value)

            if isinstance(parsed, (bool, float, int, str)):
                def edit(text):
                    if text == "": return

                    value = parse(text)

                    if value != None:
                        return callback(value)

                widget = Input(value)
                widget.setCursorPosition(0)
                widget.textChanged.connect(edit)
                widget.returnPressed.connect(lambda : edit(widget.text))
            elif value.startswith("ref "):
                widget = Button(f"ref {str(value).split(" ")[-1]}")
                widget.clicked.connect(callback)
            else:
                widget = Input(str(value))
                widget.setCursorPosition(0)
                widget.setReadOnly(True)
        else:
            widget = Input(str(value))
            widget.setCursorPosition(0)
            widget.setReadOnly(True)

        return widget
    
    def open_filechoose(self, title, *filters):
        filterstr = ";;".join(f"{f[0]} ({f[1]})" for f in filters)

        return QFileDialog.getOpenFileName(
            self,
            title,
            "",
            filterstr
        )[0]