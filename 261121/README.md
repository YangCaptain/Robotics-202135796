(2026.11.21) — 센서 통신(UART·I2C), IMU·LiDAR, ROS2 기초
1. 개요

ESP32(D1 R32)에 IMU(MPU6050)와 LiDAR를 연결해 각각 I2C와 UART로 센서 값을 읽고, ROS2의 기본 구조(노드·토픽·Publisher/Subscriber)를 turtlesim과 talker/listener 예제로 실습했다.

2. 이론적 배경
2.1 IMU (Inertial Measurement Unit, 관성 측정 장치)

여러 센서를 묶은 장치라서 "Unit"이라고 부른다.

센서	측정값	비고
Gyroscope	각속도 (회전 속도, °/s)	정지 상태에서도 0이 아닌 값 → 바이어스(편향) 존재
Accelerometer	가속도 (m/s²)	정지 상태에서 z축 ≈ −9.8 (중력가속도)
Magnetometer	지자기 (북쪽 기준 방향)	주변 전자기기 자기장에 취약 → 이번 실습에서는 제외
바이어스 보정: 정지 상태에서 약 1,000개 샘플을 평균 내어 오프셋을 구하고 측정값에서 빼준다.
가속도를 활용할 때는 z축에 항상 중력(−9.8 m/s²)이 포함된다는 점을 고려해야 한다.
2.2 통신 프로토콜: 동기 vs 비동기

통신 프로토콜 = 두 장치(MCU↔MCU, MCU↔센서)가 0과 1을 주고받기 위한 약속. 실제로는 전압 HIGH(1) / LOW(0) 를 바꿔가며 데이터를 전송한다.

구분	동기 (Synchronous)	비동기 (Asynchronous)
기준	공유 클럭 신호에 맞춰 송수신	클럭 없이 송신
핵심	타이밍	버퍼 관리 + 약속된 전송 속도(baud rate)
비유	단체 줄넘기에 같이 들어가 리듬에 맞춰 대화	데이터를 던져두고 가면 수신 측 버퍼에 쌓임
예	I2C, SPI	UART
2.3 UART (Universal Asynchronous Receiver/Transmitter)
비동기 직렬 통신, 가장 간단하고 범용적. 1:1 통신
TX(송신) ↔ 상대 RX(수신) 교차 연결
클럭이 없으므로 양쪽이 같은 baud rate를 미리 약속해야 한다 (baud rate 개념은 261115 참고)
프레임 구조: 평소 HIGH(idle) → Start bit(LOW) → Data 8bit (LSB → MSB 순) → (Parity) → Stop bit(HIGH)
예: 'A' = 0x41 = 0100 0001 → LSB부터 1000 0010 순서로 전송
8N1: Data 8bit, Parity 없음(None), Stop bit 1개 — 가장 많이 쓰는 설정
Parity bit: 1의 개수를 짝수/홀수로 맞추는 오류 검출용 비트 (잘 쓰지 않음)
단점: TX/RX 한 쌍당 장치 하나 → 센서가 많아지면 핀이 부족
2.4 I2C (Inter-Integrated Circuit)
동기식 직렬 통신, 신호선 SDA(데이터) + SCL(클럭) 2개만으로 여러 장치를 병렬 연결
Master–Slave(Controller–Target) 구조: Master(MCU)가 클럭을 만들고, 통신할 Slave를 주소로 선택
두 선 모두 풀업 저항으로 평소 HIGH 유지
통신 순서
Start condition: SCL이 HIGH일 때 SDA가 HIGH→LOW (falling edge)
Slave 주소 7bit + R/W 1bit = 1byte 전송 → 모든 Slave가 듣고 자기 주소면 응답
ACK/NACK: 해당 Slave가 SDA를 LOW로 끌어내리면 ACK("나 여기 있어"), 반응 없으면 NACK
Data 1byte 전송 → ACK (SCL rising edge에서 데이터를 읽고, HIGH 동안 값이 유지되어야 함)
Stop condition: SCL이 HIGH일 때 SDA가 LOW→HIGH (rising edge)
2.5 MPU6050 읽기 (I2C 적용)
ESP32 I2C 핀: SDA = GPIO21, SCL = GPIO22 (핀아웃 참고), 주소 0x68
MPU6050은 Sleep 상태로 시작 → PWR_MGMT_1(0x6B) 레지스터에 0x00을 써서 깨움 (setup에서 1회)
0x3B 레지스터부터 14byte 요청: 가속도 6 + 온도 2 + 자이로 6
각 축 값은 2byte → (high << 8) | low 로 16bit 정수 복원 (비트 시프트 + OR)
2.6 LiDAR 데이터 읽기 (UART 적용)
회전하며 레이저로 360° 거리를 측정. 데이터를 47byte 패킷 단위로 UART 전송 → MCU는 버퍼에서 읽음
패킷 구조: Header(0x54) · VerLen(0x2C) · 회전 속도 · 시작 각도 · 측정점 12개 × (거리 2byte + 신뢰도 1byte) · 끝 각도 · Timestamp · CRC
첫 두 byte(0x54, 0x2C)로 패킷 시작을 검증
각도는 소수점 없이 ×100 한 정수로 전송 → ÷100 해서 실제 각도로 복원
다중 byte 값은 Low byte 먼저 전송 → low | (high << 8)
ESP32는 UART가 여러 개 → Serial(PC 모니터, 115200)과 Serial2(LiDAR, 230400, 8N1, RX=GPIO16)를 분리 사용
장착 방향에 따라 0°/90°/180°/270°가 로봇의 앞·좌·뒤·우 중 어디인지 정해짐
2.7 ROS2 기초
Node: 하나의 기능을 수행하는 실행 단위 (클래스 하나 = 노드 하나)
Topic: 노드 간 데이터 통로. Publisher가 발행하면 같은 토픽을 Subscriber가 받는 일방향·비동기 통신
Message: 토픽에 실리는 데이터 타입 (예: std_msgs/String). String()으로 객체를 생성한 뒤 .data에 값을 넣어 publish
Timer: create_timer(주기, 콜백) → 주기마다 콜백 실행 (talker는 1초마다 발행)
Callback: Subscriber가 메시지를 받을 때 자동 호출되는 함수
QoS depth (10): 처리 못 한 메시지를 최대 몇 개까지 큐에 보관할지
워크스페이스 구조: colcon_ws/src/<패키지> — 패키지 생성은 src에서, 빌드는 워크스페이스 최상위에서 colcon build 후 source install/setup.bash
CLI 도구: ros2 topic list / echo / info, ros2 run, rqt_graph, turtlesim
geometry_msgs/Twist: 로봇 속도 명령 메시지. linear(x, y, z 직선 속도)와 angular(x, y, z 회전 속도) 두 개의 Vector3로 구성 → ros2 topic pub으로 코드 없이 터미널에서 직접 발행 가능
3. 핵심 기술
3.1 IMU 값 복원과 단위 변환 (imu_test.ino)
MPU6050 레지스터는 한 축 값을 High byte → Low byte 순으로 저장한다. (Wire.read() << 8) | Wire.read() 로 첫 byte를 8칸 왼쪽으로 밀고 두 번째 byte를 OR 해서 16bit 부호 있는 정수(int16_t) 로 합친다.
원시값(raw)을 물리 단위로 변환한다 (기본 측정 범위 기준).
가속도: raw / 16384.0 × 9.80665 → m/s² (±2g 범위, 1g = 16384)
자이로: raw / 131.0 → °/s (±250°/s 범위, 1°/s = 131)
14byte를 다 받지 못하면 MPU6050 read failed 로그를 남기고 이번 루프를 건너뛰어 잘못된 값 출력을 막는다.
3.2 LiDAR 패킷 파싱 (lidar_test.ino)
Serial2 버퍼에서 0x54 → 0x2C 두 byte가 연속으로 들어올 때만 패킷 시작으로 인정하고 나머지 45byte를 읽는다.
시작/끝 각도(0.01° 단위)를 ÷100 하고, 끝 각도가 360°를 넘어 0°로 돌아간 경우 +360°로 보정한다.
한 패킷의 12개 측정점은 시작~끝 각도를 11구간으로 균등 분할(선형 보간)해 각 점의 각도를 구한다.
각도를 반올림해 distances[360] 배열의 해당 칸에 거리(mm)를 저장하고, 거리 0은 무효값으로 버린다.
각도가 300° 이상에서 60° 미만으로 넘어가면 한 바퀴 완료로 판단해 0~359° 전체 거리를 출력한다.
3.3 ROS2 Publisher / Subscriber (talker.py, listener.py)
talker: create_timer(1.0, ...) 로 1초마다 콜백 실행 → String() 객체 생성 → msg.data = "Hello ROS2: {경과 초}" → /demo_topic 에 publish
listener: create_subscription(String, '/demo_topic', callback, 10) 으로 구독, 메시지가 들어올 때마다 콜백에서 로그 출력
setup.py 의 console_scripts 에 talker, listener 실행 이름을 등록해 ros2 run 1_pubsub <이름> 으로 실행
4. 실험 과정
로봇 조립 후 하드웨어 점검: motor_test, servo_test, buzzer_test 업로드로 각 부품 동작 확인
시리얼 포트 설정: dialout 그룹 권한 확인 → ESP32를 USB로 연결 → /dev/ttyUSB0 인식 확인
IMU 테스트: imu_test.ino 업로드 → 로봇을 정지 상태로 두고 시리얼 모니터(115200)로 가속도·자이로 값 확인
LiDAR 테스트: lidar_test.ino 업로드 → 0°/90°/180°/270° 방향 거리 값이 실제 장애물 위치와 맞는지 확인
ROS2 기초: turtlesim 실행 → ros2 topic list / info / echo 로 토픽 구조 확인 → ros2 topic pub 으로 Twist 메시지 직접 발행
패키지 작성: colcon_ws/src 에 1_pubsub 패키지 생성 → talker/listener 작성 및 setup.py 등록 → colcon build → source → 터미널 2개에서 실행
5. 결과 및 분석
turtlesim	talker / listener	topic echo
./turtlesim.png	./talkerlistener.png	./echo.png
Twist 메시지 발행 (ros2 topic pub)	topic info
./Geometry.png	./topicinfo.png
결과
IMU: 정지 상태에서 가속도 z축이 약 −9.8 m/s²(중력)로 측정되고, 자이로는 0 근처지만 완전히 0이 아닌 값(바이어스)이 나타났다.
LiDAR: 패킷 헤더 검증 후 0~359° 거리 배열이 한 바퀴마다 갱신·출력되는 것을 확인했다.
ROS2: talker가 1초마다 발행한 "Hello ROS2: n" 을 listener가 그대로 수신했고, ros2 topic echo 와 ros2 topic pub 으로 코드 없이 토픽을 확인·발행할 수 있었다.
잘 안 된 점과 원인
Arduino IDE의 Port 메뉴가 비활성화: dialout 권한은 있었으나 ESP32를 USB로 연결하지 않아 /dev/ttyUSB0 자체가 생성되지 않았다. → 보드 연결 후 해결. 포트 문제는 ① 물리 연결 ② 장치 인식(ls /dev/ttyUSB*, dmesg) ③ 권한(dialout) 순서로 확인해야 한다는 것을 알게 되었다.
no executable found: setup.py 의 console_scripts 에 실행 이름을 등록하지 않거나, 빌드 후 source install/setup.bash 를 하지 않으면 노드를 찾지 못한다.
보완할 점
자이로 바이어스를 시작 시 약 1,000개 샘플 평균으로 구해 빼 주는 보정 코드를 추가하면 회전 속도를 더 정확히 측정할 수 있다.
LiDAR는 장착 방향에 따라 0°가 로봇의 어느 쪽인지 달라지므로, 로봇 기준 앞/좌/뒤/우 각도를 미리 정해 두고 자율주행 코드에 반영해야 한다.
실험마다 시리얼 출력 화면(IMU, LiDAR)도 캡처해 두면 결과 비교가 쉬워진다.
6. 파일 구조
261121/
├── README.md
├── Arduino/
│   ├── imu_test.ino      # MPU6050 가속도·자이로 읽기 (I2C)
│   ├── lidar_test.ino    # LiDAR 47byte 패킷 파싱 (UART, Serial2)
│   ├── motor_test.ino    # 4륜 모터 구동 테스트
│   ├── servo_test.ino    # 로봇 조립 후 동작 확인용 (내용은 261115 실습과 동일)
│   └── buzzer_test.ino   # 로봇 조립 후 동작 확인용 (내용은 261115 실습과 동일)
├── 1_pubsub/             # ROS2 Python 패키지
│   ├── 1_pubsub/talker.py     # /demo_topic 에 1초마다 발행
│   ├── 1_pubsub/listener.py   # /demo_topic 구독 후 로그 출력
│   ├── setup.py
│   └── package.xml
├── ROS/1/setup.sample.py # 강사 제공 setup.py 샘플 (console_scripts 작성 참고용)
├── Latex/algorithm_template.tex  # 강사 제공 알고리즘 작성 템플릿
└── *.png                 # 실행 결과 스크린샷

Arduino/ 테스트 코드와 talker.py, listener.py는 수업 제공 예제를 그대로 실행한 것이다.

7. 실행 방법
의존성
Ubuntu 24.04 + ROS2 Jazzy
Arduino IDE 2.x + esp32 by Espressif 보드 패키지 (보드: ESP32 Dev Module)
시리얼 포트 권한: sudo usermod -a -G dialout $USER 후 재부팅
Arduino (IMU / LiDAR)
보드를 USB로 연결 → ls /dev/ttyUSB* 로 포트 확인
Arduino IDE에서 .ino 열기 → Board/Port 선택 → Upload
Serial Monitor 115200 baud
ROS2 talker / listener
bash
cp -r 1_pubsub ~/robot_navigation/colcon_ws/src/
cd ~/robot_navigation/colcon_ws
colcon build --packages-select 1_pubsub
source install/setup.bash
ros2 run 1_pubsub talker      # 터미널 1
ros2 run 1_pubsub listener    # 터미널 2
