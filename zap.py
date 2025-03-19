from PySide6.QtWidgets import QApplication
from main import MainWindow

app = QApplication([])
window = MainWindow()
window.show()
app.exec()