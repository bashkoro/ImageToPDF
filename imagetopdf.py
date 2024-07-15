import sys
import cv2
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QFileDialog
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1231, 1080)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.imageLabel = QtWidgets.QLabel(self.centralwidget)
        self.imageLabel.setGeometry(QtCore.QRect(380, 10, 480, 800))
        self.imageLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.imageLabel.setText("")
        self.imageLabel.setObjectName("imageLabel")
        self.verticalSlider = QtWidgets.QSlider(self.centralwidget)
        self.verticalSlider.setGeometry(QtCore.QRect(930, 180, 22, 400))
        self.verticalSlider.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider.setMinimum(-100)
        self.verticalSlider.setMaximum(100)
        self.verticalSlider.setValue(0)
        self.verticalSlider.setObjectName("verticalSlider")
        self.loadImageButton = QtWidgets.QPushButton(self.centralwidget)
        self.loadImageButton.setGeometry(QtCore.QRect(380, 840, 480, 50))
        self.loadImageButton.setObjectName("loadImageButton")
        self.saveButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveButton.setGeometry(QtCore.QRect(380, 890, 480, 100))
        self.saveButton.setObjectName("saveButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1231, 24))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.loadImageButton.clicked.connect(self.load_image)
        self.saveButton.clicked.connect(self.save_to_pdf)
        self.verticalSlider.valueChanged.connect(self.update_brightness)

        self.image = None
        self.bright_image = None

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.loadImageButton.setText(_translate("MainWindow", "Load Image"))
        self.saveButton.setText(_translate("MainWindow", "Save To PDF"))

    def load_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(None, "Open Image File", "", "Image Files (*.png *.jpg *.bmp)", options=options)
        if file_path:
            self.image = cv2.imread(file_path)
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            self.update_image_label(self.image)

    def update_brightness(self):
        if self.image is not None:
            brightness_value = self.verticalSlider.value()
            self.bright_image = cv2.convertScaleAbs(self.image, alpha=1, beta=brightness_value)
            self.update_image_label(self.bright_image)

    def update_image_label(self, image):
        height, width = image.shape
        bytes_per_line = width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.imageLabel.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.imageLabel.setPixmap(scaled_pixmap)

    def save_to_pdf(self):
        if self.bright_image is not None:
            options = QFileDialog.Options()
            save_path, _ = QFileDialog.getSaveFileName(None, "Save PDF", "", "PDF Files (*.pdf)", options=options)
            if save_path:
                # Resize the image to A4 size
                a4_width, a4_height = A4
                resized_image = cv2.resize(self.bright_image, (int(a4_width), int(a4_height)))

                # Save the image as a temporary file
                temp_path = 'temp_image.jpg'
                cv2.imwrite(temp_path, resized_image)

                # Create the PDF and add the resized image
                pdf = canvas.Canvas(save_path, pagesize=A4)
                pdf.drawImage(temp_path, 0, 0, width=a4_width, height=a4_height)
                pdf.save()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
