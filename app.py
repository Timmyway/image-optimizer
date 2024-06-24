from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QColorDialog
from PyQt6.QtGui import QGuiApplication, QIcon, QShortcut, QKeySequence, QDesktopServices
from PyQt6.QtCore import QPoint, QDir, pyqtSignal, QUrl
from PyQt6 import uic
# Built-in module :
import sys, os

from core.optimizer import ImageOptimizer
from ui_util import msg_box, open_folder, ImageHelper, JsonConfig

basedir = os.path.dirname(__file__)

def resourcePath(relativePath):
	""" Get absolute path to resource, works for dev and for PyInstaller """
	try:
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		basePath = sys._MEIPASS
	except Exception:
		basePath = os.path.abspath(".")	
	return os.path.join(basePath, relativePath)

def workingDirPath(filename):
	return os.path.join(os.getcwd(), filename)


class App(QMainWindow):
	signalProgression = pyqtSignal(int, name='update')

	def __init__(self, parent=None, title='Image optimizer'):
		super(App, self).__init__(parent)
		uic.loadUi(resourcePath('look.ui'), self)
		self.title = title
		print(resourcePath('look.ui'))
		self.basepath = resourcePath('')
		self.last_folder = '/home'
		# The following config method helps us to set all default behaviours
		self.config()

	def config(self):
		# Load user configuration:
		self.user_config = JsonConfig.read('config')

		# Configure widgets and connections		
		self.setWindowTitle(self.title)		
		self.center_mainwindow(w=600, h=100)		
		self.updateQualitySliderLabel()
		self.setupComboBoxFormats()
		self.setupCheckBoxes()
		self.setupWidgetConnections()
		
		self.signalProgression['int'].connect(self.progressBar.setValue)

		# Set shortcut
		self.shortcut_delete_from_list = QShortcut(QKeySequence('Del'), self.listWidgetImages)
		self.shortcut_delete_from_list.activated.connect(lambda: self.removeImages())

		# Set default values:
		self.spinBoxBasewidth.setValue(self.user_config.get('resize_width', 0))
		self.hSliderQuality.setValue(self.user_config.get('compression_quality', 80))

	def setupWidgetConnections(self):
		# Connect buttons to actions
		self.btnBrowseImageFolder.clicked.connect(self.browse)
		self.btnOptimize.clicked.connect(lambda: self.optimize('compress'))
		self.btnBrowseFolder.clicked.connect(lambda: open_folder(self.formImageFolder.text()))		
		self.btnMakeGif.clicked.connect(lambda: self.optimize('build_gif'))
		self.btnMakeGifBgColor.clicked.connect(self.pickBgColor)

		# Sliders
		self.hSliderQuality.valueChanged.connect(self.updateQualitySliderLabel)

		# Checkboxes
		self.chkReplaceSource.stateChanged.connect(self.setOverwriteMode)
		self.chkFileMode.stateChanged.connect(self.setBrowseMode)

	def setupComboBoxFormats(self):
		# Set up formats in combobox from config
		formats = self.user_config.get('formats', ['default', 'WebP', 'png', 'jpeg', 'gif', 'ico', 'tiff', 'bmp'])
		self.comboBoxFormat.addItems(formats)

	def setupCheckBoxes(self):
		# Set initial checkbox states based on config
		self.chkReplaceSource.setChecked(self.user_config.get('replace_source', False))
		self.chkFileMode.setChecked(self.user_config.get('file_mode', False))
		self.listWidgetImages.setVisible(self.chkFileMode.isChecked())
		self.formImageFolder.setVisible(not self.chkFileMode.isChecked())	
		self.chkOpenWhenFinished.setChecked(self.user_config.get('open_when_finished', False))

	def center_mainwindow(self, w=600, h=300):
		self.resize(w,h)
		size_window = self.geometry()
		# cp is the Center Point of user screen. Ex: if 600x300 so cp = 300,150
		cp = QGuiApplication.primaryScreen().availableGeometry().center()
		# x = center point - width's half | x = center point - height's half
		position = QPoint(cp.x() - w // 2, cp.y() - h // 2)
		self.move(position)

	def updateQualitySliderLabel(self):
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
			"images (*.webp *.png *.jpeg *.jpg *.gif *.ico *.bmp)"
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
		self.signalProgression.emit(0)
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
		if self.chkFileMode.isChecked() and self.user_config.get('clear_after_upload', False):
			self.listWidgetImages.clear()

	def save(self, filename, mode='a', content=''):
		with open(workingDirPath(filename), mode, encoding='utf-8') as f:
			f.write(content)

	def pickBgColor(self) -> None:
		"""
        Opens a color dialog to select a background color for the GIF.
        """
		color = QColorDialog.getColor()
		if color.isValid():
			self.spinBoxMakeGifBgRed.setValue(color.red())
			self.spinBoxMakeGifBgGreen.setValue(color.green())
			self.spinBoxMakeGifBgBlue.setValue(color.blue())

	def getGifBgColor(self) -> tuple:
		"""
		Retrieves the background color RGB components from UI elements.

		Returns:
			tuple: A tuple containing RGB components (red, green, blue).
		"""
		red = self.spinBoxMakeGifBgRed.value()
		green = self.spinBoxMakeGifBgGreen.value()
		blue = self.spinBoxMakeGifBgBlue.value()

		# Ensure RGB values are within valid range (0-255)
		red = max(0, min(255, red))
		green = max(0, min(255, green))
		blue = max(0, min(255, blue))

		return red, green, blue
	
	def collectImages(self):
		images = []
		# Iterate over the items in the list widget to gather image file names
		for index in range(self.listWidgetImages.count()):
			images.append(self.listWidgetImages.item(index))
		# Extract text from list widget items to get file paths
		images = [image.text() for image in images]
		return images
	
	def openFolder(self, path: str) -> None:
		"""
        Opens the folder containing the specified path. If the path is a file,
        it opens the parent folder.

        Args:
            path (str): The path to the file or folder.
        """
		# Check if the path is a file
		if os.path.isfile(path):
			# If it's a file, get the parent directory
			folder_path = os.path.dirname(path)
		else:
			# If it's a directory, use the path as is
			folder_path = path

		# Open the folder
		QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
	
	def optimize(self, optimization_type: str = 'compress'):
		''' Compress and resize images inside user defined folder '''
		# Get the path of the images folder from the form
		images_path = self.formImageFolder.text()

		# Configuration dictionary for the optimizer	
		config = {'quality': self.hSliderQuality.value(),
			'base_width': self.spinBoxBasewidth.value(),
			'format': self.comboBoxFormat.currentText(),
			'overwrite': self.chkReplaceSource.isChecked()
		}

		# Initialize the image optimizer with the specified configuration
		opt = ImageOptimizer(self, images_path, config)

		# Emit a signal to set the progression bar to 0
		self.signalProgression.emit(0)

		# Check if file mode is selected
		if self.chkFileMode.isChecked():
			# If the widget list has images
			if self.listWidgetImages.count() > 0:
				images = self.collectImages()

				if optimization_type == 'compress':
					# Compress the images with overwrite option
					opt.compress(config['overwrite'], images, filemode=True)
				elif optimization_type == 'build_gif':
					# Build the GIF from the images
					dest_path = opt.buildGif(
				  		images,
						filemode=True,
						duration=self.spinBoxMakeGifDuration.value(),
						loop=self.spinBoxMakeGifRepeat.value(),
						bgColor=self.getGifBgColor()
					)

					if dest_path and self.chkOpenWhenFinished.isChecked():
						self.openFolder(dest_path)
				else:
					print('===================>', optimization_type)
					# Show an error message if the optimization type is not recognized
					msg_box(msg_text=f'Unknown optimization type: {optimization_type}', msg_title='Optimize image', 
							autoclose=True, timeout=2000, msg_type=QMessageBox.Icon.Warning)
			else:
				# Show a warning message box if no images are found in file mode
				msg_box(msg_text=f'File mode: "no images found"', msg_title='Optimize image', 
					autoclose=True, timeout=2000,
					msg_type=QMessageBox.Icon.Warning
				)
		else:
			# Folder mode is selected
			if not images_path:
				# Show a warning message box if no images path is provided in folder mode
				msg_box(msg_text=f'Folder mode: "no images found"', msg_title='Optimize image', 
					autoclose=True, timeout=2000,
					msg_type=QMessageBox.Icon.Warning
				)
			else:
				if optimization_type == 'compress':
					# Compress images in the specified folder with overwrite option
					opt.compress(config['overwrite'])
				elif optimization_type == 'build_gif':
					# Show an error message as building GIF from a folder is not supported
					msg_box(msg_text='Building GIF from a folder is not supported. Please select files in file mode.', 
							msg_title='Optimize image', autoclose=True, timeout=2000, msg_type=QMessageBox.Icon.Warning)
				else:
					# Show an error message if the optimization type is not recognized
					msg_box(msg_text=f'Unknown optimization type: {optimization_type}', msg_title='Optimize image', 
							autoclose=True, timeout=2000, msg_type=QMessageBox.Icon.Warning)

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