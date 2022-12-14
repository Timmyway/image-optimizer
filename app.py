from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QGridLayout, QFileDialog, QMessageBox
from PyQt6.QtGui import QGuiApplication, QIcon
from PyQt6.QtCore import QPoint, QDir, pyqtSignal
from PyQt6 import uic
# Built-in module :
import sys, os

from core.optimizer import ImageOptimizer
from ui_util import msg_box, open_folder

basedir = os.path.dirname(__file__)

def resourcePath(relativePath):
	""" Get absolute path to resource, works for dev and for PyInstaller """
	try:
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		basePath = sys._MEIPASS
	except Exception:
		basePath = os.path.abspath(".")

	print('=====>', os.path.join(basePath, relativePath))	
	return os.path.join(basePath, relativePath)

class App(QMainWindow):
	signalProgression = pyqtSignal(int, name='update')

	def __init__(self, parent=None, title='Image optimizer'):
		super(App, self).__init__(parent)
		uic.loadUi(resourcePath('look.ui'), self)
		self.title = title
		self.basepath = resourcePath('')
		# The following config method helps us to set all default behaviours
		self.config()

	def config(self):        
		# Set application title -----------------------------------------------
		self.setWindowTitle(self.title)
		# ---- Size and position of Mainwindow --------------------------------
		self.center_mainwindow(w=600, h=100)
		# Default values:
		self.sliderNotif()
		self.spinBoxBasewidth.setValue(0)
		# Widget config
		# -- COMBOBOX -- #
		# -------------- #
		formats = ['default', 'WebP', 'png', 'jpeg', 'gif', 'ico', 'tiff' 'bmp']
		self.comboBoxFormat.addItems(formats)
		self.signalProgression['int'].connect(self.progressBar.setValue)
		# -- CHECkBOX -- #
		# Don't replace original file by default
		self.chkReplaceSource.setChecked(False)
		# ------------- #
		# Connect widget to actions
		self.btnBrowseImageFolder.clicked.connect(self.chooseFolder)
		self.btnOptimize.clicked.connect(lambda: self.optimize())
		self.hSliderQuality.valueChanged.connect(lambda: self.sliderNotif())
		self.btnBrowseFolder.clicked.connect(lambda: open_folder(self.formImageFolder.text()))
		self.chkReplaceSource.stateChanged.connect(self.setOverwriteMode)

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
		''' Open a dialog to let user choose a folder on his computer '''
		folder = QFileDialog().getExistingDirectory(self,
			self.tr("Open images directory"), self.formImageFolder.text()
		)
		if folder:
			self.formImageFolder.setText(QDir.toNativeSeparators(folder))

	def optimize(self):
		''' Compress and resize images inside user defined folder '''
		images_path = self.formImageFolder.text()
		if (not images_path):
			msg_box(msg_text=f'No images found', msg_title='Optimize image', 
				autoclose=True, timeout=2000,
				msg_type=QMessageBox.Icon.Warning
			)
			return
		print(images_path)
		config = {'quality': self.hSliderQuality.value(),
			'base_width': self.spinBoxBasewidth.value(),
			'format': self.comboBoxFormat.currentText(),
			'overwrite': self.chkReplaceSource.isChecked()
		}
		opt = ImageOptimizer(self, images_path, config)		
		opt.compress(config['overwrite'])
		# msg_box(msg_text=f'Finished', msg_title='Optimize image', 
		# 	autoclose=True, timeout=3000
		# )

	def setOverwriteMode(self):
		if self.chkReplaceSource.isChecked():
			self.comboBoxFormat.setCurrentText('default')
			self.comboBoxFormat.setEnabled(False)
		else:			
			self.comboBoxFormat.setEnabled(True)
		
def main(): 
	app = QApplication(sys.argv)
	app.setWindowIcon(QIcon(resourcePath('fav.ico')))
	form = App()
	form.show()
	sys.exit(app.exec())


if __name__ == '__main__':
	main()