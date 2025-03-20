<p align="center">
  <img src="https://github.com/user-attachments/assets/cb27f64d-80cf-41a4-9e5b-52d803e5f808" width="400"/>
</p>

### 🎬 유튜브 영상 다운로드 및 파일이름 변경과 프레임 추출 프로그램
## 📌 개요
- PyQt5 기반의 GUI를 통해 유튜브 링크를 입력하면
해당 영상을 다운로드, 파일 이름을 변경,
그리고 일정 간격으로 프레임을 추출하여 JPG 이미지로 저장할 수 있는 기능을 제공합니다.

## 📌 사용된 주요 모듈

| 모듈           | 설명                                 |
|----------------|--------------------------------------|
| `pytubefix`    | YouTube 영상 다운로드를 위한 라이브러리 |
| `cv2 (OpenCV)` | 영상에서 프레임을 추출하고 저장         |
| `os`, `sys`    | 경로 처리 및 실행 환경 확인 등 시스템 작업 |
| `PyQt5`        | GUI 구성 및 사용자 입력 처리            |

```python
from pytubefix import YouTube
from pytubefix.cli import on_progress
import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from youtubedownload import Ui_MainWindow
import cv2
```
❗ 프로그레스 바는 0% 또는 100%로만 작동 (중간 상태는 생략됨)

## 📌 경로 처리 방식
```python
if getattr(sys,'frozen',False):  # 패키징된 실행 파일인지 확인
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))
```
- .exe 배포 시 파일 경로 오류를 막기 위해 실행 파일 위치 기준으로 경로 처리
- sys.frozen: 실행 파일일 경우 True
- os.path.abspath(__file__): 현재 파일의 절대경로

✅ .py, .exe 환경 모두에서 동일하게 작동 → 이식성 향상



## 📌 .ui 파일 연결 방식
- .ui 직접 로딩은 .ui 파일 필수 → 배포 시 문제 발생
테스트 후 pyuic5로 .py 파일로 변환해 사용
```bash
pyuic5 youtubedownload.ui -o youtubedownload.py
```
```python
from youtubedownload import Ui_MainWindow

class Windowclass(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
```
- IDE 자동환성 사용이 어려움
- ⇒ 테스트가 끝난 후에는 .py 파일로 변경하여 배포후에도 .ui파일 없이 코드만으로 실행 가능함.
## 📌 주요 클래스 및 초기 설정
```python
class Windowclass(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.progressBar.setValue(0)
        self.status_lab.clear()
        self.status_lab.append("-----사용법-------")
        self.status_lab.append("1. 유튜브 링크 입력")
        self.status_lab.append("2. 영어 이름으로 변경")
        self.status_lab.append("3. 프레임 간격 숫자 입력")
        self.status_lab.append("4. 1보다 클수록 프레임 간격 증가")

        self.download_btn.clicked.connect(self.download_video)
        self.clear_btn.clicked.connect(self.clear_log)
        self.chname_btn.clicked.connect(self.rename_video)
        self.tojpg_btn.clicked.connect(self.convert_video_to_jpg)
```
- Ui_MainWindow는 변환된 .py 파일에 정의된 클래스
- self.setupUi(self)를 통해 현재 클래스에 UI 요소들을 로드함
- GUI 초기 설정 및 버튼 이벤트 연결
- status_lab에 사용 설명 기입.
## 📌 download_video(self)
```python
def download_video(self):
    url = self.download_lab.text()
    if url.strip():
        self.status_lab.append("다운로드 준비 중...")
        self.progressBar.setValue(0)
        self.youtube_downloader(url)
    else:
        QMessageBox.warning(self, "Input Required", "Please enter a valid URL!")
```
- 사용자가 입력한 URL이 유효하면 youtube_downloader를 호출함
- 사용자 실수를 막기 위해 URL이 공백일 시 경고메시지 표시
- 정상 URL이라면 youtube_downloader 함수 호출
## 📌 youtube_downloader(self, url)
```python
def youtube_downloader(self, url):
    try:
        yt = YouTube(url)
        ys = yt.streams.get_highest_resolution()
        filepath = ys.download(output_path=base_dir)
        self.last_download_path = filepath
        self.status_lab.append(f"다운로드 완료: {yt.title}")
        self.status_lab.append(f"다운로드 경로: {filepath}")
        self.progressBar.setValue(100)
    except Exception as e:
        self.status_lab.append(f"오류 발생: {str(e)}")
```
- YouTube(url) 객체 생성 → 가장 고화질 스트림 선택 → 지정 경로로 다운로드
- 다운로드 완료 후 상태로그에 경로 및 제목을 표시함
- 어떤 오류가 발생하더라도 상태 로그에 예외 메시지 출력
- 다운로드 성공시 progressBar = 100%
## 📌 rename_video(self)
```python
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
        self.status_lab.append(f"파일 이름 변경 완료 → {new_name}.mp4")
    except Exception as e:
        self.status_lab.append(f"이름 변경 실패: {str(e)}")
```
- 다운로드한 영상의 파일을 변경한다.
- 마지막 다운로드 경로가 존재하는지 확인 → 사용자가 입력한 이름을 기반으로 새 경로 생성
- os.rename()을 사용해 파일 이름 변경
- 이름이 비어있거나 os.rename()중 에러 발생 시 → 상태로그 기록
## 📌 convert_video_to_jpg(self)
```python
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

    self.status_lab.append(f"프레임 추출 시작: {filepath}, {frame_interval}초 간격")
    self.progressBar.setValue(0)

    try:
        video_path = os.path.join(base_dir, filepath)
        video = cv2.VideoCapture(video_path)

        if not video.isOpened():
            self.status_lab.append(f"파일 열기 실패: {filepath}")
            return

        fps = video.get(cv2.CAP_PROP_FPS)
        video_name = os.path.splitext(os.path.basename(filepath))[0]
        save_dir = os.path.join(base_dir, video_name)
        os.makedirs(save_dir, exist_ok=True)

        count = 0
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
        self.status_lab.append(f"변환 실패: {str(e)}")
```
- 사용자 입력으로부터 파일명, 프레임 간격 확인 → OpenCV로 영상 로드 → FPS 기준 프레임 간격 계산
- 지정된 프레임마다 이미지를 저장함.
- 영상파일명/ 폴더 내에 frameX.jpg 형식으로 저장 및 상태로그에도 기록
- 존재하지 않는 파일, 잘못된 프레임 간격에 대한 안내 → 상태로그 기록
## 📌 clear_log(self)
```python
def clear_log(self):
    self.status_lab.clear()
    self.progressBar.setValue(0)
    self.download_lab.setText("")
    self.chname_lab.setText("")
    self.tojpg_lab.setText("")
```
