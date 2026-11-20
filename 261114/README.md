# Lab #1 (2026.11.14) — 개발 환경, Linux CLI, 임베디드 기초

## 1. 개요
Tinkercad에서 Arduino Uno로 LED를 1초 간격으로 깜빡이는 디지털 출력 실습을 진행했다.

## 2. 이론적 배경
로봇 구동 시스템
High-Level : SBC/ROS2 --- Low level : MC/RTOS

로봇 구동 시스템의 구성 :
- 로봇 주행은 단순한 모터 제어만으로 이루어 지지 않음
- 센서 데이터 처리, 위치추정,경로 계획, 모터제어가 동시에 수행됨
- (중요) 각 기능은 요구되는 연산량과 제어 주기가 다름
- 따라서 로봇 시스템은 일반적으로 High-level/Low-level로 역할을 분리
1. high-level : 복잡한 연산과 로봇의 판단,명령을 담당
2. Low-level: 실제 하드웨어를 빠르고 일정한 주기로 제어
(완벽한 제어주기를 가져야함)

High-Level Decision-Making

센서 데이터 처리 및 주변 환경 인식

Localization/Mapping/SLAM

Path Planning 및 Navigation

카메라 LiDAR

로봇 구동 시스템

High-Level 하드웨어(SBC)

Low-Level Control:

- 모터 PWM 출ㄹ력
- Encoder 데이터 처리
- PID Control
- 각종 센서 데이터 수집 및 전처리(IMU,Ultrasonic)
- GPIO,ADC/DAC/UART/I2C,SPI 등 직접적인 하드웨어 제어)
- 짧고 일정한 주기의 제어 수행

Low-Level 하드웨어 ( MCU) 마이크로 컨트롤러 유닛 :  저수준의 계산

- r32
- openCR

High-level/lowlevel 분리 이유

- 높은 레벨은 많은 연산량이 필요
- 로우 레벨은 빠르고 일정한 제어 주기가 중요
- SBC에서는 여러 프로세스가 동시에 실행되어 제어 주기가 변할 수 있음
- SBC는  리눅스 기반으로 다양한 소프트 웨어및 고성능 연산 환경을 제공
- MCU+ RTOS는 모터 제어와 같은 주기적 작업을 안정적으로 수행 가능
- 역할을 분리하면 각 하드웨어의 장점을 활용 할수있음

|  | 고수준 | 저수준 |
| --- | --- | --- |
| 주요 역할 | 판단/계획 | 직접 제어 |
| 연산량 | 높음 | 상대적 낮음 |
| 중요요소 | 처리 성능 | 실시간성 |
| 하드웨어 | SBC | MCU |
| OS | 리눅스 | RTOS |
| 소프트웨어 | ROS2 | Firmware/micro-ROS |
| 주요 개발 언어 | 파이썬/c++ | c/c++ |

Linux

- 높은 개발 자유도
    - 오픈 소스 기반으로 시스템 내부 구조 및 커널 수준까지 수정 가능
- 강력한 패키지 관리
    - 소프트웨어 설치, 의존성 관리 및 업데이트 용이
- ROS2 중심의 개발 생태계
    - 주요 로봇 소프트 웨어, 라이브러리 및 개발 문서가 Ubuntu 환경을 중심으로 제공
- 광범위한 활용 분야
    - 서버,클라우드,임베디드 시스템 등 현대 IT 인프라 전반을 뒷받침하는 핵심 운영 체제

Linux CLI

GUI vs CLI

CLI란 사용자가 명령어를 입력하여 컴퓨터와 상호작용하는 방식

GUI :  아이콘, 창, 마우스로 조작

CLI: 명령어 입력으로 조작

gui로 할수없는게 너무 많음

user_name: 현재 로그인한 사용자 이름

host_name: 현재 접속한 컴퓨터 이름

home directory : ~ 

~ = $HOME = /home/user

@ : 사용자와 컴퓨터를 구분하는 표시

~: 사용자의 home 디렉토리

/: 폴더와 폴더를 구분하는 표시

parent_directory: 상위 디렉토리

current_directory: 현재 디렉토리

/folder1/folder2 → 상대경로 (이거 잘모르겠음)

pwd : 지금 내 경로

cd .. 전으로

ls : list

ls-a : 숨김파일까지 보여주기

mkdir : make directory

mkdir -p adw/dwad/dwa/dwdwa/dw 이렇게 만들수있음4

touch : py 파일 만들기

cp : copy

rm 삭제

chmod +x test.py

실행권한

ssh 

echo : 내가 적은거 다시 한번 적어줌

echo hello > test.txt 앞에 있었던거 삭제하고 덮어씌움

echo hello >>  test.txt  전에거 기억하고 밑에 적음

ping  :인터넷 연결

sudo : 관리자 권한으로 실행하겠다

apt : 강력한 패키지 관리

sudo apt update : 새로운 버전 업그레이드 할

sudo apt upgrade : 새로운 버전이 나와서 업그레이드 하는것 

임베디드 시스템(삽입되어있는 시스템)

- 특정 기능을 수행하도록 설계된 시스템
- MCU 기반으로 동작
- 센서 및 액추에이터와 직접 연결하여 물리적 화너경과 상호작용
- 자동차 제어 시스템, 산업용 로봇,IoT 디바이스,의료기기 등에 활용
- 주요특징
    - 낮은 연산량과 제한된 컴퓨팅 자원
    - 실시간 처리 및 제어에 적합

## 3. 핵심 기술
- `pinMode(pin, OUTPUT)`으로 GPIO를 출력 모드로 설정
- `digitalWrite(HIGH/LOW)` + `delay()`로 주기적인 ON/OFF 제어

## 4. 실험 과정
<!-- 직접 작성: 회로 구성 순서, 시행착오 -->

## 5. 결과 및 분석
![LED 회로](./ledPin)
<!-- 결과 / 잘 안 된 점과 원인 / 보완할 점 -->

## 6. 파일 구조
```
261114/
├── README.md
├── ledPincode.txt   # LED 1초 간격 점멸 코드 (Arduino Uno)
└── ledPin           # Tinkercad 회로 스크린샷 (PNG)
```

## 7. 실행 방법
### 의존성
- Tinkercad Circuits (웹, 별도 설치 없음) 또는 Arduino IDE 2.x
- 보드: Arduino Uno R3, 추가 라이브러리 없음

### 배선
| 부품 | 연결 |
|---|---|
| LED (+, 긴 다리) | D7 ← 220Ω 저항 |
| LED (−, 짧은 다리) | GND |

### 실행
1. Tinkercad에서 위 표대로 회로 구성
2. Code 탭 → Text 모드 → `ledPincode.txt` 내용 붙여넣기
3. Start Simulation → LED가 1초 간격으로 점멸하는지 확인
