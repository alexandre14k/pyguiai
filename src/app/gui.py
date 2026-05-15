# src/app/gui.py

from .init import qt_widgets_mod
from .init import qt_gui_mod
from .init import qt_core_mod
from .init import os_mod


class Gui:
    def __init__(self, queue_ref):
        self.queue = queue_ref
        self.app = qt_widgets_mod.QApplication([])
        self.win = qt_widgets_mod.QWidget()
        self.font_size = 12
        self._init_win()
        self._init_layout()
        self._bind_events()
        self._init_styles()

    def center_on_screen(self):
        screen = qt_widgets_mod.QApplication.primaryScreen()
        screen_geo = screen.availableGeometry()
        window_geo = self.frameGeometry()
        window_geo.moveCenter(screen_geo.center())
        self.move(window_geo.topLeft())

    def _init_styles(self):
        self.app.setStyleSheet("""
            QWidget {
                background-color: #F8F8F9;
                font-size: 14px;
            }

            QLabel {
                font-weight: bold;
                padding-bottom: 4px;
                color: #333333;
            }

            QTextEdit, QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 6px;
                color: #222222;
                selection-background-color: #CCE0FF;
            }

            /* Prompt box color override */
            #ui_prompt {
                background-color: #FFF8DC;
            }

            QPushButton {
                background-color: #E0E0E0;
                border: 1px solid #B0B0B0;
                border-radius: 4px;
                padding: 6px 12px;
                color: #222222;
            }

            QPushButton:hover {
                background-color: #D0D0D0;
            }

            QPushButton:pressed {
                background-color: #C0C0C0;
            }

            /* Scrollbar styling */
            QScrollBar:vertical {
                background: #E6E6E6;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical {
                background: #B0B0B0;
                min-height: 20px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical:hover {
                background: #909090;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar:horizontal {
                background: #E6E6E6;
                height: 12px;
                margin: 0px;
                border-radius: 6px;
            }

            QScrollBar::handle:horizontal {
                background: #B0B0B0;
                min-width: 20px;
                border-radius: 6px;
            }

            QScrollBar::handle:horizontal:hover {
                background: #909090;
            }

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)


    def _init_win(self):
        self.win.setWindowTitle("pyguiai")
        self.win.setMinimumSize(300, 400)

        f = qt_gui_mod.QFont()
        f.setPointSize(self.font_size)
        self.win.setFont(f)
        self._emoji_font()

    def _emoji_font(self):
        if os_mod.name == "nt":
            families = ["Segoe UI", "Segoe UI Emoji"]
        else:
            families = ["Noto Sans", "Noto Color Emoji"]

        f = self.win.font()
        f.setFamilies(families)
        self.win.setFont(f)

    def _init_layout(self):
        lay = qt_widgets_mod.QVBoxLayout()
        self.win.setLayout(lay)
        self._row1(lay)
        self._row2(lay)
        self._row3(lay)
        self._row4(lay)

    def _row1(self, lay):
        frame = qt_widgets_mod.QWidget()
        v = qt_widgets_mod.QVBoxLayout()
        frame.setLayout(v)

        label = qt_widgets_mod.QLabel("Context")
        self.ui_label_context = label

        left = qt_core_mod.Qt.AlignmentFlag.AlignLeft

        label.setAlignment(left)
        v.addWidget(label)

        box = qt_widgets_mod.QTextEdit()
        box.setObjectName("ui_context")
        box.setMinimumHeight(200)
        box.setReadOnly(True)
        box.setAlignment(left)

        self.ui_context = box
        v.addWidget(box)

        lay.addWidget(frame)

    def _row2(self, lay):
        frame = qt_widgets_mod.QWidget()
        v = qt_widgets_mod.QVBoxLayout()
        frame.setLayout(v)

        left = qt_core_mod.Qt.AlignmentFlag.AlignLeft

        label = qt_widgets_mod.QLabel("Prompt")
        self.ui_label_context = label

        label.setAlignment(left)
        v.addWidget(label)

        box = qt_widgets_mod.QLineEdit() # << was QTextEdit
        box.setObjectName("ui_prompt")
        box.setMinimumHeight(50)
        box.setAlignment(left)

        box.setText("python is hard ... i wonder why")

        self.ui_prompt = box
        v.addWidget(box)

        lay.addWidget(frame)

    def _row3(self, lay):
        w = qt_widgets_mod.QWidget()
        h = qt_widgets_mod.QHBoxLayout()
        w.setLayout(h)
        center = qt_core_mod.Qt.AlignmentFlag.AlignCenter
        h.setAlignment(center)
        self._buttons(h)
        lay.addWidget(w)

    def _buttons(self, h):
        b1 = qt_widgets_mod.QPushButton("Submit")
        b1.setObjectName("ui_button_submit")
        self.ui_button_submit = b1
        h.addWidget(b1)
        b2 = qt_widgets_mod.QPushButton("Clear")
        b2.setObjectName("ui_button_clear")
        self.ui_button_clear = b2
        h.addWidget(b2)
        b3 = qt_widgets_mod.QPushButton("Zoom")
        b3.setObjectName("ui_button_zoom")
        self.ui_button_zoom = b3
        h.addWidget(b3)
        b4 = qt_widgets_mod.QPushButton("Append")
        b4.setObjectName("ui_button_append")
        self.ui_button_append = b4
        h.addWidget(b4)
        b5 = qt_widgets_mod.QPushButton("Exit")
        b5.setObjectName("ui_button_exit")
        self.ui_button_exit = b5
        h.addWidget(b5)

    def _row4(self, lay):
        frame = qt_widgets_mod.QWidget()
        v = qt_widgets_mod.QVBoxLayout()
        frame.setLayout(v)

        # Label
        label = qt_widgets_mod.QLabel("Logger")
        self.ui_label_logger = label
        v.addWidget(label)

        # Logger box
        box = qt_widgets_mod.QLineEdit()
        box.setObjectName("ui_logger")
        box.setMinimumHeight(40)
        box.setReadOnly(True)
        center = qt_core_mod.Qt.AlignmentFlag.AlignCenter
        box.setAlignment(center)

        self.ui_logger = box
        v.addWidget(box)

        lay.addWidget(frame)

    def _bind_events(self):
        self.ui_button_submit.clicked.connect(
            self._cb_submit
        )
        self.ui_button_clear.clicked.connect(
            self._cb_clear
        )
        self.ui_button_zoom.clicked.connect(
            self._cb_zoom
        )
        self.ui_button_append.clicked.connect(
            self._cb_append
        )
        self.ui_button_exit.clicked.connect(
            self._cb_exit
        )
        self.win.closeEvent = self._cb_close

    def _send(self, src, data):
        msg = (src, data)
        self.queue.put(msg)

    def _cb_submit(self):
        self._send("ui_button_submit", "click")

    def _cb_clear(self):
        self._send("ui_button_clear", "click")

    def _cb_zoom(self):
        self._send("ui_button_zoom", "click")

    def _cb_append(self):
        self._send("ui_button_append", "click")

    def _cb_exit(self):
        self._send("ui_button_exit", "click")
        self.app.quit()

    def _cb_close(self, ev):
        self._cb_exit()
        ev.accept()

    def show_ui(self):
        self.win.show()
        self.app.exec()

    def zoom_ui(self):
        size = self.font_size + 2
        if size > 32:
            size = 12
        self.font_size = size

        f = self.win.font()
        f.setPointSize(size)

        self.win.setFont(f)

        self.ui_context.setFont(f)
        self.ui_prompt.setFont(f)
        self.ui_logger.setFont(f)

        self.ui_button_submit.setFont(f)
        self.ui_button_clear.setFont(f)
        self.ui_button_zoom.setFont(f)
        self.ui_button_append.setFont(f)
        self.ui_button_exit.setFont(f)

        self.win.updateGeometry()

    def logger_set(self, text):
        self.ui_logger.setText(text)

    def context_set(self, text):
        self.ui_context.setPlainText(text)

    def context_get(self):
        return self.ui_context.toPlainText()

    def prompt_set(self, text):
        self.ui_prompt.setText(text)

    def prompt_get(self):
        return self.ui_prompt.text()

    def clear_ui(self):
        self.ui_context.setPlainText("")
        self.ui_prompt.setText("")
        self.ui_logger.setText("")

    def append_ui(self, text):
        cursor = self.ui_context.textCursor()
        location = qt_gui_mod.QTextCursor.MoveOperation.End
        cursor.movePosition(location)
        cursor.insertText(text)

    def exit_ui(self):
        self.app.quit()


gui = Gui
