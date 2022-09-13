from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QGridLayout, QFileDialog, QMessageBox
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import QPoint, QDir
from PyQt6 import uic
# Built-in module :
import sys

from core.optimizer import ImageOptimizer
# from ui_util import msg_box

class App(QMainWindow):
	def __init__(self, parent=None, title='Image optimizer'):
		super(App, self).__init__(parent)
		uic.loadUi('look.ui', self)
		self.title = title
		# The following config method helps us to set all default behaviours
		self.config()

	def config(self):        
		# Set application title -----------------------------------------------
		self.setWindowTitle(self.title)
		# ---- Size and position of Mainwindow --------------------------------
		self.center_mainwindow(w=600, h=100)
		# Default values:
		self.sliderNotif()
		self.spinBoxBasewidth.setValue(1280)
		# Connect widget to actions
		self.btnBrowseImageFolder.clicked.connect(self.chooseFolder)
		self.btnOptimize.clicked.connect(lambda: self.optimize())
		self.hSliderQuality.valueChanged.connect(lambda: self.sliderNotif())

	def center_mainwindow(self, w=600, h=300):
		self.resize(w,h)
		size_window = self.geometry()
		# cp is the Center Point of user screen. Ex: if 600x300 so cp = 300,150
		cp = QGuiApplication.primaryScreen().availableGeometry().center()
		# x = center point - width's half | x = center point - height's half
		position = QPoint(cp.x() - w // 2, cp.y() - h // 2)
		self.move(position)

	def sliderNotif(self):
		self.labelSliderQualityValue.setText(f'{self.hSliderQuality.value()}')

	def chooseFolder(self):        
		folder = QFileDialog().getExistingDirectory(self,
		self.tr("Open images directory"), "images")
		if folder:
			self.formImageFolder.setText(QDir.toNativeSeparators(folder))    

	def optimize(self):
		images_path = self.formImageFolder.text()
		if (not images_path):
			# msg_box(msg_text=f'No images found', msg_title='Optimize image', 
			# 	autoclose=True, timeout=3000,
			# 	msg_type=QMessageBox.Icon.Warning
			# )
			return
		print(images_path)
		config = {'quality': self.hSliderQuality.value(),
			'base_width': self.spinBoxBasewidth.value()
		}
		opt = ImageOptimizer(images_path, config)
		opt.compress()
		# msg_box(msg_text=f'Finished', msg_title='Optimize image', 
		# 	autoclose=True, timeout=3000
		# )
		
def main(): 
	app = QApplication(sys.argv)
	form = App()
	form.show()
	sys.exit(app.exec())


if __name__ == '__main__':
	main()