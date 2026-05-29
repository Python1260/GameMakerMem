import os
import sys
import ctypes

frozen = getattr(sys, "frozen", False)
environment = os.path.dirname(os.path.abspath(__file__))
os.chdir(environment)

appid = "flyingdum.gmm.appid"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

if not frozen:
    os.system("pip install -r requirements.txt")

from app import App

if __name__ == "__main__":
    app = App()
    app.run()