
# Frameworks
import sys
from GUI.YSViewController import Controller
from PyQt5.QtWidgets import QApplication


# 启动GUI
def start_GUI_Window():
    app = QApplication(sys.argv)
    controller = Controller()
    controller.show_welcome()
    sys.exit(app.exec_())































