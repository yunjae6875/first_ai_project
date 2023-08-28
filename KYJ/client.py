"""
- mainClass: 메인 윈도우 클래스
- joinClass: 회원가입 다이얼로그

최초 작성: 2023-08-27 18:45
최종 수정: 2023-08-28 23:51
"""

import sys
import os
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimediaWidgets import *
from _ui.ui_main_form import Ui_mainForm
from _ui.ui_join_form import Ui_joinForm
from ultralytics import YOLO
from PIL import Image
from glob import glob
from time import sleep
from PIL.ImageFont import *
from PIL.Image import *
from PIL.ImageDraw import *
import cv2
import easyocr
import threading
import matplotlib.pyplot as plt
import warnings
import random
import numpy as np

warnings.filterwarnings('ignore')  # 불필요한 경고문 제거

class mainClass(QMainWindow, Ui_mainForm):
    """
    메인 윈도우 클래스
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # UI 초기화
        self.initUi()  # UI 요소 초기화
        self.initSignal()  # 버튼 및 시그널 연결 초기화
        self.initFunc()  # 기능 연결 초기화

    def initUi(self):
        """
        GUI 스타일시트의 초기화를 담당합니다.
        """
        self.stackedWidget.setCurrentIndex(0)  # 메인 페이지 0번 인덱스 고정
        self.setWindowFlags(Qt.FramelessWindowHint)  # 창 테두리 제거
        self.icon_title_img.setIcon((QIcon('./_icons/cam_icon_white.png')))
        self.icon_open_id.setIcon((QIcon('./_icons/person_icon.png')))
        self.icon_open_pw.setIcon((QIcon('./_icons/lock_icon.png')))
        self.lb_main_title_background.setPixmap(QPixmap('./_icons/main_title.png'))
        self.lb_main_img.setPixmap(QPixmap('./_icons/play_button_img.png'))
        self.lb_plate_img.setPixmap((QPixmap('./_icons/plate_img.png')))
        self.icon_top_img.setIcon((QIcon('./_icons/cam_icon_white.png')))

    def initSignal(self):
        """
        버튼 및 시그널 연결의 초기화를 담당합니다.
        """
        self.btn_open_login.clicked.connect(lambda: print(">> stackedWidget: index 1") or self.stackedWidget.setCurrentIndex(1))
        self.btn_main1_close.clicked.connect(lambda: print(">> main window close") or sys.exit())
        self.btn_main2_close.clicked.connect(lambda: print(">> main window close") or sys.exit())
        self.btn_open_signup.clicked.connect(self.signup_show_event)
        self.btn_video_connect.clicked.connect(self.start_video_processing)
        self.btn_video_disconnect.clicked.connect(self.stop_video_event)

    def initFunc(self):
        """
        메소드의 초기화를 담당합니다.
        """
        pass

    def signup_show_event(self):
        """
        회원가입 다이얼로그를 열어주는 메소드
        """
        self.join_dialog = joinClass()
        self.join_dialog.show()

    def start_video_processing(self):
        """
        비디오 처리 시작 메소드
        """
        # 비디오 파일과 모델 경로를 설정하고 YOLOVideoClass 인스턴스 생성
        print(">> 재생 버튼 클릭")
        video_path = r'seoul_drive.mp4'
        model_path = r'best.pt'
        self.video_processor = YOLOVideoClass(model_path, video_path)
        self.video_processor.process_video(self.update_display)

    def update_display(self, frame):
        """
        프레임을 Qt 이미지로 변환하고 화면에 업데이트 하는 메소드
        """
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        qt_pixmap = QPixmap.fromImage(qt_image)
        self.lb_main_img.setPixmap(qt_pixmap)

    def stop_video_event(self):
        """
        비디오 처리 중단 메소드
        """
        self.video_processor.stop()
        self.lb_main_img.setPixmap(QPixmap('./_icons/play_button_img.png'))

class YOLOVideoClass:
    """
    YOLO 객체 감지 모델을 사용하여 비디오 처리하는 클래스
    """
    def __init__(self, model_path, video_path):
        self.model = YOLO(model_path)
        self.cap = cv2.VideoCapture(video_path)
        self.keep_processing = True

    def init_display_window(self):
        """
        디스플레이 창 초기화
        """
        cv2.namedWindow("Model View", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Model View", 700, 400)

    def process_video(self, callback):
        """
        비디오 처리 함수
        """
        while self.cap.isOpened() and self.keep_processing:
            # 비디오 캡쳐 객체가 열려 있고 처리를 계속 해야 하는 동안 반복
            success, frame = self.cap.read()  # 다음 프레임 읽기
            if success:
                # 프레임 읽기에 성공했을 때
                results = self.model(frame)  # YOLO 모델을 사용하여 프레임 내 객체 감지
                # print(results[0].boxes)  # 감ㅈ된 객체의 경계 상자 좌표 출력
                annotated_frame = results[0].plot()  # 객체 감지 결과를 프레임에 표시한 이미지 생성
                annotated_frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)  # 이미지 색상 공간 변환
                callback(annotated_frame_rgb)  # 콜백 함수 호출하여 프레임 업데이트 및 표시

                key = cv2.waitKey(1)  # 키 입력 대기 (1ms)
                if key == ord("q"):
                    break  # 'q' 키를 누르면 처리 중단
            else:
                break

    def release_resources(self):
        """
        캡쳐 및 창 리소스 해제 메소드
        """
        self.cap.release()
        cv2.destroyAllWindows()

    def stop(self):
        """
        비디오 처리 중단 메소드
        """
        self.keep_processing = False
        self.release_resources()


class TextDetectionVisualizer:
    def __init__(self, languages=['ko'], gpu=True, target_height=600, target_width=600):
        self.reader = easyocr.Reader(languages, gpu=gpu)  # 지정된 언어와 GPU 사용 옵션으로 EasyOCR Reader를 초기화
        self.target_height = target_height  # 출력 이미지의 원하는 높이
        self.target_width = target_width  # 출력 이미지의 원하는 너비

    def enhance_image(self, image):
        """
        입력 이미지를 가우시안 블러를 사용하여 개선하는 메서드를 정의
        """
        blurred = cv2.GaussianBlur(image, (0, 0), 3)  # 가우시안 블러 적용
        enhanced = cv2.addWeighted(image, 1.5, blurred, -0.5, 0)  # 이미지 개선
        return enhanced

    def add_padding(self, image):
        """
        입력 이미지에 패딩을 추가하여 목표 차원과 일치하도록 하는 메서드를 정의
        """
        # 각 면에 대한 패딩 양을 계산
        if image.shape[0] < self.target_height or image.shape[1] < self.target_width:
            top_padding = max((self.target_height - image.shape[0]) // 2, 0)
            bottom_padding = max(self.target_height - image.shape[0] - top_padding, 0)
            left_padding = max((self.target_width - image.shape[1]) // 2, 0)
            right_padding = max(self.target_width - image.shape[1] - left_padding, 0)
            # 패딩을 추가하여 이미지를 생성
            padded_image = cv2.copyMakeBorder(image, top_padding, bottom_padding, left_padding, right_padding, cv2.BORDER_CONSTANT)
            return padded_image
        else:
            return image

    def visualize_text_detection(self, image_path):
        """
        입력 이미지에서 텍스트 탐지를 시각화하는 메서드를 정의합니다.
        """
        # OpenCV를 사용하여 입력 이미지를 읽음
        img = cv2.imread(image_path)
        enhanced_img = self.enhance_image(img)  # 이미지 개선
        padded_img = self.add_padding(enhanced_img)  # 목표 차원에 맞게 패딩 추가

        # 패딩된 이미지에서 텍스트 인식을 수행
        result = self.reader.readtext(padded_img)

        # 각 인식된 텍스트 영역에 대해 세부 정보를 출력
        for (bbox, text, prob) in result:
            print(f">> Bounding Box: {bbox} / Text: {text} / Probability: {prob * 100}")

        img_pil = Image.fromarray(padded_img)  # 이미지를 PIL 형식으로 변환
        font = ImageFont.truetype('Pretendard-Medium.ttf', 60)  # 텍스트 렌더링을 위한 폰트 로드
        draw = ImageDraw.Draw(img_pil)  # 이미지에 그리기 객체 생성

        np.random.seed(42)
        COLORS = np.random.randint(0, 255, size=(255, 3), dtype="uint8")  # 랜덤한 색상 생성

        # 각 인식된 텍스트 영역에 대해 경계 상자와 텍스트를 이미지에 그림
        for i in result:
            x = i[0][0][0]  # 경계 상자의 좌상단 x 좌표
            y = i[0][0][1]  # 경계 상자의 좌상단 y 좌표
            w = i[0][1][0] - i[0][0][0]  # 경계 상자의 너비
            h = i[0][2][1] - i[0][1][1]  # 경계 상자의 높이

            color_idx = random.randint(0, 255)  # 랜덤한 색상 인덱스 선택
            color = tuple([int(c) for c in COLORS[color_idx]])  # 색상 값을 튜플로 변환

            # 인식된 텍스트 영역 주위에 사각형 그리기
            draw.rectangle(((x, y), (x + w, y + h)), outline=color, width=2)
            # 사각형 위에 인식된 텍스트 그리기
            draw.text((int((x + x + w) / 2), y - 2), str(i[1]), font=font, fill=color)

        # 최종 이미지를 matplotlib을 사용하여 표시
        plt.figure(figsize=(10, 10))
        plt.imshow(img_pil)
        plt.axis('off')
        plt.show()




class joinClass(QDialog, Ui_joinForm):
    """
    회원가입 다이얼로그 클래스
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def initUi(self):
        pass

    def initSignal(self):
        pass

    def initFunc(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fontDB = QFontDatabase()
    fontDB.addApplicationFont('./_font/Pretendard-Medium.ttf') # 폰트 지정
    app.setFont(QFont('Pretendard Medium'))
    run = mainClass()
    run.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("Closing Window...")