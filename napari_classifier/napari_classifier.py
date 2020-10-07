import os
from functools import partial
import napari
import pandas as pd
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (QWidget,
	QMessageBox,
	QFileDialog,
	QVBoxLayout,
	QHBoxLayout,
	QGridLayout,
	QPushButton,
	QLineEdit,
	QGroupBox
	)

DEFAULT_PATH = os.path.expanduser('~')

GUI_MAXIMUM_WIDTH = 2000
GUI_MINIMUM_WIDTH = 500
CLASS_PANEL_MINIMUM_WIDTH = 250
GUI_MAXIMUM_HEIGHT = 250

class Classifier(QWidget):
	def __init__(self, viewer, metadata_levels, *args, **kwargs):
		super(Classifier,self).__init__(*args,**kwargs)

		self.viewer = viewer

		# open image if not already open
		while len(self.viewer.layers)!=1:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)
			msg.setText("No image open, please select an image in the following dialog.")
			msg.exec()
			self.viewer.window.qt_viewer._open_files_dialog()

		# get image shape
		self.shape = self.viewer.layers[0].shape

		# check metadata levels
		if not metadata_levels:
			self.metadata_levels = [f'dim_{dim}' for dim in range(len(self.shape[:-2]))]
		elif len(metadata_levels)!=len(self.shape[:-2]):
			metadata_levels_warning = NapariNotification((f'Number of metadata_levels ({len(metadata_levels)}) does not match '
								f'number of leading image dimensions ({len(self.shape[:-2])}); will use default metadata_levels.'),
								severity='warning')
			metadata_levels_warning.show()
			self.metadata_levels = [f'dim_{dim}' for dim in range(len(self.shape[:-2]))]
		else:
			self.metadata_levels = metadata_levels

		# load metadata
		self.load_metadata()

		# initialize widget
		layout = QHBoxLayout()

		self.add_class_button = QPushButton('Add class',self)
		self.new_class_text = QLineEdit(self)
		self.new_class_text.setAlignment(Qt.AlignLeft)
		self.save_button = QPushButton('Save...',self)

		## io panel
		save_button = QPushButton('Save...',self)
		save_button.clicked.connect(self.save_results)
		io_panel = QWidget()
		io_layout = QVBoxLayout()
		io_layout.addWidget(save_button)
		io_panel.setLayout(io_layout)
		# io_panel.setMaximumWidth(GUI_MAXIMUM_WIDTH/4)
		layout.addWidget(io_panel)

		# initialize class panel
		self.classes_panel = QGroupBox('classes')
		self.classes_layout = QHBoxLayout()
		self.classes_layout.addWidget(self.add_class_button)
		self.classes_layout.addWidget(self.new_class_text)
		self.classes_panel.setMaximumWidth(GUI_MAXIMUM_WIDTH)
		self.classes_panel.setMinimumWidth(GUI_MINIMUM_WIDTH)
		self.classes_panel.setLayout(self.classes_layout)
		layout.addWidget(self.classes_panel)

		## set widget layout
		layout.setAlignment(Qt.AlignTop)
		layout.setSpacing(4)
		self.setLayout(layout)
		self.setMaximumHeight(GUI_MAXIMUM_HEIGHT)
		self.setMaximumWidth(GUI_MAXIMUM_WIDTH)

		self.add_class_button.clicked.connect(self.add_class)
		self.save_button.clicked.connect(self.save_results)
		self.classes = []
		self.class_buttons = []

	def load_metadata(self):
		filename = QFileDialog.getOpenFileName(self,'Open metadata table',DEFAULT_PATH,'Metadata table (*.csv *.hdf)')

		self.df_metadata = None
		if filename[0]:
			ext = filename[0].split('.')[-1]
			if ext == 'csv':
				self.df_metadata = pd.read_csv(filename[0])
			elif ext == 'hdf':
				self.df_metadata = pd.read_hdf(filename[0])
			else:
				print(f'filetype {ext} not recognized, creating default metadata table')

		if self.df_metadata is None:
			from itertools import product
			self.df_metadata = pd.DataFrame([{level:idx for level,idx in zip(self.metadata_levels,indices)} 
				for indices in product(*(range(dim) for dim in self.shape[:-2]))]
				)

		if 'annotated_class' not in self.df_metadata.columns:
			self.df_metadata = self.df_metadata.assign(annotated_class=None)

		self.df_metadata = self.df_metadata.set_index(self.metadata_levels)

	def add_class(self):
		self.classes.append(self.new_class_text.text())
		self.class_buttons.append(QPushButton('{class_name} [{num}]'.format(
			class_name=self.classes[-1], num=len(self.classes)),
			self))
		self.class_buttons[-1].clicked.connect(partial(self.classify_frame,key_press=None,chosen_class=self.classes[-1]))
		self.viewer.bind_key(key=str(len(self.classes)),func=partial(self.classify_frame,chosen_class=self.classes[-1]))

		self.classes_layout.addWidget(self.class_buttons[-1])

	def classify_frame(self,key_press,chosen_class):
		coords = self.viewer.layers[0].coordinates[:-2]
		self.df_metadata.loc[coords+('annotated_class',)] = chosen_class
		if self.shape[:-2]==coords:
			# last slice
			pass
		else:
			for level,(current,total) in enumerate(zip(coords[::-1],self.shape[::-1])):
				if current<total:
					self.viewer.dims._increment_dims_right(axis=(-3-level))
				else:
					self.viewer.dims._set_current_step(axis=(-3-level),value=0)
					self.viewer.dims._increment_dims_right(axis=(-4-level))


	def save_results(self):
		filename = QFileDialog.getSaveFileName(self,
        	'Export classification data',
        	os.path.join(DEFAULT_PATH, 'classified.csv'),
        	'Classification files (*.csv *.hdf)')

		if filename[0]:
			ext = filename[0].split('.')[-1]
			if ext == 'csv':
				self.df_metadata.to_csv(filename[0])
			elif ext == 'hdf':
				self.df_metadata.to_hdf(filename[0],'x',mode='w')
			else:
				print(f'filetype {ext} not recognized, cannot save')
		else:
			print('no file selected, did not save')


def build_widget(viewer,metadata_levels=None):
	classifier = Classifier(viewer,metadata_levels=metadata_levels)

	viewer.window.add_dock_widget(classifier,
		name='classifier',
		area='bottom'
		)