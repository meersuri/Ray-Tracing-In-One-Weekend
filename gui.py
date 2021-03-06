from email.charset import QP
import sys
import os
import PySide2
from multiprocessing import Process

from main import PathTracer

dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

from PySide2.QtCore import Qt, QSize, QProcess
from PySide2.QtGui import QImage, QPainter, QPixmap, qRgb
from PySide2.QtWidgets import QApplication, QLabel, QLineEdit
from PySide2.QtWidgets import QPushButton, QMainWindow, QVBoxLayout, QHBoxLayout, QFormLayout, QWidget
from PySide2.QtWidgets import QMenu, QAction
from PySide2.QtWidgets import QCheckBox, QSpinBox, QSlider, QProgressBar, QComboBox

def path_tracer_runner(**kwargs):
    pt = PathTracer(**kwargs)
    pt.run()

class PathTracerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('PathTracer')
        self.setFixedWidth(1280)
        self.setFixedHeight(720)

        self.render_button = QPushButton('Render')
        self.render_button.setCheckable(True)
        self.render_button.clicked.connect(self.render_clicked)
        self.render_button.setFixedWidth(100)
        self.is_rendering = False

        self.save_button = QPushButton('Save')
        self.save_button.setFixedWidth(100)

        line_edit_attrs = [
            ('image_width', {'val': 100, 'in_mask': '900', 'width': 40, 'slot': self.image_width_changed, 'len': 3}),
            ('image_height', {'val': 100, 'in_mask': '900', 'width': 40, 'slot': self.image_height_changed, 'len': 3}),
            ('samples_per_pix', {'val': 2, 'in_mask': '90', 'width': 30, 'slot': self.samples_per_pix_changed, 'len': 2}),
            ('max_depth', {'val': 2, 'in_mask': '90', 'width': 30, 'slot': self.max_depth_changed, 'len': 2}),
            ('workers', {'val': 4, 'in_mask': '90', 'width': 30, 'slot': self.workers_changed, 'len': 2}),
        ]
        for attr_name, cfg in line_edit_attrs:
            setattr(self, attr_name, cfg['val'])
            box_attr_name = attr_name + '_box'
            setattr(self, box_attr_name, QLineEdit())
            getattr(self, box_attr_name).setPlaceholderText(str(cfg['val']))
            getattr(self, box_attr_name).setInputMask(cfg['in_mask'])
            getattr(self, box_attr_name).setFixedWidth(cfg['width'])
            getattr(self, box_attr_name).setMaxLength(cfg['len'])
            getattr(self, box_attr_name).textChanged.connect(cfg['slot'])

        self.form_layout = QFormLayout()
        self.form_layout.addRow('Image width', self.image_width_box)
        self.form_layout.addRow('Image height', self.image_height_box)
        self.form_layout.addRow('Samples/pix', self.samples_per_pix_box)
        self.form_layout.addRow('Max depth', self.max_depth_box)
        self.form_layout.addRow('Workers', self.workers_box)

        self.form_widget = QWidget()
        self.form_widget.setLayout(self.form_layout)

        self.input_layout = QVBoxLayout()
        self.input_layout.addWidget(self.form_widget)
        self.input_layout.addWidget(self.render_button)
        self.input_layout.addWidget(self.save_button)

        self.input_widget = QWidget()
        self.input_widget.setLayout(self.input_layout)

        self.display_widget = QLabel()
        pixmap = QPixmap(self.image_width, self.image_height)
        pixmap.fill(Qt.white)
        self.display_widget.setPixmap(pixmap)
        self.painter = QPainter(self.display_widget.pixmap())

        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.input_widget, Qt.AlignCenter)
        self.main_layout.addWidget(self.display_widget, Qt.AlignCenter)

        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)

        self.setCentralWidget(self.main_widget)

        self.render_process = None
        self.pixel_count = 0
        self.row, self.col = None, None
        self.r, self.g, self.b = None, None, None

    def render_clicked(self, is_checked):
        if not is_checked:
            self.render_process.kill()
            self.render_button.setText('Render')
            return
        self.render()
        self.render_button.setText('Stop')
    
    def image_width_changed(self, text):
        n = int(text) if text else 1
        self.image_width = min(max(1, n), 400)
        if self.image_width != n:
            self.image_width_box.setText(str(self.image_width))
        self.painter.end()
        pixmap = self.display_widget.pixmap()
        pixmap.fill(Qt.white)
        self.display_widget.setPixmap(pixmap.scaled(QSize(self.image_width, self.image_height)))
        self.painter = QPainter(self.display_widget.pixmap())

        self.main_layout.itemAt(1).setAlignment(Qt.AlignLeft)
    
    def image_height_changed(self, text):
        n = int(text) if text else 1
        self.image_height = min(max(1, n), 400)
        if self.image_height != n:
            self.image_height_box.setText(str(self.image_height))
        self.painter.end()
        pixmap = self.display_widget.pixmap()
        pixmap.fill(Qt.white)
        self.display_widget.setPixmap(pixmap.scaled(QSize(self.image_width, self.image_height)))
        self.painter = QPainter(self.display_widget.pixmap())

        self.main_layout.itemAt(1).setAlignment(Qt.AlignLeft)

    def samples_per_pix_changed(self, text):
        n = int(text) if text else 1
        self.samples_per_pix = min(max(1, n), 8)
        if self.samples_per_pix != n:
            self.samples_per_pix_box.setText(str(self.samples_per_pix))

    def max_depth_changed(self, text):
        n = int(text) if text else 1
        self.max_depth = min(max(1, n), 30)
        if self.max_depth != n:
            self.max_depth_box.setText(str(self.max_depth))

    def workers_changed(self, text):
        n = int(text) if text else 1
        self.workers = min(max(1, n), os.cpu_count())
        if self.workers != n:
            self.workers_box.setText(str(self.workers))

    def render(self):
        self.is_rendering = True
        kwargs=dict(
            image_width=self.image_width,
            image_height=self.image_height,
            samples_per_pix=self.samples_per_pix,
            max_depth=self.max_depth,
            workers=self.workers
        )
        args = [
            'main.py',
            self.image_width,
            self.image_height,
            self.samples_per_pix,
            self.max_depth,
            self.workers
        ]
        self.render_process = QProcess()
        self.render_process.setProgram('python')
        self.render_process.setArguments([str(arg) for arg in args])
        self.render_process.readyReadStandardOutput.connect(self.set_pixel)
        self.render_process.start()

    def set_pixel(self):
        data = bytes(self.render_process.readAllStandardOutput()).decode()
        parts = data.split('\n')
        for s in parts:
            if not s or ':' not in s:
                continue
            s = s.strip('\r')
            label, val = s.split(':')
            val = int(val)
            if label == 'x':
                self.row = self.image_width - 1 - val
            elif label == 'y':
                self.col = self.image_height - 1 - val
            elif label == 'r':
                self.r = val
            elif label == 'g':
                self.g = val
            elif label == 'b':
                self.b = val
            if all([
                self.row is not None,
                self.col is not None,
                self.r is not None,
                self.g is not None,
                self.b is not None
            ]):
                self.painter.setPen(qRgb(self.r, self.g, self.b))
                self.painter.drawPoint(self.row, self.col)
                self.display_widget.update()
                self.pixel_count += 1
                self.row, self.col = None, None
                self.r, self.g, self.b = None, None, None

    def render_worker(self):
        self.pt = PathTracer()
        self.pt.run()

if __name__ == '__main__':
    app = QApplication([])
    window = PathTracerWindow()
    window.show()
    app.exec_()
