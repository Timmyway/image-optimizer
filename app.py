from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QGridLayout, QFileDialog, QMessageBox
from PyQt6.QtGui import QGuiApplication, QIcon, QShortcut, QKeySequence
from PyQt6.QtCore import QPoint, QDir, pyqtSignal
from PyQt6 import uic
# Built-in module :
import sys, os

from core.optimizer import ImageOptimizer
from core.kitbuilder import Kitbuilder
from ui_util import msg_box, open_folder, ImageHelper, JsonConfig

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
		self.last_folder = '/home'
		# The following config method helps us to set all default behaviours
		self.config()

	def config(self):
		# Configuration datas:
		self.user_config = JsonConfig.read(resourcePath('config'))
		print(self.user_config)
		# Set application title -----------------------------------------------
		self.setWindowTitle(self.title)
		# ---- Size and position of Mainwindow --------------------------------
		self.center_mainwindow(w=600, h=100)
		# Default values:
		self.sliderNotif()
		self.spinBoxBasewidth.setValue(self.user_config.get('resize_width', 0))
		# Kitbuilder
		Kitbuilder.url = self.user_config.get('kitbuilder_url', 'http://127.0.0.1:9000/')
		try:
			creds = {'username': self.user_config['kb_username'], 
				'password': self.user_config['kb_password']
			}
			self.kitbuilder = Kitbuilder(creds)
			if self.kitbuilder.status == 'off':
				self.btnKbUpload.setVisible(False)
		except KeyError:
			self.btnKbUpload.setVisible(False)		
		# Widget config
		# -- COMBOBOX -- #
		# -------------- #
		formats = self.user_config.get('formats', 
			['default', 'WebP', 'png', 'jpeg', 'gif', 'ico', 'tiff', 'bmp']
		)
		self.comboBoxFormat.addItems(formats)
		self.signalProgression['int'].connect(self.progressBar.setValue)
		# -- CHECkBOX -- #
		# Don't replace original file by default
		self.chkReplaceSource.setChecked(self.user_config.get('replace_source', False))		
		self.chkFileMode.setChecked(self.user_config.get('file_mode', False))
		self.listWidgetImages.setVisible(self.chkFileMode.isChecked())
		# ------------- #
		# Connect widget to actions
		self.btnBrowseImageFolder.clicked.connect(self.browse)
		self.btnOptimize.clicked.connect(lambda: self.optimize())
		self.hSliderQuality.valueChanged.connect(lambda: self.sliderNotif())
		self.btnBrowseFolder.clicked.connect(lambda: open_folder(self.formImageFolder.text()))
		self.chkReplaceSource.stateChanged.connect(self.setOverwriteMode)
		self.chkFileMode.stateChanged.connect(self.setBrowseMode)		
		self.btnKbUpload.clicked.connect(lambda: self.kbUploadImages())
		# Set shortcut
		self.shortcut_delete_from_list = QShortcut(QKeySequence('Del'), self.listWidgetImages)
		self.shortcut_delete_from_list.activated.connect(lambda: self.removeImages())
		# Set default values:
		self.hSliderQuality.setValue(self.user_config.get('compression_quality', 80))

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

	def browse(self):
		if self.chkFileMode.isChecked():
			self.chooseFiles()
		else:
			self.chooseFolder()

	def chooseFolder(self):
		''' Open a dialog to let user choose a folder on his computer '''
		folder = QFileDialog().getExistingDirectory(self,
			self.tr("Open images directory"), self.formImageFolder.text()
		)
		if folder:
			self.formImageFolder.setText(QDir.toNativeSeparators(folder))

	def chooseFiles(self):
		''' Open a dialog to let user choose multiple files on his computer '''		
		dialog = QFileDialog()
		dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
		images = dialog.getOpenFileNames(self, 
			"Select files", self.last_folder,
			"images (*.webp .png *.jpeg *.jpg *.gif *.ico *.bmp)"
		)
		try:
			self.last_folder = os.path.dirname(images[0][0])
			self.listWidgetImages.insertItems(0, images[0])
		except IndexError:
			pass

	def removeImages(self):
		selected_images = self.listWidgetImages.selectedItems()
		if not selected_images: return
		for image_item in selected_images:
			self.listWidgetImages.takeItem(self.listWidgetImages.row(image_item))

	def kbUploadImages(self):		
		# File mode
		images = []	
		if self.chkFileMode.isChecked():
			if self.listWidgetImages.count() > 0:
				for index in range(self.listWidgetImages.count()):
					images.append(self.listWidgetImages.item(index))
				images = [image.text() for image in images]
			else:
				msg_box(msg_text=f'File mode: "no images found"', msg_title='Optimize image', 
					autoclose=True, timeout=2000,
					msg_type=QMessageBox.Icon.Warning
				)
		# Folder mode
		else:
			images_path = self.formImageFolder.text()
			if not images_path:
				msg_box(msg_text=f'Folder mode: "no images found"', msg_title='Optimize image', 
					autoclose=True, timeout=2000,
					msg_type=QMessageBox.Icon.Warning
				)
			else:
				images = ImageHelper.parseImages(images_path, relative=False)
		for i,image in enumerate(images):
			image_url = self.kitbuilder.storeImage(image)
			content = f'''<a href="{image_url}" target="_blank">
	<span>{image_url}</span>
</a><br />
			'''
			self.save('last_uploaded.html', content=content)
			progress_value = ((i+1) * 100) // len(images)
			self.signalProgression.emit(progress_value)
		if self.chkFileMode.isChecked() and self.user_config.get('clear_after_upload', False):
			self.listWidgetImages.clear()		

	def save(self, filename='saveed.txt', mode='a', content=''):
		with open(resourcePath(filename), mode) as f:
			f.write(content)

	
	def optimize(self):
		''' Compress and resize images inside user defined folder '''
		images_path = self.formImageFolder.text()

		config = {'quality': self.hSliderQuality.value(),
			'base_width': self.spinBoxBasewidth.value(),
			'format': self.comboBoxFormat.currentText(),
			'overwrite': self.chkReplaceSource.isChecked()			
		}
		opt = ImageOptimizer(self, images_path, config)
		if self.chkFileMode.isChecked():
			print('List item count: ', type(self.listWidgetImages.count()))
			if self.listWidgetImages.count() > 0:
				images = []
				for index in range(self.listWidgetImages.count()):
					images.append(self.listWidgetImages.item(index))
				images = [image.text() for image in images]
				print('------------>', images)				
				opt.compress(config['overwrite'], images, True)
			else:
				msg_box(msg_text=f'File mode: "no images found"', msg_title='Optimize image', 
					autoclose=True, timeout=2000,
					msg_type=QMessageBox.Icon.Warning
				)
		else:
			if not images_path:
				msg_box(msg_text=f'Folder mode: "no images found"', msg_title='Optimize image', 
					autoclose=True, timeout=2000,
					msg_type=QMessageBox.Icon.Warning
				)
			else:
				opt.compress(config['overwrite'])

	def setOverwriteMode(self):
		if self.chkReplaceSource.isChecked():
			self.comboBoxFormat.setCurrentText('default')
			self.comboBoxFormat.setEnabled(False)
		else:			
			self.comboBoxFormat.setEnabled(True)

	def setBrowseMode(self):
		file_mode = self.chkFileMode.isChecked()		
		self.listWidgetImages.setEnabled(file_mode)
		self.listWidgetImages.setVisible(file_mode)
		self.formImageFolder.setEnabled(not file_mode)
		self.formImageFolder.setVisible(not file_mode)		
		
def main(): 
	app = QApplication(sys.argv)
	app.setWindowIcon(QIcon(resourcePath('fav.ico')))
	form = App()
	form.show()
	sys.exit(app.exec())


if __name__ == '__main__':
	main()