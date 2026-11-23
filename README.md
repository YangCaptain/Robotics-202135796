# Robotics-202135796

가천대학교 **로봇 자율주행: High-Level 의사결정과 Low-Level 제어** 실습 저장소

- 이름: 양다빈
- 학번: 202135796
- 기간: 2026.11.14 ~ 2026.12.13

## 실습 목록

| 날짜 | 폴더 | 주제 | 플랫폼 |
|---|---|---|---|
| 11/14 (토) | [`261114`](./261114) | 개발 환경, Linux CLI, 임베디드 기초, LED 디지털 출력 | Tinkercad (Arduino Uno) |
| 11/15 (일) | [`261115`](./261115) | 버튼 입력, ADC·PWM, 부저, 서보모터 제어 | Tinkercad (Uno) / ESP32 |
| 11/21 (토) | [`261121`](./261121) | UART·I2C 통신, IMU·LiDAR 센서, ROS2 기초 (Pub/Sub) | ESP32 / ROS2 Jazzy |
| 11/22 (일) | [`261122`](./261122) | 노드 체이닝, Launch 파일, 서비스·커스텀 인터페이스 | ROS2 Jazzy |

## 저장소 구조

```
Robotics-202135796/
├── README.md          # 저장소 소개 (이 파일)
├── 261114/            # 개발 환경, 임베디드 기초
├── 261115/            # 센서·액추에이터 제어
├── 261121/            # 센서 통신, ROS2 기초
│   ├── Arduino/       # IMU, LiDAR, 모터 테스트 코드
│   └── 1_pubsub/      # ROS2 talker / listener 패키지
└── 261122/            # ROS2 서비스
    ├── custom_interfaces/   # 커스텀 msg / srv 정의
    └── 2_srvmsg/            # 서비스 서버 / 클라이언트 패키지
```

각 폴더의 README에 이론적 배경, 핵심 기술, 실험 과정, 결과 분석, 실행 방법을 정리했습니다.

## 개발 환경

- Ubuntu 24.04, ROS2 Jazzy
- Arduino IDE 2.x + esp32 by Espressif 보드 패키지
- 보드: ESP32 (D1 R32), Arduino Uno (Tinkercad 시뮬레이션)
