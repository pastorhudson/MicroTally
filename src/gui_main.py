import sys
import asyncio
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import QThreadPool, QRunnable
import argparse
import asyncio
from tally_server import cleanup, CAMERA_STATE, handle_tally, CAMERA_CONFIG, all_off
from utils import setup_logger, check_config, ConfigError, should_continue, get_wirecast_shots
import logging
import win32api
import win32con


class AsyncWorker(QRunnable):
    def __init__(self, coroutine, callback=None):
        super().__init__()
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
            logger.info('running')
            shots = get_wirecast_shots()
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

        # Stop event
        self.stop_event = asyncio.Event()

        # Layout and buttons
        self.setWindowTitle("MicroTally")
        self.setMinimumSize(400, 200)
        layout = QVBoxLayout()
        self.start_button = QPushButton("Start Tallys")
        self.stop_button = QPushButton("Stop Tallys")
        self.start_button.setStyleSheet("QPushButton {font-size:36; }")
        self.stop_button.setStyleSheet("QPushButton {font-size:36; }")

        self.stop_button.setEnabled(False)  # Disabled by default

        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Connect buttons
        self.start_button.clicked.connect(self.start_async_task)
        self.stop_button.clicked.connect(self.stop_async_task)

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
