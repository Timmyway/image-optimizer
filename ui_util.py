from pathlib import Path
from PyQt6.QtCore import pyqtSignal, QObject, QTimer
from PyQt6.QtWidgets import QMessageBox
import threading
import webbrowser
import os, json

class JsonConfig:
	@staticmethod
	def read(path):		
		try:
			with open(path + '.json', encoding='utf-8') as json_data:
				config = json.load(json_data)
				return config
		except FileNotFoundError:
			print(f'No such file or directory: {path}')
			return {}

class ImageHelper:
	@staticmethod
	def parseImages(folder, allowed_extensions=['WebP', 'png', 'jpeg', 'jpg', 'gif', 'ico', 'tiff' 'bmp'], relative=True):
		# keep only allowed images		
		images = []
		extensions = [ext.lower() for ext in allowed_extensions]
		for item in os.listdir(folder):			
			item_abs_path = os.path.join(folder, item)			
			if os.path.isfile(item_abs_path):
				print('=============> Folder: ', item_abs_path)		
				_, ext = os.path.splitext(os.path.basename(item))				
				if ('.' in ext) and (ext.lstrip('.').lower() in extensions):
					if relative:
						images.append(item)
					else:
						images.append(item_abs_path)
		print('Parse images: ', images)
		return images

def is_visible(visible, widget):
	''' Set widget visibility according to a variable state '''
	if visible:		
		widget.setVisible(True)
	else:		
		widget.setVisible(False)

class TimedMessageBox(QMessageBox):
	"""docstring for TimedMessageBox"""
	def __init__(self):
		super(TimedMessageBox, self).__init__()
		pass

	def countdown_close(self, timeout=3000):
		QTimer.singleShot(timeout, lambda: self.close())

def msg_box(msg_text="", msg_title="", msg_type=QMessageBox.Icon.Information, need_value=False, option_1=QMessageBox.StandardButton.Ok, 
		option_2=QMessageBox.StandardButton.Cancel, autoclose=False, timeout=3000, detailed_text=False):
		''' 
			Custom Message box popup => Bgcolor changed according to message type.
			4 levels: WARNING, CRITICAL, INFORMATION, QUESTION
			Possible settings: AUTOCLOSE - TIMEOUT
		'''		
		style_master = '''
		QMessageBox {{
			background-color: {msg_bgcolor};			
			font-family: verdana; font-size: {font_size}; color: {msg_color};
		}}
		QMessageBox QPushButton {{
			background-color: {btn_bgcolor}; 
			border-radius: {btn_border_radius}; padding: 4px; color: {btn_color};
			font-size: {font_size};

		}}
		QMessageBox QPushButton:hover {{
			background-color: {btn_bgcolor_onhover}; color: {btn_color_onhover};
		}}
		'''
		style = {
			'information': style_master.format(
				msg_bgcolor='#34cb47', msg_color='#468847', btn_bgcolor='#333333', btn_border_radius='8px',
				btn_color='#FDFDFD', btn_bgcolor_onhover='#123456', btn_color_onhover='#F3F3F3',
				font_size='17px'),

			'question': style_master.format(
				msg_bgcolor='#afeeee', msg_color='#4682b4', btn_bgcolor='#333333', btn_border_radius='8px', 
				btn_color='#FDFDFD', btn_bgcolor_onhover='#123456', btn_color_onhover='#F3F3F3',
				font_size='17px'),

			'warning': style_master.format(
				msg_bgcolor='#fafad2', msg_color='#2e473b', btn_bgcolor='#333333', btn_border_radius='8px', 
				btn_color='#FDFDFD', btn_bgcolor_onhover='#123456', btn_color_onhover='#F3F3F3',
				font_size='17px'),

			'critical': style_master.format(
				msg_bgcolor='#ebcece', msg_color='#b94a48', btn_bgcolor='#333333', btn_border_radius='8px', 
				btn_color='#FDFDFD', btn_bgcolor_onhover='#123456', btn_color_onhover='#F3F3F3',
				font_size='17px')
		}
		msg = TimedMessageBox()
		if detailed_text:
			msg.setDetailedText(msg_text)
		else:
			msg.setText(msg_text)
		msg.setWindowTitle(msg_title)
		print(msg_type)
		if need_value:
			msg.setStandardButtons(option_1 | option_2)
		if msg_type.value == 1:
			msg.setStyleSheet(style['information'])
			print('Information mode')
			msg.setIcon(QMessageBox.Icon.Information)		
		elif msg_type.value == 2:
			msg.setStyleSheet(style['warning'])
			msg.setIcon(QMessageBox.Icon.Warning)
			print('Warning mode')
		elif msg_type.value == 3:
			msg.setStyleSheet(style['critical'])
			msg.setIcon(QMessageBox.Icon.Critical)
			print('Critical mode')
		elif msg_type.value == 4:
			msg.setStyleSheet(style['question'])
			msg.setIcon(QMessageBox.Icon.Information)
			print('Question mode')

		msg.show()
		if autoclose:
			msg.countdown_close(timeout)
		retval = msg.exec()
		print(retval)
		return retval

def create_dirs(path, erase_if_exits=False):
	dir_path = Path(path)
	# Create path directory
	try:
		Path(dir_path).mkdir(parents=True, exist_ok=erase_if_exits)
		return 1
	except FileExistsError as e:
		print(e)
		return None

	except PermissionError as e:
		print(e)
		return None	

def open_folder(path=''):
	if path is None:
		return
	p = Path(path)
	# Open app directory if no path is provided
	if not path:
		current_dir = Path.cwd()
		webbrowser.open(current_dir)
	else:
		create_dirs(p)
		webbrowser.open(str(p))

def delay_action(action, callback, timeout=3000):		
	try:			
		threading.Thread(target=action).start()
	finally:
		QTimer.singleShot(timeout, lambda: callback())

class InsideThread(object):
	"""docstring for InsideThread"""
	def __init__(self, callback, button, label=None, 
			moovie=None, emit_object=False
		):
		super(InsideThread, self).__init__()
		self.button = button
		self.label = label
		self.loading_anim = moovie
		self.signal = CustomSignal()
		self.callback = callback
		self.emit_object = emit_object		
		self.signal.finished.connect(self.after)		
		self.button.clicked.connect(lambda: self.run())

	def before(self):
		if self.callback.get('start', None):
			self.callback.get('start')()
		self.button.setVisible(False)
		if self.label:
			self.label.setVisible(True)
		if self.loading_anim:
			self.loading_anim.start()

	def after(self):
		print('---------- After ----------')
		if self.callback.get('after', None):
			if not self.emit_object:
				self.callback.get('after')()
			else:
				self.callback.get('after')(self.emit_object)
		self.button.setVisible(True)
		if self.label:
			self.label.setVisible(False)
		if self.loading_anim:
			self.loading_anim.stop()
		print('Call end')

	def run(self):
		self.before()
		def inside_thread():			
			if not self.emit_object:
				self.callback.get('run')()
				self.signal.finished.emit()
				print('Signal should be emitted')
			else:
				self.callback['run']['func']()
				self.signal.object_transfered.emit(self.callback['run']['object_to_emit'])

		t = threading.Thread(target=inside_thread)
		t.start()

class CustomSignal(QObject):
	"""docstring for CustomSignal"""
	finished = pyqtSignal()	
	object_transfered = pyqtSignal(object)
	def __init__(self):
		super(CustomSignal, self).__init__()
		pass

signal_g_card_edit = CustomSignal()