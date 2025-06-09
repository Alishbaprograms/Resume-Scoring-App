import sys
from PyQt5.QtWidgets import QApplication
from gui import ResumeProcessorGUI

app = QApplication(sys.argv)
window = ResumeProcessorGUI()
window.show()
sys.exit(app.exec_())
