import napari
import pandas as pd
import os,sys
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (QWidget, 
	QVBoxLayout, 
	QHBoxLayout, 
	QPushButton,
	QLineEdit,
	QGroupBox
	)

DEFAULT_PATH = os.getcwd()

GUI_MAXIMUM_WIDTH = 225
GUI_MAXIMUM_HEIGHT = 350

class Classifier(QWidget):
	def __init__(self,viewer,metadata_levels,*args,**kwargs):
		super(Classifier,self).__init__(*args,**kwargs)

		self.viewer = viewer
		self.metadata_levels = metadata_levels

		if len(self.viewer.layers)!=1:
			raise ValueError('Please have a single image/layer open in napari before running classifier')

		classifier.load_metadata(metadata_levels)

		leading_dims = self.viewer.layers[0].shape[:-2]

		if self.df_metadata is None:
			from itertools import product
			self.df_metadata = pd.DataFrame([{level:idx for level,idx in zip(metadata_levels,indices)} 
				for indices in product(*(range(dim) for dim in leading_dims))]
				)

		self.df_metadata = self.df_metadata.assign(annotated_class=None).set_index(metadata_levels)

		layout = QHBoxLayout()

		# self.load_metadata_button = QPushButton('Load metadata...',self)
		self.add_class_button = QPushButton('Add class',self)
		self.new_class_text = QLineEdit(self)
		self.new_class_text.setAlignment(Qt.AlignLeft)
		self.save_button = QPushButton('Save...',self)

		# io panel
		io_panel = QWidget()
		io_layout = QVBoxLayout()
		# io_layout.addWidget(self.load_metadata_button)
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

		self.metadata_filename = None
		self.classes = []
		self.class_buttons = []

	def load_metadata():
		filename = QFileDialog.getOpenFileName(self,
			'Open metadata table',
			DEFAULT_PATH,
			'Metadata table (*.csv *.hdf)'
			)
		if filename[0]:
			ext = filename[0].split('.')[-1]
			if ext == 'csv':
				self.df_metadata = pd.read_csv(filename[0])
			elif ext = 'hdf':
				self.df_metadata = pd.read_hdf(filename[0])
		else:
			self.df_metadata = None

	def add_class():
		self.classes.append(self.new_class_text.text())
		self.class_buttons.append(QPushButton('{class_name} [{num}]'.format(
			class_name=self.classes[-1], num=len(self.classes)),
			self))
		self.class_buttons[-1].clicked.connect(self.classify_frame)

	def classify_frame():
		coords = self.viewer.layers[0].coordinates[:-2]
		self.df_metadata.loc[all(self.df_metadata[level]==coord 
			for level,coord in zip(self.metadata_levels,coords))] = 'annotated'

	def save_results():
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

def build_widget(viewer,metadata_levels=['cell','frame']):
	classifier = Classifier(viewer,metadata_levels=metadata_levels)

	viewer.window.add_dock_widget(classifier,
		name='classifier',
		area='bottom'
		)