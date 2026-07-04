import time
import threading

class Bridge():
    def __init__(self, name, handler):
        self.name = name
        self.handler = handler

        self.table = None
        self.env = None
        self.dataout = None
        self.datain = None

        self.event = None
        self.thread = None

        self.delay = 1 / 60

    def init(self, table=0):
        if self.event and self.thread:
            self.event.set()
            self.thread.join()

            self.event = None
            self.thread = None
        
        self.table = None
        self.env = None
        self.dataout = None
        self.datain = None
        
        if table:
            self.table = table

            self.event = threading.Event()
            self.thread = threading.Thread(target=self.worker, daemon=True)
            
            self.thread.start()

    def wait_for(self, callback, delay=3):
        start = time.perf_counter()

        while not callback():
            time.sleep(self.delay)

            if (time.perf_counter() - start) > delay:
                return False
        
        return True
    
    def worker(self):
        if not self.table or not self.event:
            return

        while not self.event.wait(self.delay):
            self.env = self.env if self.env else self.table.get_variable(self.name)

            if self.env:
                self.dataout = self.dataout if self.dataout else self.env.get_variable("out")
                self.datain = self.datain if self.datain else self.env.get_variable("in")
                if not self.dataout or not self.datain: continue

                name = self.dataout.get(0)

                if isinstance(name, str) and name != "":
                    try:
                        args = self.dataout.get(1).get_elements()
                        success, result = self.handler(name, args)
                    except Exception as error:
                        success, result = False, None

                    self.datain.set(1, result)
                    self.datain.set(0, success)