# 🎭 Video_blur - 얼굴 모자이크 처리 GUI 애플리케이션

PySide6, OpenCV, moviepy, pytubefix 등을 활용하여 YouTube 영상을 다운로드하고,  
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
PyInstaller로 .exe 빌드된 실행 환경과 .py 파일 실행 환경에서 각각 경로 문제를 해결하기 위한 함수입니다.

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

## 📦 1. DownloadThread
YouTube 영상 다운로드 담당 스레드

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

다운로드 성공 시 finished 시그널로 제목/경로 전달
실패 시 error 시그널로 예외 메시지 전송

## 📦 2. RenameThread
영상 파일명 변경 담당 스레드

python
복사
편집
class RenameThread(QThread):
    ...
기존 경로에서 새 파일명으로 변경
성공/실패를 시그널로 GUI에 전달
📦 3. BlurThread
얼굴 모자이크 처리 스레드

python
복사
편집
class BlurThread(QThread):
    ...
OpenCV로 얼굴 인식 → 프레임 단위로 모자이크 처리
ffmpeg를 사용해 오디오와 병합
처리 도중 progress, log, error, finished 시그널을 통해 GUI와 연동
💡 에러 이슈 및 해결
.audio.write_audiofile() 에서 NoneType 에러 발생
→ moviepy 대신 subprocess + ffmpeg 방식으로 오디오 추출/병합 대체
🖥️ GUI 메인 클래스: Window
python
복사
편집
class Window(QMainWindow, Ui_Video_blur):
    ...
PySide6 기반 GUI 전체 제어
주요 메서드:
함수명	설명
download_video()	영상 다운로드 시작
rename_video()	영상 파일명 변경
blur_faces_in_video()	얼굴 블러 처리 시작
clear_log()	로그 및 입력 필드 초기화
update_progress()	진행률 반영
append_log()	로그 출력
📝 사용 설명서 (GUI 내부에도 표시됨)
유튜브 링크를 입력한 뒤 Download 버튼 클릭
파일명을 영어로 변경
모자이크 처리를 원하는 영상 파일명을 입력하고 Blur 버튼 클릭
처리 완료 후 blurred_파일명.mp4 생성됨
✅ 기타
.exe 실행 파일로 빌드 시 경로 관련 오류를 방지하기 위해 resource_path() 사용
얼굴 인식은 정면 + 측면 감지를 위해 두 개의 haarcascade 사용
