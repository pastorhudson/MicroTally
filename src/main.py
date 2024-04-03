import sys
from configparser import ConfigParser
from editconfig import ConfigEditor
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QSpacerItem, \
    QSizePolicy
from PySide6.QtCore import QThreadPool, QRunnable
import asyncio
from tally_server import CAMERA_STATE, handle_tally, CAMERA_CONFIG, all_off
from utils import setup_logger, check_config, resource_path

if sys.platform.startswith('win'):
    from utils import get_wirecast_shots
elif sys.platform.startswith('darwin'):
    from mac_wirecast import get_mac_wirecast_shots


class AsyncWorker(QRunnable):
    def __init__(self, coroutine, callback=None):
        super().__init__()
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.coroutine = coroutine
        self.callback = callback

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        task = loop.create_task(self.coroutine)
        loop.run_until_complete(task)
        loop.close()
        # Execute callback after completion if provided
        if self.callback:
            self.callback()


async def async_task(stop_event):
    logger = setup_logger('microtally')

    try:
        logger.info("Checking Config")
        check_config()
        logger.info('Starting MicroTally')
        while not stop_event.is_set():
            if sys.platform.startswith('win'):
                shots = get_wirecast_shots()
            elif sys.platform.startswith('darwin'):
                shots = get_mac_wirecast_shots()
            for shot_type, shots in shots.items():
                # logger.debug(f"{shot_type}, {shots}")
                # logger.debug(CAMERA_STATE)
                if shot_type == 'queue' and not shots:
                    # logger.debug('Nothing Queued!')
                    for cam, cam_state in CAMERA_STATE.items():
                        # logger.debug(f"{cam}, {cam_state}")
                        if cam_state == 'queue':
                            await handle_tally(cam, "off")

                for shot in shots:
                    if shot.lower() in CAMERA_CONFIG and CAMERA_STATE[shot.lower()] != shot_type:
                        logger.info(f"Updating: {shot.lower()} to {shot_type}")
                        CAMERA_STATE[shot.lower()] = shot_type
                        await handle_tally(shot.lower(), shot_type)
                    else:
                        logger.debug('skipping no updates')
            await asyncio.sleep(.5)
        await all_off()
        # while not stop_event.is_set():
        #     print("Doing something...")
        #     await asyncio.sleep(1)  # Simulate async work
    except asyncio.CancelledError:
        print("Task was cancelled!")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()
        check_config()
        # Stop event
        self.stop_event = asyncio.Event()

        # Main window setup
        self.setWindowTitle("MicroTally")
        self.setMinimumSize(400, 200)
        self.setWindowIcon(QIcon(resource_path('images/MicroTally.ico')))

        # Main layout
        layout = QVBoxLayout()

        # Top row layout for gear button
        topRowLayout = QHBoxLayout()
        gearButton = QPushButton()
        gearButton.setIcon(QIcon(resource_path('images/settings.png')))  # Make sure to adjust the path to your actual gear icon

        gearButton.setFixedSize(40, 40)
        gearButton.clicked.connect(self.open_config_editor)

        # Add spacer and gear button to the top row layout
        topRowLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum))
        topRowLayout.addWidget(gearButton)

        # Add the top row layout to the main layout
        layout.addLayout(topRowLayout)

        # Configure and add the start and stop buttons
        self.start_button = QPushButton("Start Tallys")
        self.stop_button = QPushButton("Stop Tallys")
        self.start_button.setStyleSheet("QPushButton {font-size:36; }")
        self.stop_button.setStyleSheet("QPushButton {font-size:36; }")
        self.stop_button.setEnabled(False)  # Disabled by default

        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        # Set the main layout
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Connect buttons to their functions
        self.start_button.clicked.connect(self.start_async_task)
        self.stop_button.clicked.connect(self.stop_async_task)

    def open_config_editor(self):
        self.editor = ConfigEditor()
        self.editor.show()

    def start_async_task(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        worker = AsyncWorker(async_task(self.stop_event), self.on_task_complete)
        self.threadpool.start(worker)

    def stop_async_task(self):
        self.stop_event.set()  # Signal the task to stop

    def on_task_complete(self):
        # Reset UI and stop event for next task
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.stop_event.clear()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
