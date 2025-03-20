<p align="center">
  <img src="https://github.com/user-attachments/assets/90153858-df2e-4668-8765-f36a1aa7fabb" width="400"/>
</p>

# 🎭 Video_blur - 얼굴 모자이크 처리 GUI 애플리케이션

- 기존 youtubedownload 애플리케이션을 업그레이드 한 버전으로 얼굴인식 + 블러 처리 기능 추가
- QThread 기반 멀티 스레딩 도입
- GUI 구성 향상 (PyQt5 -> PySide6)
- PyInstaller 대응 강화
- PySide6, OpenCV, moviepy, pytubefix 등을 활용하여 YouTube 영상을 다운로드하고,  
해당 영상에서 얼굴을 자동으로 인식해 모자이크(블러) 처리를 할 수 있는 **Windows 데스크톱 GUI 애플리케이션**입니다.

---

## 🎯 프로그램 개요

- 유튜브 영상 다운로드
- 다운로드한 영상 이름 변경
- 영상에서 얼굴 인식 후 블러 처리
- 진행 상태를 GUI에서 실시간 확인 가능 (진행률, 로그, Clear 버튼 등)

---

## 🔧 사용된 주요 라이브러리

| 라이브러리 | 설명 |
|------------|------|
| `PySide6` | 파이썬에서 Qt 기반 GUI를 구현 |
| `pytubefix` | YouTube 영상 다운로드 |
| `moviepy` | 영상 및 오디오 처리 |
| `OpenCV` | 얼굴 인식 및 영상 처리 |
| `subprocess` | ffmpeg 등 외부 실행파일 호출용 |

```python
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
```

## 📁 경로 처리 (resource_path)
- PyInstaller로 .exe 빌드된 실행 환경과 .py 파일 실행할 때의 파일 경로를 다르게 처리함.
resource_path() 함수는 실행 파일 또는 소스 위치에 있는 리소스 파일 경로를 반환.


```python
if getattr(sys,'frozen',False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(base_dir, relative_path)

 #PyInstaller로 패키징한 exe 실행시 sys에 _MEIPASS 속성을 추가
 #sys._MEIPASS -> 임시 디렉토리
 #.exe -> _MEIPASS가 존재하므로 여기 경로 사용
 #.py -> _MEIPASS가 존재x 현재 디렉터리 기준의 상대경로 사용
```

## 🧵 QThread 기반 멀티스레딩 구성
- GUI의 응답을 유지하기 위해 주요 작업을 QThread로 정리

### 📌 1. DownloadThread
- YouTube 영상 다운로드 담당 스레드

```python
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
```

- 다운로드 성공 시 finished 시그널로 제목/경로 전달
- 실패 시 error 시그널로 예외 메시지 전송

### 📌 2. RenameThread
- 영상 파일명 변경 담당 스레드

```python
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
```

- 기존 경로에서 새 파일명으로 변경
- 성공/실패를 시그널로 GUI에 전달
- blur처리 시 한글, 공백으로 인한 오류 예방

### 📌 3. BlurThread
- 얼굴 모자이크 처리 스레드

```python
class BlurThread(QThread):
		#시그널 사용
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
		        #moviepy에서 사용할 FFMPEG 실행 파일 경로 설정
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
                audio_path         #영상에서 오디오만 추출해서 temp_audio.aac로 저장함.
            ], capture_output=True, text=True)

            has_audio = True
            
            if audio_extract.returncode != 0:   #예외 처리
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
                
            #영상 프레임 단위로 얼굴 블러 처리

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
            
            #오디오 병합
            
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


                # 파일 정리
                os.remove(temp_video_path)
                os.remove(audio_path)
            else:
                shutil.move(temp_video_path, final_output)

            self.finished.emit(final_output)

        except Exception as e:
            self.error.emit(str(e))
```

- OpenCV로 얼굴 인식 → 프레임 단위로 모자이크 처리
- ffmpeg를 사용해 오디오와 병합
- 처리 도중 progress, log, error, finished 시그널을 통해 GUI와 연동


## 💡 에러 이슈 및 해결
- .audio.write_audiofile() 에서 NoneType 에러 발생
- → moviepy 대신 subprocess + ffmpeg 방식으로 오디오 추출/병합 대체


## 🖥️ GUI 메인 클래스: Window
```python
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
```

- GUI의 주요 기능을 담당하는 **Window 클래스**의 핵심 메서드

| 함수명 | 설명 |
|--------|--------------------------------|
| `download_video()` | 유튜브 영상 다운로드 시작 |
| `rename_video()` | 다운로드한 영상 파일명 변경 |
| `blur_faces_in_video()` | 얼굴 블러 처리 시작 |
| `clear_log()` | 로그 및 입력 필드 초기화 |
| `update_progress()` | 진행률 업데이트 |
| `append_log()` | 로그 추가 및 출력 | 

---

## 📝 사용 설명서 (GUI 내부에도 표시됨)
- 유튜브 링크를 입력한 뒤 Download 버튼 클릭
- 파일명을 영어로 변경
모자이크 처리를 원하는 영상 파일명을 입력하고 Blur 버튼 클릭
처리 완료 후 blurred_파일명.mp4 생성됨


## ✅ 기타
.exe 실행 파일로 빌드 시 경로 관련 오류를 방지하기 위해 resource_path() 사용
얼굴 인식은 정면 + 측면 감지를 위해 두 개의 haarcascade 사용
