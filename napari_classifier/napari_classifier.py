import napari
# import pandas as pd
import sys
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (QWidget, 
	QVBoxLayout, 
	QHBoxLayout, 
	QPushButton,
	QLineEdit,
	QGroupBox
	)

# viewer = sys.argv[1]
# print(viewer)
GUI_MAXIMUM_WIDTH = 225
GUI_MAXIMUM_HEIGHT = 350

class Classifier(QWidget):
	def __init__(self,*args,**kwargs):
		super(Classifier,self).__init__(*args,**kwargs)

		layout = QVBoxLayout()

		self.load_metadata_button = QPushButton('Load metadata...',self)
		self.add_class_button = QPushButton('Add class',self)
		self.new_class_text = QLineEdit(self)
		self.new_class_text.setAlignment(Qt.AlignLeft)
		self.save_button = QPushButton('Save...',self)

		# io panel
		io_panel = QWidget()
		io_layout = QHBoxLayout()
		io_layout.addWidget(self.load_metadata_button)
		io_layout.addWidget(self.save_button)
		io_panel.setLayout(io_layout)
		io_panel.setMaximumWidth(GUI_MAXIMUM_WIDTH)
		layout.addWidget(io_panel)

		# initialize class panel
		self.classes_panel = QGroupBox('classes')
		self.classes_layout = QHBoxLayout()
		self.classes_layout.addWidget(self.add_class_button)
		self.classes_layout.addWidget(self.new_class_text)
		self.classes_panel.setMaximumWidth(GUI_MAXIMUM_WIDTH)
		self.classes_panel.setLayout(self.classes_layout)
		layout.addWidget(self.classes_panel)

		layout.setAlignment(Qt.AlignTop)
		layout.setSpacing(4)

		self.setLayout(layout)
		self.setMaximumHeight(GUI_MAXIMUM_HEIGHT)
		self.setMaximumWidth(GUI_MAXIMUM_WIDTH)

		self.load_metadata_button.clicked.connect(self.load_metadata)
		self.add_class_button.clicked.connect(self.add_class)
		self.save_button.clicked.connect(self.save_results)

	def load_metadata():
		print('metdata')

	def add_class():
		print('new class')

	def save_results():
		print('save')

def build_widget(viewer):
	classifier = Classifier()

	viewer.window.add_dock_widget(classifier,
		name='classifier',
		area='bottom'
		)