import subprocess
import sys
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6 import QtCore, QtWidgets
import os
from pytubefix import YouTube
from moviepy.editor import VideoFileClip
import cv2
from PySide6.QtGui import QIcon
from moviepy.config import change_settings
import shutil


if getattr(sys,'frozen',False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(base_dir, relative_path)

class Ui_Video_blur(object):
    def setupUi(self, Video_blur):
        Video_blur.setObjectName("Video_blur")
        Video_blur.resize(596, 497)
        self.centralwidget = QtWidgets.QWidget(Video_blur)
        self.centralwidget.setObjectName("centralwidget")
        self.downloadbord = QtWidgets.QGroupBox(self.centralwidget)
        self.downloadbord.setGeometry(QtCore.QRect(20, 10, 561, 61))
        self.downloadbord.setObjectName("downloadbord")
        self.download_lab = QtWidgets.QLineEdit(self.downloadbord)
        self.download_lab.setGeometry(QtCore.QRect(10, 20, 391, 31))
        self.download_lab.setObjectName("download_lab")
        self.download_btn = QtWidgets.QPushButton(self.downloadbord)
        self.download_btn.setGeometry(QtCore.QRect(420, 20, 121, 31))
        self.download_btn.setObjectName("download_btn")
        self.chnamebord = QtWidgets.QGroupBox(self.centralwidget)
        self.chnamebord.setGeometry(QtCore.QRect(20, 80, 561, 61))
        self.chnamebord.setObjectName("chnamebord")
        self.chname_lab = QtWidgets.QLineEdit(self.chnamebord)
        self.chname_lab.setGeometry(QtCore.QRect(10, 20, 391, 31))
        self.chname_lab.setObjectName("chname_lab")
        self.chname_btn = QtWidgets.QPushButton(self.chnamebord)
        self.chname_btn.setGeometry(QtCore.QRect(420, 20, 121, 31))
        self.chname_btn.setObjectName("chname_btn")
        self.tojpgbord = QtWidgets.QGroupBox(self.centralwidget)
        self.tojpgbord.setGeometry(QtCore.QRect(20, 150, 561, 61))
        self.tojpgbord.setObjectName("tojpgbord")
        self.tojpg_lab = QtWidgets.QLineEdit(self.tojpgbord)
        self.tojpg_lab.setGeometry(QtCore.QRect(10, 20, 391, 31))
        self.tojpg_lab.setObjectName("tojpg_lab")
        self.blur_btn = QtWidgets.QPushButton(self.tojpgbord)
        self.blur_btn.setGeometry(QtCore.QRect(420, 20, 121, 28))
        self.blur_btn.setObjectName("blur_btn")
        self.statusbord = QtWidgets.QGroupBox(self.centralwidget)
        self.statusbord.setGeometry(QtCore.QRect(20, 280, 561, 191))
        self.statusbord.setObjectName("statusbord")
        self.status_lab = QtWidgets.QTextBrowser(self.statusbord)
        self.status_lab.setGeometry(QtCore.QRect(5, 21, 541, 151))
        self.status_lab.setObjectName("status_lab")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(20, 210, 561, 71))
        self.groupBox.setObjectName("Progress")
        self.clear_btn = QtWidgets.QPushButton(self.groupBox)
        self.clear_btn.setGeometry(QtCore.QRect(420, 20, 121, 31))
        self.clear_btn.setObjectName("clear_btn")
        self.progressBar = QtWidgets.QProgressBar(self.groupBox)
        self.progressBar.setGeometry(QtCore.QRect(20, 40, 361, 21))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setStyleSheet("""QProgressBar {
                                                        border: 1px solid #bbb;
                                                        border-radius: 5px;
                                                        background-color: #eee;
                                                        text-align: center;
                                                        font-weight: bold;
                                                        }

                                    QProgressBar::chunk {
                                                        background-color: #0078d7;
                                                        width: 20px;
                                                        margin: 1px;
                                                        }""")
        self.process_txt = QtWidgets.QLabel(self.groupBox)
        self.process_txt.setGeometry(QtCore.QRect(130, 10, 161, 21))
        self.process_txt.setObjectName("process_txt")
        Video_blur.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(Video_blur)
        self.statusbar.setObjectName("statusbar")
        Video_blur.setStatusBar(self.statusbar)

        self.retranslateUi(Video_blur)
        QtCore.QMetaObject.connectSlotsByName(Video_blur)

    def retranslateUi(self, Video_blur):
        _translate = QtCore.QCoreApplication.translate
        Video_blur.setWindowTitle(_translate("Video_blur", "YoutubeVideo_download_blur"))
        self.downloadbord.setTitle(_translate("Video_blur", "Download_Youtube Video_URL"))
        self.download_btn.setText(_translate("Video_blur", "Download"))
        self.chnamebord.setTitle(_translate("Video_blur", "Change Video Name "))
        self.chname_btn.setText(_translate("Video_blur", "Change"))
        self.tojpgbord.setTitle(_translate("Video_blur", "Name of the video file you want to BLUR"))
        self.blur_btn.setText(_translate("Video_blur", "Blur"))
        self.statusbord.setTitle(_translate("Video_blur", "Log"))
        self.groupBox.setTitle(_translate("Video_blur", "GroupBox"))
        self.clear_btn.setText(_translate("Video_blur", "Clear"))
        self.process_txt.setText(_translate("Video_blur", "Download progress"))

class DownloadThread(QThread):
    progress = Signal(int)
    finished = Signal(str, str)
    error = Signal(str)
    
    def __init__(self,url,out_path):
        super().__init__()
        self.url = url
        self.out_path = out_path
        
    def run(self):
        try:
            yt = YouTube(self.url)
            ys = yt.streams.get_highest_resolution()
            filepath = ys.download(output_path=self.out_path)
            self.finished.emit(yt.title, filepath)
        except Exception as e:
            self.error.emit(str(e))
        
class RenameThread(QThread):
    finished = Signal(str)
    error = Signal(str)
    
    def __init__(self, old_path, new_name, base_dir):
        super().__init__()
        self.old_path = old_path
        self.new_name = new_name
        self.base_dir = base_dir

    def run(self):
        try:
            ext = os.path.splitext(self.old_path)[1]
            new_path = os.path.join(self.base_dir, self.new_name + ext)
            os.rename(self.old_path, new_path)
            self.finished.emit(new_path)
        except Exception as e:
            self.error.emit(str(e))

class BlurThread(QThread):
    progress = Signal(int)
    finished = Signal(str)
    error = Signal(str)
    log = Signal(str)
    
    def __init__(self, input_path, output_path):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path

    def run(self):
        try:
            change_settings({"FFMPEG_BINARY": resource_path("ffmpeg.exe")})

            audio_path = os.path.join(base_dir, "temp_audio.aac")
            temp_video_path = os.path.join(base_dir, "temp_blurred_video.mp4")

            self.log.emit("오디오 추출 중..")
            # 오디오만 추출
            audio_extract = subprocess.run([
                resource_path("ffmpeg.exe"),
                "-y",
                "-i", self.input_path,
                "-vn",
                "-acodec", "aac",
                audio_path
            ], capture_output=True, text=True)

            has_audio = True
            
            if audio_extract.returncode != 0:
                if "Stream map '0:a'" in audio_extract.stderr or \
                "does not contain any stream" in audio_extract.stderr or \
                "Output file #0 does not contain any stream" in audio_extract.stderr:
                    has_audio = False  # 오디오 없는 정상 상황
                    self.log.emit("오디오 없음..! 영상 모자이크 처리 중...")
                else:
                    self.error.emit(f"오디오 추출 실패:\n{audio_extract.stderr}")
                    return
                
            self.log.emit("오디오 추출 완료..! 영상 모자이크 처리 중...")
            
            cap = cv2.VideoCapture(self.input_path)
            
            if not cap.isOpened():
                self.error.emit("비디오를 열 수 없습니다.")
                return

            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            frontal_cascade = cv2.CascadeClassifier(resource_path("haarcascade_frontalface_default.xml"))
            profile_cascade = cv2.CascadeClassifier(resource_path("haarcascade_profileface.xml"))

            # 직접 영상 저장용 객체
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))

            count = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces_frontal = frontal_cascade.detectMultiScale(gray, 1.3, 5)
                faces_profile = profile_cascade.detectMultiScale(gray, 1.3, 5)
                faces = list(faces_frontal) + list(faces_profile)

                for (x, y, w, h) in faces:
                    face = frame[y:y+h, x:x+w]
                    small = cv2.resize(face, (10, 10), interpolation=cv2.INTER_LINEAR)
                    mosaic = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
                    frame[y:y+h, x:x+w] = mosaic

                out.write(frame)
                count += 1
                if frame_count:
                    progress = int((count / frame_count) * 100)
                    self.progress.emit(progress)

            cap.release()
            out.release()

            self.log.emit("영상 모자이크 처리 완료!")
            # ffmpeg로 오디오 붙이기 (안전한 방식)
            self.log.emit("영상 + 오디오 병합 중...")
            
            final_output = self.output_path
            if has_audio:
                try:
                    subprocess.run([
                        resource_path("ffmpeg.exe"),
                        "-y",
                        "-i", temp_video_path,
                        "-i", audio_path,
                        "-c:v", "copy",
                        "-c:a", "aac",
                        "-strict", "experimental",
                        final_output
                    ], check=True)
                except subprocess.CalledProcessError as e:
                    self.error.emit(f"ffmpeg 병합 실패: {e}")
                    return


                # 정리
                os.remove(temp_video_path)
                os.remove(audio_path)
            else:
                shutil.move(temp_video_path, final_output)

            self.finished.emit(final_output)

        except Exception as e:
            self.error.emit(str(e))


class Window(QMainWindow,Ui_Video_blur):
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.progressBar.setValue(0)
        self.setFixedSize(self.size())
        self.setWindowIcon(QIcon("icon.ico"))
        self.status_lab.append("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ설명서ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
        self.status_lab.append("1. 저장하고 싶은 유튜브 링크를 Download_Youtube Video_URL에 입력하세요")
        self.status_lab.append("2. 용량이 큰 파일이라면 시간이 걸릴 수 있습니다. progressbar가 안움직여도 다운로드 중입니다.")
        self.status_lab.append("3. 저장한 영상을 '영어'로 알기 쉽게 이름을 변경해주세요")
        self.status_lab.append("4. 얼굴에 모자이크를 처리를 하고싶다면 Name of the video file you want to BLUR에 파일명을   입력하세요")
        self.status_lab.append("5. 이 파일과 같은 폴더 내에 있는 영상파일이어야 합니다.")
        self.status_lab.append("6. 모자이크 처리는 시간이 걸릴 수 있습니다.")
        
        self.clear_btn.clicked.connect(self.clear_log)
        self.download_btn.clicked.connect(self.download_video)
        self.chname_btn.clicked.connect(self.rename_video)
        self.blur_btn.clicked.connect(self.blur_faces_in_video)
        
    def download_video(self):
        url = self.download_lab.text().strip()
        if not url:
            self.status_lab.append("URL을 입력하세요..!")
            return
        
        self.download_btn.setEnabled(False)
        self.status_lab.append("다운로드 준비 중...")
        self.progressBar.setValue(0)
        
        self.thread = DownloadThread(url, base_dir)
        self.thread.finished.connect(self.download_finished)
        self.thread.error.connect(self.download_failed)
        self.thread.start()
        
    def download_finished(self, title, filepath):
        self.progressBar.setValue(50)
        self.last_download_path = filepath
        self.status_lab.append(f"다운로드 완료: {title}")
        self.status_lab.append(f"다운로드 경로: {filepath}")
        self.download_btn.setEnabled(True)   
        self.progressBar.setValue(100) 
        
    def download_failed(self, error_msg):
        self.status_lab.append(f"다운로드 중 오류 발생: {error_msg}")
        self.download_btn.setEnabled(True)
        
    def clear_log(self):
        self.status_lab.clear()
        self.download_lab.setText("")
        self.chname_lab.setText("")
        self.tojpg_lab.setText("")
        self.progressBar.setValue(0)
        self.status_lab.append("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ설명서ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
        self.status_lab.append("1. 저장하고 싶은 유튜브 링크를 Download_Youtube Video_URL에 입력하세요")
        self.status_lab.append("2. 용량이 큰 파일이라면 시간이 걸릴 수 있습니다. progressbar가 안움직여도 다운로드 중입니다.")
        self.status_lab.append("3. 저장한 영상을 '영어'로 알기 쉽게 이름을 변경해주세요")
        self.status_lab.append("4. 얼굴에 모자이크를 처리를 하고싶다면 Name of the video file you want to BLUR에 파일명을   입력하세요")
        self.status_lab.append("5. 이 파일과 같은 폴더 내에 있는 영상파일이어야 합니다.")
        self.status_lab.append("6. 모자이크 처리는 시간이 걸릴 수 있습니다.")
    
    def rename_video(self):
        new_name = self.chname_lab.text().strip()
        if not new_name:
            self.status_lab.append("변경할 새 이름을 입력하세요.")
            return
        if not hasattr(self, "last_download_path"):
            self.status_lab.append("먼저 다운로드를 진행해 주세요")
            return
        self.progressBar.setValue(0)
        self.chname_btn.setEnabled(False)
        self.rename_thread = RenameThread(self.last_download_path, new_name, base_dir)
        self.rename_thread.finished.connect(self.rename_finished)
        self.rename_thread.error.connect(self.rename_failed)
        self.rename_thread.start()
    
    def rename_finished(self, new_path):
        self.status_lab.append(f"파일 이름이 성공적으로 변경 되었습니다.")
        self.status_lab.append(f"{os.path.basename(self.last_download_path)} -> {os.path.basename(new_path)}")
        self.last_download_path = new_path
        self.progressBar.setValue(100)
        self.chname_btn.setEnabled(True)
    
    def rename_failed(self, error_msg):
        self.status_lab.append(f"이름 변경 중 오류 발생: {error_msg}")
        self.chname_btn.setEnabled(True)
    
    def blur_faces_in_video(self):
        filename = self.tojpg_lab.text().strip()
        if not filename:
            self.status_lab.append("영상 파일 명을 입력하세요.")
            return
        
        input_path = os.path.join(base_dir, filename)
        output_path = os.path.join(base_dir, "blurred_" + filename)
        
        if not os.path.exists(input_path):
            self.status_lab.append(f"파일을 찾을 수 없습니다: {input_path}")
            return
        
        self.status_lab.append(f"얼굴 모자이크 처리 시작: {filename}")
        self.progressBar.setValue(0)
        self.blur_btn.setEnabled(False)
        
        self.blur_thread = BlurThread(input_path, output_path)
        self.blur_thread.progress.connect(self.update_progress)
        self.blur_thread.finished.connect(self.blur_finished)
        self.blur_thread.error.connect(self.blur_failed)
        self.blur_thread.log.connect(self.append_log)
        self.blur_thread.start()
    
    def blur_finished(self, output_path):
        self.status_lab.append(f"모자이크 + 오디오 완료 -> {output_path}")
        self.progressBar.setValue(0)
        self.blur_btn.setEnabled(True)
    
    def blur_failed(self, error_msg):
        self.status_lab.append(f"처리 중 오류 발생: {error_msg}")
        self.blur_btn.setEnabled(True)
        self.progressBar.setValue(0)
    
    def update_progress(self, value):
        self.progressBar.setValue(value)
        self.process_txt.setText(f"{value}%")
        if value == 100:
            self.status_lab.append("잠시만 기다려 주세요...")
            
    def append_log(self, msg):
        self.status_lab.append(msg)
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())       