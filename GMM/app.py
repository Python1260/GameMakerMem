import os
import sys

from src.memory import Memory
from src.ui import MainWindow, QApplication
from src.settings.types import *

LOCALAPPDATA = os.getenv("LOCALAPPDATA")

class App():
    def __init__(self):
        self.name = "GameMakerMem"
        self.version = "2.0.0"
        self.icon = "assets/images/icon.png"
        self.size = (500, 700)

        self.path = os.path.join(LOCALAPPDATA, self.name)
        os.makedirs(self.path, exist_ok=True)
        
        self.memory = None
        self.mainwindow = None

        self.instances = []
        self.current_instance = None
    
    def run(self):
        runner = QApplication(sys.argv)

        self.memory = Memory(self)
        self.mainwindow = MainWindow(self)

        self.init_memory()
        self.init_ui()

        self.mainwindow.show()

        return runner.exec()
    
    def on_attach(self):
        text = self.ui_attach_input.text.strip()
        if text == "": return

        try: text = int(text)
        except: pass

        shouldinit = self.memory.attach(text)

        if shouldinit: self.reset()

        if self.memory.attached():
            self.ui_attach_status.text = "attaching..."
            QApplication.processEvents()

            if shouldinit: self.init_attach()

            if self.memory:
                self.ui_attach_status.text = "attached!"
            else:
                self.ui_attach_status.text = "unsupported!"
        else:
            self.ui_attach_status.text = "failed to attach!"

            if shouldinit: self.ui_execute_input.init()
    
    def init_memory(self):
        def callback():
            self.reset()
            self.init_room()
            self.ui_attach_status.text = "detached!"

        self.memory.on_detached(callback)
    
    def init_ui(self):
        self.ui_attach_input = self.mainwindow.attach_input
        self.ui_attach_status = self.mainwindow.attach_status
        self.ui_attach_button = self.mainwindow.attach_button

        self.ui_room_name = self.mainwindow.room_name
        self.ui_room_width = self.mainwindow.room_width
        self.ui_room_height = self.mainwindow.room_height
        self.ui_room_persistent = self.mainwindow.room_persistent
        self.ui_room_instancecount = self.mainwindow.room_instancecount
        self.ui_room_speed = self.mainwindow.room_speed
        self.ui_roomgoto_input = self.mainwindow.roomgoto_input
        self.ui_roomgoto_button = self.mainwindow.roomgoto_button
        self.ui_room_refresh = self.mainwindow.room_refresh

        self.ui_instance_list = self.mainwindow.instance_list
        self.ui_instance_refresh = self.mainwindow.instance_refresh
        self.ui_instance_destroy = self.mainwindow.instance_destroy
        self.ui_variable_dict = self.mainwindow.variable_dict
        self.ui_variable_refresh = self.mainwindow.variable_refresh

        self.ui_execute_input = self.mainwindow.execute_input
        self.ui_execute_filechoose = self.mainwindow.execute_filechoose
        self.ui_execute_button = self.mainwindow.execute_button
        self.ui_execute_status = self.mainwindow.execute_status

        self.ui_attach_input.returnPressed.connect(self.on_attach)
        self.ui_attach_button.clicked.connect(self.on_attach)

        self.ui_roomgoto_input.returnPressed.connect(self.goto_room)
        self.ui_roomgoto_button.clicked.connect(self.goto_room)
        self.ui_room_refresh.clicked.connect(self.init_room)

        self.ui_instance_list.itemClicked.connect(self.on_instanceselect)
        self.ui_instance_refresh.clicked.connect(self.init_instances)
        self.ui_instance_destroy.clicked.connect(self.destroy_instance)
        self.ui_variable_refresh.clicked.connect(self.init_variables)

        self.ui_execute_filechoose.clicked.connect(self.execute_filechoose)
        self.ui_execute_button.clicked.connect(self.execute_code)
    
    def init_attach(self):
        if not self.memory: return

        self.memory.context.init()
        strings, variables, functions, instance_variables, assets, declaredfunctions, globaltable = self.memory.context.get_gamecontext()

        self.memory.executor.init(strings, variables, functions, instance_variables, assets, declaredfunctions, globaltable)
        self.ui_execute_input.init(variables, functions, assets)

        self.init_room()
    
    def init_room(self):
        if not self.memory: return

        room = self.memory.context.get_room()
        roomref = self.memory.context.get_roomref()

        self.ui_room_name.text = f"{self.memory.context.get_assetname(*roomref)} (id {roomref[1]})"
        self.ui_room_width.text = room.width
        self.ui_room_height.text = room.height
        self.ui_room_persistent.text = room.persistent
        self.ui_room_speed.text = self.memory.context.get_fps()

        self.init_instances()
    
    def init_instances(self):
        if not self.memory: return

        room = self.memory.context.get_room()
        instances = room.get_instances()

        self.instances = instances
        self.ui_room_instancecount.text = len(self.instances)

        if self.current_instance and not self.current_instance in self.instances:
            self.current_instance = None

        self.ui_instance_list.clear()
        self.ui_attach_input.deselect()

        prev_inst = self.instances

        globalinstance = self.memory.context.get_globaltable()
        globaltext = "Instance GLOBAL"

        if globalinstance:
            self.ui_instance_list.add(globaltext, globalinstance)

        for instance in self.instances:
            deactive = instance.get_deactive()
            text = f"Instance {instance.id} ({self.memory.context.get_assetname(*instance.object_index)}) {"(deactive)" if deactive else ""}"

            self.ui_instance_list.add(text, instance, disabled=deactive)

            QApplication.processEvents()
            if self.instances != prev_inst or self.mainwindow.closed: break
        
        if globalinstance:
            self.instances.append(globalinstance)
        
        self.init_variables()

    def init_variables(self):
        if not self.memory: return
        if not self.current_instance or not self.current_instance in self.instances:
            self.current_instance = None
            self.ui_variable_dict.clear()
            return

        self.ui_variable_dict.clear()
        self.ui_attach_input.deselect()

        variables = self.current_instance.get_variables()

        prev_inst = self.current_instance

        for variable in variables:
            value = self.current_instance.get_variable(variable)
            callback = lambda value, variable=variable : self.current_instance.set_variable(variable, value)

            if isinstance(value, str):
                value = f"\"{value}\""
            elif isinstance(value, float):
                value = f"{value:.2f}"
            elif isinstance(value, tuple):
                for instance in self.instances:
                    if instance.id == value[1]:
                        def select():
                            for i in range(self.ui_instance_list.count()):
                                item = self.ui_instance_list.item(i)

                                if item.get() == instance:
                                    self.ui_instance_list.setCurrentItem(item)
                                    self.ui_instance_list.scrollToItem(item)
                                    break

                            self.current_instance = instance
                            self.init_variables()
                        
                        callback = select
                        break
                else:
                    callback = lambda *_ : True
                        
                value = f"ref {self.memory.context.get_refname(value[0])} {self.memory.context.get_assetname(*value)}"
            else:
                value = str(value)

            editable = (getattr(self.current_instance.__class__, variable).fset is not None) if hasattr(self.current_instance, variable) else True

            parsed = self.mainwindow.parse_widget(value, callback, editable)

            self.ui_variable_dict.add(variable, value, parsed)

            QApplication.processEvents()
            if self.current_instance != prev_inst or self.mainwindow.closed: break
    
    def on_instanceselect(self, item):
        instance = item.get()

        self.current_instance = instance

        self.init_variables()
    
    def goto_room(self):
        if not self.memory or not self.memory.attached(): return

        text = self.ui_roomgoto_input.text.strip()
        if not text: return

        try: text = int(text)
        except: return

        self.memory.context.room_goto(text)
    
    def destroy_instance(self):
        if not self.memory or not self.memory.attached(): return
        if not self.current_instance or not self.current_instance in self.instances:
            self.current_instance = None
            return
        
        if self.current_instance.id < 100000: return
        
        self.memory.context.instance_destroy(self.current_instance)
        self.current_instance = None

        self.init_instances()
    
    def execute_code(self):
        if not self.memory or not self.memory.attached(): return

        text = self.ui_execute_input.text
        if not text: return

        self.ui_execute_status.text = "* Injecting GML..."
        QApplication.processEvents()

        status, result = self.memory.executor.inject(text)

        if status == 0:
            self.ui_execute_status.text = "* GML executed successfully!"
        elif status == 1:
            self.ui_execute_status.text = "* Failed to compile GML!"
        elif status == 2:
            self.ui_execute_status.text = "* Failed to execute GML!"
        elif status == 3:
            self.ui_execute_status.text = "* Failed to inject init!"
        else:
            self.ui_execute_status.text = "* Execution failed!"
    
    def execute_filechoose(self):
        path = self.mainwindow.open_filechoose(
            "Open file",
            ("GML Files", "*.gml"),
            ("Text Files", "*.txt"),
            ("All Files", "*")
        )

        if path:
            with open(path, encoding="utf-8", errors="ignore") as file:
                self.ui_execute_input.text = file.read()

    def reset(self):
        self.memory.executor.init([], {}, {}, {}, [], 0, 0)
        self.ui_execute_input.init()
        
        self.ui_execute_status.text = "..."

        self.instances = []
        self.current_instance = None

        self.ui_instance_list.clear()
        self.ui_variable_dict.clear()