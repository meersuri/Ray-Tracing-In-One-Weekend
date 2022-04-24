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

class ImageWidget(QWidget):
    def __init__(self, image):
        super().__init__()
        self.painter = QPainter(self)
        self.painter.begin(self)
        self.painter.setRenderHint(QPainter.Antialiasing)
        self.image = image

    def paintEvent(self, event: PySide2.QtGui.QPaintEvent) -> None:
        self.painter.drawImage(event.rect(), self.image)

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

        self.image_width = 200
        self.image_width_box = QLineEdit()
        self.image_width_box.setPlaceholderText(str(self.image_width))
        self.image_width_box.setInputMask('900')
        self.image_width_box.textChanged.connect(self.image_width_changed)
        self.image_width_box.setFixedWidth(40)

        self.image_height = 200
        self.image_height_box = QLineEdit()
        self.image_height_box.setPlaceholderText(str(self.image_height))
        self.image_height_box.setInputMask('900')
        self.image_height_box.textChanged.connect(self.image_height_changed)
        self.image_height_box.setFixedWidth(40)

        self.samples_per_pix = 2
        self.samples_per_pix_box = QLineEdit()
        self.samples_per_pix_box.setPlaceholderText(str(self.samples_per_pix))
        self.samples_per_pix_box.setInputMask('90')
        self.samples_per_pix_box.textChanged.connect(self.samples_per_pix_changed)
        self.samples_per_pix_box.setFixedWidth(30)
    
        self.max_depth = 2
        self.max_depth_box = QLineEdit()
        self.max_depth_box.setPlaceholderText(str(self.max_depth))
        self.max_depth_box.setInputMask('90')
        self.max_depth_box.textChanged.connect(self.max_depth_changed)
        self.max_depth_box.setFixedWidth(30)

        self.workers = 4
        self.workers_box = QLineEdit()
        self.workers_box.setPlaceholderText(str(self.workers))
        self.workers_box.setInputMask('90')
        self.workers_box.textChanged.connect(self.workers_changed)
        self.workers_box.setFixedWidth(30)
    
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
        self.display_widget.setPixmap(QPixmap(self.image_width, self.image_height))
        self.painter = QPainter(self.display_widget.pixmap())

        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.input_widget)
        self.main_layout.addWidget(self.display_widget)

        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)

        self.setCentralWidget(self.main_widget)

        self.render_process = None
        self.pixel_count = 0

    def render_clicked(self, is_checked):
        if not is_checked:
            self.render_process.kill()
            self.render_button.setText('Render')
            return
        print(self.pixel_count)
        self.render()
        self.render_button.setText('Stop')
    
    def image_width_changed(self, text):
        n = int(text) if text else 1
        self.image_width = min(max(1, n), 400)
        if self.image_width != n:
            self.image_width_box.setText(str(self.image_width))
        self.painter.end()
        self.display_widget.setPixmap(QPixmap(self.image_width, self.image_height))
        self.painter = QPainter(self.display_widget.pixmap())
    
    def image_height_changed(self, text):
        n = int(text) if text else 1
        self.image_height = min(max(1, n), 400)
        if self.image_height != n:
            self.image_height_box.setText(str(self.image_height))
        self.painter.end()
        self.display_widget.setPixmap(QPixmap(self.image_width, self.image_height))
        self.painter = QPainter(self.display_widget.pixmap())

    def samples_per_pix_changed(self, text):
        n = int(text) if text else 1
        self.samples_per_pix = min(max(1, n), 8)
        if self.samples_per_pix != n:
            self.samples_per_pix_box.setText(str(self.samples_per_pix))

    def max_depth_changed(self, text):
        n = int(text) if text else 1
        self.max_depth = min(max(1, n), 20)
        self.max_depth_box.setText(str(self.max_depth))

    def workers_changed(self, text):
        n = int(text) if text else 1
        self.workers = min(max(1, n), os.cpu_count())
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
#        self.render_process = Process(target=path_tracer_runner, kwargs=kwargs, daemon=False).start()
        self.render_process = QProcess()
        self.render_process.setProgram('python')
        self.render_process.setArguments([str(arg) for arg in args])
        self.render_process.readyReadStandardOutput.connect(self.set_pixel)
        self.render_process.start()

    def set_pixel(self):
        data = bytes(self.render_process.readLine()).decode()
        if len(data.strip().split(' ')) != 5:
            return

        row, col, r, g, b = [int(x) for x in data.split()]
#        self.image.setPixelColor(i, j, qRgb(r, g, b))
        self.painter.setPen(qRgb(r, g, b))
        self.painter.drawPoint(row, col)
        self.display_widget.update()
        self.pixel_count += 1

    def render_worker(self):
        self.pt = PathTracer()
        self.pt.run()

if __name__ == '__main__':
    app = QApplication([])
    window = PathTracerWindow()
    window.show()
    app.exec_()
