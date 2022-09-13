from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QSize, pyqtSignal, QTimer, QRect, QPropertyAnimation, QSequentialAnimationGroup
from PyQt5.QtGui import QIcon, QFont, QCursor
from PyQt5.QtWidgets import QListWidget, QLineEdit, QVBoxLayout,\
QPushButton, QListWidgetItem, QLabel, QPushButton, QHBoxLayout, QWidget, QSizePolicy, QDialog,\
QTextEdit, QMessageBox, QSystemTrayIcon, QFrame, QGridLayout, QDesktopWidget
from functools import partial
import threading
import time
import sys
import sip

class CustomTag(QWidget):
	"""docstring for CustomLabel"""
	def __init__(self, parent, text, button_width=10, button_height=10):
		super(CustomTag, self).__init__()
		self.parent = parent
		self.label = QLabel(self)
		self.remove_button = QPushButton(self)
		self.label.setText(text)
		# Style:
		self.label_style = '''background-color: transparent; color: #ffffff; font-family: verdana; font-size: 11px;'''
		self.remove_button_style = '''background-color: transparent; width: 25px; height: 25px; border: 0px solid black'''
		# Remove button width and height
		self.button_width = button_width
		self.button_height = button_height
		# Layout definition:
		self.hBox = QHBoxLayout(self)        
		self.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
		self.widget_config()
		self.remove_button.clicked.connect(lambda: self.deleteLayout(self.hBox))	

	def widget_config(self):
		self.setGeometry(0, 0, 300, 100)    
		# self.setAlignment(QtCore.Qt.AlignLeft)
		self.setGeometry(100, 50, 100, 50)
		self.setLayout(self.hBox)
		self.parent.addWidget(self)
		# LABEL AND BUTTON CONFIGURATION :
		self.label.setStyleSheet(self.label_style)        
		self.remove_button.setStyleSheet(self.remove_button_style)
		self.remove_button.setIcon(QIcon('static/button/cross5.png'))
		self.remove_button.setIconSize(QSize(self.button_width, self.button_height))
		self.remove_button.setCursor(QtCore.Qt.PointingHandCursor)
		# SET SIZE POLICY
		self.size_policy.setHorizontalStretch(0)
		self.size_policy.setVerticalStretch(0)
		self.label.setSizePolicy(self.size_policy)
		self.remove_button.setSizePolicy(self.size_policy)
		# Box configuration :
		self.hBox.addWidget(self.label)
		self.hBox.addWidget(self.remove_button)
		self.hBox.setSpacing(0)
		self.hBox.addStretch(1)       

	def text(self):
		return self.label.text()

	def _set_label_style(self, new_style):
		self.label.setStyleSheet(new_style)

	def _set_remove_button_style(self, new_style):
		self.remove_button_style = new_style

	def deleteLayout(self, layout):
		self.deleteLater()

class ResultDialog(QDialog):
	"""docstring for ResultDialog"""
	def __init__(self, parent, external={}):
		super(ResultDialog, self).__init__()
		self.external = external
		self.__code = {}
		self.__code['original'] = ''
		self.__code['processed'] = ''
		self.__code['plaintext'] = ''       
		self.dic_widget = {
			'processed': {'label': ClickableLabel('Processed'), 'txt': QTextEdit(), 'btn_copy': QPushButton('Copy'), 'btn_edit': QPushButton('Edit')},
			'plaintext': {'label': ClickableLabel('Plaintext ▲▼'), 'txt': QTextEdit(), 'btn_copy': QPushButton('Copy'), 'btn_edit': QPushButton('Edit')},			
			'original': {'label': ClickableLabel('Original ▲▼'), 'txt': QTextEdit(), 'btn_copy': QPushButton('Copy'), 'btn_edit': QPushButton('Edit')}
		}
		self.formSubject = QLineEdit()
		self.formInfo = QLineEdit()
		self.size_policy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
		self.vCodeLayout = QVBoxLayout()		
		self.setWindowTitle("Result HTML")

	def init(self):
		self.setWindowModality(QtCore.Qt.NonModal)
		self.setGeometry(300, 50, 100, 50)
		self.resize(600, 600)
		label_style = 'background: #546e7a; font-family: Roboto; font-size: 16px; color: #eeeeee;'
		txt_style = '''background: #546e7a; color: #eeeeee;
			border-radius: 6px; border: 1px solid #29434e; padding: 10px;
			'''
		btn_style = '''background: {colors};
			border-width: 2px; border-radius: 6px;
			padding-left: 5px;
			padding-right: 5px;
			padding-top: 6px;
			padding-bottom: 6px;			
			width: 70px;
			font-family: Roboto;
			font-weight: 700;
			font-size: 13px;'''
		form_style = '''border-width: 2px; border-radius: 6px;
			padding: 6px;
			width: 140px;			
			font-size: 16px;
			background-color: #546e7a; color: #eeeeee;'''
		# Set Text widget to be read only :     
		[widget.setReadOnly(True) for widget in [self.dic_widget[x]['txt'] for x in self.dic_widget]]        
		# APPLY STYLE ON WIDGETS :
		self.setStyleSheet('background: #333333;')
		[widget.setStyleSheet(txt_style) for widget in [self.dic_widget[x]['txt'] for x in self.dic_widget]]
		[widget.setStyleSheet(label_style) for widget in [self.dic_widget[x]['label'] for x in self.dic_widget]]
		[widget.setStyleSheet(btn_style.format(colors='#007ac1; color: #EEEEEE')) for widget in [self.dic_widget[x]['btn_copy'] for x in self.dic_widget]]
		[widget.setStyleSheet(btn_style.format(colors='#c41c00; color: #EEEEEE')) for widget in [self.dic_widget[x]['btn_edit'] for x in self.dic_widget]]
		self.formSubject.setStyleSheet(form_style)
		self.formInfo.setStyleSheet(form_style)
		# Layout management :		
		self.vCodeLayout.addWidget(self.formInfo)
		self.vCodeLayout.addWidget(self.formSubject)		
		[self.vCodeLayout.addWidget(widget) for label,widgets in self.dic_widget.items()
		for inner_lab,widget in widgets.items()]		
		self.setLayout(self.vCodeLayout) # Connect the vertical layout to self		
		self.formSubject.setReadOnly(True)
		self.formInfo.setReadOnly(True)
		# SET SIZE POLICY
		self.size_policy.setHorizontalStretch(0)
		self.size_policy.setVerticalStretch(0)
		[widget.setSizePolicy(self.size_policy) for widget in [self.dic_widget[x]['btn_copy'] for x in self.dic_widget]]
		[widget.setSizePolicy(self.size_policy) for widget in [self.dic_widget[x]['btn_edit'] for x in self.dic_widget]]
		[widget.setSizePolicy(self.size_policy) for widget in [self.dic_widget[x]['label'] for x in self.dic_widget]]
		[self.dic_widget[label]['btn_copy'].clicked.connect(partial(self.copy_all, self.dic_widget[label]['txt'])) for 
		label in self.dic_widget]
		[self.dic_widget[label]['btn_edit'].clicked.connect(partial(self.emit_code, self.dic_widget[label]['txt'].toPlainText())) for 
		label in self.dic_widget]
		# Hide original/Plaintext textedit
		self.dic_widget['original']['txt'].setVisible(False)
		self.dic_widget['plaintext']['txt'].setVisible(False)
		self.dic_widget['plaintext']['btn_copy'].setVisible(False)
		self.dic_widget['plaintext']['btn_edit'].setVisible(False)
		self.dic_widget['original']['btn_copy'].setVisible(False)
		self.dic_widget['original']['btn_edit'].setVisible(False)
		[self.dic_widget[label]['label'].clicked.connect(partial(self.switch_visibility, [self.dic_widget[label]['txt'],
		self.dic_widget[label]['btn_copy'], self.dic_widget[label]['btn_edit']])) for label in self.dic_widget if label != 'processed']
		self.show()

	def emit_code(self, code):
		''' Emit signal "edit code" in order to send HTML code to main text editor '''		
		self.external['signal_editcode'].object_transfered.emit(code)
		self.close()

	def switch_visibility(self, widgets):
		for widget in widgets:
			if widget.isVisible():
				widget.setVisible(False)				
			else:
				widget.setVisible(True)

	def _set(self, original, processed, plaintext, subject='', info=''):
		self.__code['original'] = original
		self.__code['processed'] = processed
		self.__code['plaintext'] = plaintext
		try:
			self.dic_widget['original']['txt'].insertPlainText(self.__code['original'])
		except KeyError:
			pass
		try:
			self.dic_widget['processed']['txt'].insertPlainText(self.__code['processed'])
		except KeyError:
			pass
		try:
			self.dic_widget['plaintext']['txt'].insertPlainText(self.__code['plaintext'])
		except KeyError:
			pass
		self.formSubject.setText(subject)
		self.formInfo.setText(info)

	def copy_all(self, widget):
		""" Select all the content of the (text) widget then show
			a message in the status bar when finished """       
		widget.selectAll()
		widget.copy()
		return 'copied'
		
class ClickableLabel(QLabel):
	"""docstring for ClickableLable"""
	clicked = pyqtSignal()
	def __init__(self, text):
		super(ClickableLabel, self).__init__()
		self.setText(text)

	def mousePressEvent(self, event):
		self.clicked.emit()

class TimedMessageBox(QMessageBox):
	"""docstring for TimedMessageBox"""
	def __init__(self):
		super(TimedMessageBox, self).__init__()
		pass

	def countdown_close(self, timeout=3000):
		QTimer.singleShot(timeout, lambda: self.close())

class CustomNotification(QDialog):
	def __init__(self, parent=None):
		super(CustomNotification, self).__init__(parent)        
		self.event_manage()
		self.mainFrame = QFrame(self)
		self.headerLabel = QLabel(self.mainFrame)
		self.bodyText = QTextEdit(self.mainFrame)
		self.footerLabel = QLabel(self.mainFrame)		
		self.self_geo = {'width': self.geometry().width(), 'height': self.geometry().height()}
		self.screen_geo = {'width': QDesktopWidget().screenGeometry().width(), 'height': QDesktopWidget().screenGeometry().height()}
		self.corner = {}
		self.place_corner()
		self.gridMain = QGridLayout()
		self.vLayout = QVBoxLayout()
		self.animFinishedSignal = CustomSignal()
		self.animFinishedSignal.finished.connect(lambda: self.close())
		self.max_policy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

	def place_corner(self):
		self.corner = {}
		self.corner['top-left'] = QRect(0,0,self.self_geo['width'] // 2,self.self_geo['height'] // 2)
		self.corner['bottom-left'] = QRect(0,self.screen_geo['height']-self.self_geo['height'] // 2, self.self_geo['width'] // 2,self.self_geo['height'] // 2)
		self.corner['top-right'] = QRect(self.screen_geo['width']-self.self_geo['width'] // 2,0,self.self_geo['width'] // 2,self.self_geo['height'] // 4)
		self.corner['bottom-right'] = QRect(self.screen_geo['width']-self.self_geo['width'] // 2,self.screen_geo['height']-self.self_geo['height'] // 2,self.self_geo['width'] // 2,self.self_geo['height'] // 2)

	def set_bgcolor(self, error=False):
		error = '''QDialog {background: #e94c45; border-radius: 10px; border: 0px solid #e3e3e3;}
			QFrame {background: #e94c45;
				font-size: 14px; font-weight: bold; color: #ffffff;
				padding: 4px; border: 0px solid #e3e3e3; border-radius: 8px;
			}'''
		if error:
			self.setStyleSheet(error)
			
	def anim(self, t=8):
		display_time = t * 1000
		self.show()
		def animation(object_to_animate, details={'type': b'opacity', 'duration': 750, 
				'start': 1, 'end': 0}):
			''' Generic function that animate an object '''
			anim = QPropertyAnimation(object_to_animate, details['type'])
			anim.setDuration(details.get('duration', 750))
			anim.setStartValue(details.get('start', 1))
			anim.setEndValue(details.get('end', 0))            
			return anim		
		# 1. Create animation :
		print(self.screen_geo, self.self_geo)				
		# self.anim_move = animation(self, details={'type': b'geometry', 'duration': 600, 'start': QRect(self.screen_geo['width'],0,320,244),
		# 	'end': self.corner['top-right']})
		# self.anim_pause = animation(self, details={'type': b'geometry', 'duration': display_time, 'start': self.corner['top-right'],
		# 	'end': self.corner['top-right']})
		# self.anim_move2 = animation(self, details={'type': b'geometry', 'duration': 1400, 'start': self.corner['top-right'],
		# 	'end': QRect(self.screen_geo['width'],0,320,244)})
		self.anim_me = QPropertyAnimation(self, b'geometry')
		self.anim_me.setDuration(display_time)
		self.anim_me.setKeyValueAt(0, QRect(self.screen_geo['width'],0,self.self_geo['width']//2,self.self_geo['height']//4))
		self.anim_me.setKeyValueAt(0.2, self.corner['top-right'])
		self.anim_me.setKeyValueAt(0.8, self.corner['top-right'])
		self.anim_me.setKeyValueAt(1, QRect(self.screen_geo['width'],0,self.self_geo['width']//2,self.self_geo['height']//4))
		# 2. Group animations :
		# self.group_anim = QSequentialAnimationGroup()
		# self.group_anim.addAnimation(self.anim_fadein)
		# self.group_anim.addAnimation(self.anim_move)
		# self.group_anim.addAnimation(self.anim_pause)
		# self.group_anim.addAnimation(self.anim_move2)
		# self.group_anim.addAnimation(self.anim_fadeout)
		# self.group_anim.start()
		self.anim_me.start()
		def chrono(t):
			time.sleep(t)
			self.animFinishedSignal.finished.emit()
		t = threading.Thread(target=chrono, args=(10,))
		t.setDaemon(True)
		t.start()
		# group_anim.addAnimation(anim_fadein)
		# group_anim.addAnimation(anim_move)
		# group_anim.addAnimation(anim_fadeout)
		# group_anim.start(QAbstractAnimation.DeleteWhenStopped)			

	def init(self):
		self.setLayout(self.gridMain)		
		self.mainFrame.setLayout(self.vLayout)
		self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
		# Style :
		self.mainFrame.setFrameStyle(QFrame.Panel | QFrame.Raised)
		self.setStyleSheet('''
			QDialog {background: #51b2d6; border-radius: 10px; border: 0px solid #e3e3e3;}
			QFrame {background: #51b2d6; 
				font-size: 14px; font-weight: bold; color: #ffffff;
				padding: 4px; border: 0px solid #e3e3e3; border-radius: 8px;
			}
			QLabel {
				background: #d55c4b; font-size: 14px; font-family: verdana;
			}
			QLabel#headerLabel {background: #7646ff; font-size: 15px; font-weight: bold;}
			QLabel#footerLabel {background: #333333; color: #f1f0f0;}
		''')        
		# General setting :
		self.place()        
		self.gridMain.addWidget(self.mainFrame)
		self.vLayout.setSpacing(0)
		self.vLayout.addWidget(self.headerLabel, Qt.AlignTop)
		self.vLayout.addWidget(self.bodyText)
		self.vLayout.addWidget(self.footerLabel, Qt.AlignBottom)        
		self.bodyText.setAlignment(Qt.AlignLeft)
		self.bodyText.setReadOnly(True)
		self.setSizePolicy(self.max_policy)
		self.mainFrame.setSizePolicy(self.max_policy)
		self.footerLabel.setVisible(False)		

	def place(self, x=0, y=0, w=320, h=240):
		self.setGeometry(x, y, w, h)		

	def show_message(self, header, body, footer):
		self.headerLabel.setText(header)
		self.bodyText.setText(body)
		self.footerLabel.setText(footer)

	def notif_timer(self, task, timed_task, timeout=3000):
		try:
			task
		finally:
			QTimer.singleShot(timeout, functools.partial(timed_task[0], timed_task[1]))
		
	def event_manage(self):
		pass

class CustomSignal(QtCore.QObject):
	"""docstring for CustomSignal"""
	finished = QtCore.pyqtSignal()    
	object_transfered = QtCore.pyqtSignal(object)
	def __init__(self):
		super(CustomSignal, self).__init__()
		pass

		
def main():
	app = QtWidgets.QApplication(sys.argv)
	# ---------- Example ----------
	fen = QWidget() # Main widget
	fen.setGeometry(500,150,640,480)
	box = QHBoxLayout(fen)
	fen.show()
	fen.setLayout(box)
	tagLayout = QHBoxLayout()
	box.addLayout(tagLayout)	
	# Custom tag widget :
	def add_tag(layout, text):
		tag = CustomTag(layout, text)
		tag._set_label_style('''color: #333333; font-size: 11px;''')
	# Button control :
	btn = QPushButton('Test')
	box.addWidget(btn)
	btn.clicked.connect(lambda: add_tag(tagLayout, 'Taxi'))
	# 1. CUSTOM DIALOG RESULT	
	dialog = ResultDialog(box)
	box.addWidget(dialog)
	dialog._set('Processed', 'original', 'plaintext', 'subject', 'info')
	dialog.init()
	# 2. DIALOG NOTIFICATION :
	# notif = CustomNotification()	
	# notif.show_message('Kreatiki upload notification', 'The Crea with ID 5894 on Promoenexclu is optimized !', 'Thanks guys !')	
	# notif.init()
	# btn.clicked.connect(lambda: notif.anim(20))
	# --------------------------------------------------  
	app.exec_()

if __name__ == '__main__':
	main()