# 🎬 YoutubeDownload_VidBLUR

YouTube 영상 다운로드 및 얼굴 모자이크 기능을 제공하는 Python 기반의 GUI 애플리케이션 프로젝트입니다.  
본 프로젝트는 두 개의 주요 기능으로 구성되어 있으며, 각각 별도의 폴더에 모듈화되어 있습니다.

---

## 📁 폴더 구성

| 폴더명 | 설명 |
|--------|------|
| [`youtubedownloader`](./youtubedownloader) | YouTube 영상 다운로드, 파일 이름 변경, 프레임 이미지 추출 기능 포함 |
| [`Video_blur`](./Video_blur) | 영상에서 얼굴 인식 후 자동 블러 처리 기능 포함 |

---

## ✅ 주요 기능

- 🔽 YouTube 영상 다운로드 (`pytubefix`)
- ✏️ 영상 파일 이름 변경
- 🖼️ 영상 → 프레임 이미지(JPG)로 변환
- 🖥️ PySide6 / PyQt5 기반 GUI 제공
- 🔍 Haar CasCade 모델을 활용한 얼굴인식
- 🧠 얼굴 자동 감지 후 모자이크 처리 (`OpenCV`)

---

## 📖 자세한 설명

각 기능별 세부 구현 및 사용법은 아래 폴더의 `README.md`를 참고해 주세요:

- ▶️ [`youtubedownloader/README.md`](./youtubedownloader/README.md)
- 🔲 [`Video_blur/README.md`](./VidBLUR/README.md)

---

## 📦 설치 및 실행

> 각 기능 폴더별로 독립 실행이 가능하도록 구성되어 있으며, 필요한 모듈과 실행 방법은 각 폴더 내 `README`에 안내되어 있습니다.
