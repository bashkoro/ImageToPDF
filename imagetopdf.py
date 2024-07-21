# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QFileDialog, QListWidget, QListWidgetItem
import cv2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1216, 982)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.imageLabel = QtWidgets.QLabel(self.centralwidget)
        self.imageLabel.setGeometry(QtCore.QRect(380, 10, 480, 800))
        self.imageLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.imageLabel.setObjectName("imageLabel")

        self.brightSlider = QtWidgets.QSlider(self.centralwidget)
        self.brightSlider.setGeometry(QtCore.QRect(930, 180, 22, 400))
        self.brightSlider.setOrientation(QtCore.Qt.Vertical)
        self.brightSlider.setObjectName("brightSlider")

        self.loadImageButton = QtWidgets.QPushButton(self.centralwidget)
        self.loadImageButton.setGeometry(QtCore.QRect(380, 840, 480, 50))
        self.loadImageButton.setObjectName("loadImageButton")

        self.saveButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveButton.setGeometry(QtCore.QRect(380, 890, 480, 100))
        self.saveButton.setObjectName("saveButton")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(910, 600, 58, 16))
        self.label.setObjectName("label")

        self.contrastSlider = QtWidgets.QSlider(self.centralwidget)
        self.contrastSlider.setGeometry(QtCore.QRect(1090, 180, 22, 400))
        self.contrastSlider.setOrientation(QtCore.Qt.Vertical)
        self.contrastSlider.setObjectName("contrastSlider")

        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(1070, 600, 58, 16))
        self.label_2.setObjectName("label_2")

        self.imageList = QtWidgets.QListWidget(self.centralwidget)
        self.imageList.setGeometry(QtCore.QRect(20, 10, 340, 860))
        self.imageList.setObjectName("imageList")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1216, 24))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Connect Signals and Slots
        self.loadImageButton.clicked.connect(self.load_images)
        self.saveButton.clicked.connect(self.save_to_pdf)
        self.brightSlider.valueChanged.connect(self.update_brightness)
        self.contrastSlider.valueChanged.connect(self.update_contrast)
        self.imageList.currentRowChanged.connect(self.display_selected_image)

        self.images = []
        self.processed_images = []

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Image to PDF"))
        self.loadImageButton.setText(_translate("MainWindow", "Load Images"))
        self.saveButton.setText(_translate("MainWindow", "Save To PDF"))
        self.label.setText(_translate("MainWindow", "Brightness"))
        self.label_2.setText(_translate("MainWindow", "Contrast"))

    def load_images(self):
        options = QFileDialog.Options()
        file_paths, _ = QFileDialog.getOpenFileNames(None, "Open Image Files", "", "Image Files (*.png *.jpg *.jpeg *.bmp)", options=options)
        if file_paths:
            self.imageList.clear()
            self.images = []
            for file_path in file_paths:
                image = cv2.imread(file_path)
                gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                self.images.append((file_path, gray_image))
                item = QListWidgetItem(file_path)
                self.imageList.addItem(item)
            if self.images:
                self.processed_images = [img[1] for img in self.images]
                self.display_selected_image(0)  # Display the first image

    def update_brightness(self):
        brightness_value = self.brightSlider.value()
        for i, (_, image) in enumerate(self.images):
            bright_image = cv2.convertScaleAbs(image, alpha=1, beta=brightness_value)
            self.processed_images[i] = bright_image
        self.display_selected_image(self.imageList.currentRow())

    def update_contrast(self):
        contrast_value = self.contrastSlider.value()
        for i, (_, image) in enumerate(self.images):
            alpha = contrast_value / 50.0 + 1  # Contrast control (1.0-3.0)
            beta = 0  # Brightness control (0-100)
            contrast_image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
            self.processed_images[i] = contrast_image
        self.display_selected_image(self.imageList.currentRow())

    def display_selected_image(self, index):
        if index >= 0 and index < len(self.processed_images):
            image = self.processed_images[index]
            height, width = image.shape
            bytes_per_line = width
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(self.imageLabel.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.imageLabel.setPixmap(scaled_pixmap)

    def save_to_pdf(self):
        if self.processed_images:
            options = QFileDialog.Options()
            save_path, _ = QFileDialog.getSaveFileName(None, "Save PDF", "", "PDF Files (*.pdf)", options=options)
            if save_path:
                pdf = canvas.Canvas(save_path, pagesize=A4)
                a4_width, a4_height = A4
                for img in self.processed_images:
                    resized_image = cv2.resize(img, (int(a4_width), int(a4_height)))
                    temp_path = 'temp_image.jpg'
                    cv2.imwrite(temp_path, resized_image)
                    pdf.drawImage(temp_path, 0, 0, width=a4_width, height=a4_height)
                    pdf.showPage()
                pdf.save()
                # Clean up the temporary file
                import os
                if os.path.exists(temp_path):
                    os.remove(temp_path)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
