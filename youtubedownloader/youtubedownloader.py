from httpx import get
from pytubefix import YouTube
from pytubefix.cli import on_progress
import sys 
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from youtubedownload import Ui_MainWindow
import cv2

if getattr(sys,'frozen',False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

class Windowclass(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.progressBar.setValue(0)
        self.status_lab.clear()
        self.status_lab.append("-----사용법-------")
        self.status_lab.append("1. 저장하고 싶은 유튜브 링크를 \n Download_Youtube Video_URL에 입력하세요")
        self.status_lab.append("2. 저장한 영상을 '영어'로\n알기 쉽게 이름을 변경해주세요")
        self.status_lab.append("3. Frame은 0이상의 정수로 나타내주세요")
        self.status_lab.append("4. 1보타 클 수록 저장되는 프레임이 적어집니다.")
        self.download_btn.clicked.connect(self.download_video)
        self.clear_btn.clicked.connect(self.clear_log)
        self.chname_btn.clicked.connect(self.rename_video)   
        self.tojpg_btn.clicked.connect(self.convert_video_to_jpg)    
    
    
    def download_video(self):
        url = self.download_lab.text()
        if url.strip():
            self.status_lab.append("다운로드 준비 중...")
            self.progressBar.setValue(0)
            self.youtube_downloader(url)
        else:
            QMessageBox.warning(self, "Input Required", "Please enter a valid URL!")
    def youtube_downloader(self, url):
        try:
            yt = YouTube(url)
            ys = yt.streams.get_highest_resolution()
            filepath=ys.download(output_path=base_dir)
            self.last_download_path = filepath
            self.status_lab.append(f"다운로드 완료: {yt.title}")
            self.status_lab.append(f"다운로드 경로: {filepath}")
            self.progressBar.setValue(100)
        except Exception as e:
            self.status_lab.append(f"오류 발생: {str(e)}")
            self.status_lab.setWordWrap(True)
        def rename_video(self):
    
        if not self.last_download_path:  
            self.status_lab.append("먼저 다운로드를 완료해 주세요.")
            return
        new_name = self.chname_lab.text().strip()
        
        if not new_name:
            self.status_lab.append("새 파일 이름을 입력해 주세요.")
            return
        new_path = os.path.join(base_dir, new_name + ".mp4")
        
        try:
            os.rename(self.last_download_path, new_path)
            self.status_lab.append(f"파일 이름 변경 완료: \n -> {new_name}.mp4")
        except Exception as e:
            self.status_lab.append(f"이름 변경 실패: {str(e)}")         
    def clear_log(self):
        self.status_lab.clear()
        self.progressBar.setValue(0)
    def convert_video_to_jpg(self):
        filepath = self.tojpg_lab.text().strip()
        frame_interval = self.setting_lab.text().strip()
        
        if not filepath:
            self.status_lab.append("변환할 파일명을 입력하세요.")
            return
        try:
            frame_interval = float(frame_interval)
            if frame_interval <= 0:
                raise ValueError
        except ValueError:
            self.status_lab.append("프레임 간격은 1이상의 정수로 입력하세요")
            return
        self.status_lab.append(f"영상 변환 시작: {filepath}, {frame_interval}초 간격")
        self.progressBar.setValue(0)
        try:
            video_path = os.path.join(base_dir, filepath)
            video = cv2.VideoCapture(video_path)
                
            if not video.isOpened():
                self.status_lab.append(f"파일 열기 실패:{filepath}")
                self.status_lab.append("정확한 파일명과 확장자를 입력하세요.")
                return
            
            fps = video.get(cv2.CAP_PROP_FPS)
            video_name = os.path.splitext(os.path.basename(filepath))[0]
            save_dir = os.path.join(base_dir, video_name)
            os.makedirs(save_dir, exist_ok=True)
            
            count = 0
            frame_count =0
            
            while video.isOpened():
                ret, image = video.read()
                if not ret:
                    break
                if int(video.get(cv2.CAP_PROP_POS_FRAMES)) % round(fps * frame_interval) == 0:
                    filename = os.path.join(save_dir, f"frame{count}.jpg")
                    cv2.imwrite(filename, image)
                    self.status_lab.append(f"frame{count}.저장: {filename}")
                    count += 1
            self.progressBar.setValue(100)
        except Exception as e:
            self.status_lab.append(f"변환실패: {str(e)}") 
                
if __name__ == "__main__" :
    app = QApplication(sys.argv) 
    myWindow = Windowclass() 
    myWindow.show() 
    app.exec_()