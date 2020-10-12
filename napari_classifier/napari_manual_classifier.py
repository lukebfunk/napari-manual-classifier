import os
from functools import partial
import napari
from napari._qt.qt_error_notification import NapariNotification
import pandas as pd
import numpy as np
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

MAXIMUM_CLASS_BUTTONS_PER_COLUMN = 4

class Classifier(QWidget):
	def __init__(self, viewer, metadata_levels, initial_classes, *args, **kwargs):
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

		## io panel
		save_button = QPushButton('Save...',self)
		save_button.clicked.connect(self.save_results)
		io_panel = QWidget()
		io_layout = QVBoxLayout()
		io_layout.addWidget(save_button)
		io_panel.setLayout(io_layout)
		layout.addWidget(io_panel)

		## class panel
		classes_panel = QGroupBox('classes')
		classes_panel.setMinimumWidth(CLASS_PANEL_MINIMUM_WIDTH)

		### layout for adding classes
		add_classes_layout = QHBoxLayout()
		add_class_button = QPushButton('Add class',self)
		add_class_button.clicked.connect(self.click_add_class)
		self.new_class_text = QLineEdit(self)
		self.new_class_text.setAlignment(Qt.AlignLeft)
		add_classes_layout.addWidget(add_class_button)
		add_classes_layout.addWidget(self.new_class_text)

		### layout for class buttons
		self.class_button_layout = QGridLayout()

		### add sub layouts to class panel
		classes_layout = QVBoxLayout()
		classes_layout.addLayout(add_classes_layout)
		classes_layout.addLayout(self.class_button_layout)
		classes_panel.setLayout(classes_layout)
		layout.addWidget(classes_panel)

		## set widget layout
		layout.setAlignment(Qt.AlignTop)
		layout.setSpacing(4)
		self.setLayout(layout)
		self.setMaximumHeight(GUI_MAXIMUM_HEIGHT)
		self.setMaximumWidth(GUI_MAXIMUM_WIDTH)

		# initialize classes
		self.classes = []

		if initial_classes is not None:
			for initial_class in initial_classes:
				self.add_class(initial_class)

	def load_metadata(self):
		# msg = QMessageBox()
		# msg.setIcon(QMessageBox.Information)
		# msg.setText(("Use the following dialog to choose a metadata table to open, "
		# 				"otherwise click 'cancel' to use an automatically generated table."))
		# msg.exec()

		# filename = QFileDialog.getOpenFileName(self,'Open metadata table',DEFAULT_PATH,'Metadata table (*.csv *.hdf)')

		self.df_metadata = None
		# if filename[0]:
		# 	ext = filename[0].split('.')[-1]
		# 	if ext == 'csv':
		# 		self.df_metadata = pd.read_csv(filename[0])
		# 	elif ext == 'hdf':
		# 		self.df_metadata = pd.read_hdf(filename[0])
		# 	else:
		# 		print(f'filetype {ext} not recognized, creating default metadata table')

		if self.df_metadata is None:
			from itertools import product
			self.df_metadata = pd.DataFrame([{level:idx for level,idx in zip(self.metadata_levels,indices)} 
				for indices in product(*(range(dim) for dim in self.shape[:-2]))]
				)

		if 'annotated_class' not in self.df_metadata.columns:
			self.df_metadata = self.df_metadata.assign(annotated_class=None)

		self.df_metadata = self.df_metadata.set_index(self.metadata_levels)

	def click_add_class(self):
		self.add_class(self.new_class_text.text())
		self.new_class_text.clear()

	def add_class(self,new_class):
		self.classes.append(new_class)

		if len(self.classes)<10:
			# shortcut key binding available
			self.viewer.bind_key(key=str(len(self.classes)),
				func=partial(self.classify_frame,chosen_class=self.classes[-1]),
				overwrite=True)
			new_class_button = QPushButton('{class_name} [{num}]'.format(
				class_name=self.classes[-1], num=len(self.classes)),
				self)
		else:
			# shortcut key binding not available
			many_classes_notification = NapariNotification(
				('Shortcut key bindings not available with the 10th or further class'),
				severity='info')
			many_classes_notification.show()

			new_class_button = QPushButton(self.classes[-1],self)
	
		new_class_button.clicked.connect(partial(self.classify_frame,key_press=None,chosen_class=self.classes[-1]))

		self.class_button_layout.addWidget(new_class_button,
			((len(self.classes)-1)%MAXIMUM_CLASS_BUTTONS_PER_COLUMN),
			int((len(self.classes)-1)/MAXIMUM_CLASS_BUTTONS_PER_COLUMN)
			)


	def classify_frame(self,key_press,chosen_class):
		# TODO: create an annotation status bar that reports class of current slice
		coords = self.viewer.layers[0].coordinates[:-2]

		coords_string = ', '.join([f'{level}={val}' for level,val in zip(self.metadata_levels,coords)])
		if self.df_metadata.loc[(coords),('annotated_class')] is not None:
			previous_class = self.df_metadata.loc[(coords),('annotated_class')]
			if previous_class != chosen_class:
				overwrite_notification = NapariNotification((f'{coords_string} previously annotated as '
								f'`{previous_class}`, overwriting annotation as `{chosen_class}`'),
								severity='info')
				overwrite_notification.show()
		else:
			annotate_notification = NapariNotification((f'Annotating {coords_string} as `{chosen_class}`'),
									severity='info')
			annotate_notification.show()

		
		self.df_metadata.loc[(coords),('annotated_class')] = chosen_class

		if tuple(np.array(self.shape[:-2])-1)==coords:
			# last slice
			pass
		else:
			if coords[-1]<(self.shape[-3]-1):
				self.viewer.dims._increment_dims_right(axis=(-3))
			else:
				self.viewer.dims.set_current_step(axis=(-3),value=0)
				self.viewer.dims._increment_dims_right(axis=(-4))


	def save_results(self):
		filename = QFileDialog.getSaveFileName(self,
        	'Export classification data',
        	os.path.join(DEFAULT_PATH, self.viewer.layers[0].name+'.classified.csv'),
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


def build_widget(viewer, metadata_levels=None, initial_classes=['interphase','prophase','metaphase','anaphase/telophase','apoptosis/death']):
	classifier = Classifier(viewer, metadata_levels=metadata_levels, initial_classes=initial_classes)

	viewer.window.add_dock_widget(classifier,
		name='classifier',
		area='bottom'
		)