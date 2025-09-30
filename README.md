##   분류 및 입출고 자동화 시스템
- 두산 로보틱스 협동 로봇과 레고 블록을 활용한 물류 입출고 자동화 시스템 구현   
<img src="https://github.com/daeyeong-choi/WMS/blob/main/images/workspace.png" width="600" />

🔗 출처 및 라이선스

이 프로젝트는 **두산로보틱스(Doosan Robotics Inc.)**에서 배포한 ROS 2 패키지를 기반으로 합니다.
해당 소스코드는 BSD 3-Clause License에 따라 공개되어 있으며,
본 저장소 또한 동일한 라이선스를 따릅니다. 자세한 내용은 LICENSE 파일을 참고하시기 바랍니다.

    ⚠️ 본 저장소는 두산로보틱스의 공식 저장소가 아니며, 비공식적으로 일부 수정 및 구성을 포함하고 있습니다.
    공식 자료는 두산로보틱스 공식 홈페이지를 참고해 주세요.
    github (https://github.com/DoosanRobotics/doosan-robot2)

## 개발 기간 및 개발 인원
-2025.05.09~2025.05.22
|  | 역할 | 담당 업무|
| --- | --- | --- |
| 최대영 | 팀장 | 전반적인 코드 작성 및 총괄 |
| 장** | 팀원 | 분류 코드 작성 및 영상 제작 |
| 유** | 팀원 | 분류 및 재고 코드 작성 및 검토 |
| 김**| 팀원 | 분류 코드 및 보고서 작성 |
  
## 개발 환경 및 장비

### **Development Environment**

![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white)


### **Robotics**
![ROS](https://img.shields.io/badge/ros-%230A0FF9.svg?style=for-the-badge&logo=ros&logoColor=white)   

### **Programming Languages**
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

### 하드웨어 구성
#### **Robot**
- Doosan Robotics m0609, OnRobot RG2 Gripper

<p align="left">
  <img src="https://github.com/daeyeong-choi/WMS/blob/main/images/Doosan-Robotics-M0609-Cobot.png" width="300" />
  <img src="https://github.com/daeyeong-choi/WMS/blob/main/images/rg2.png" width="50" />
</p>

### 로봇 제어 시스템
- rclpy 기반 ROS2 제어 패키지 구성
- Doosan ROS2 API 사용

## 동작 환경 가정
- 생산 라인과 재고 창고 통합한 Workspace modeling
- 컨베이어 벨트 위로 랜덤으로 크기가 다른 제품 이동
- 분류 → 입고 → 출고 순으로 수행 (적재 장소에 1개 재고 있다고 가정)
<p align="left">
  <img src="https://github.com/daeyeong-choi/WMS/blob/main/images/workspace.png" width="470" />
  <img src="https://github.com/daeyeong-choi/WMS/blob/main/images/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202025-09-04%2017-51-18.png" width="400" />
</p>

## 기능   

1. 5가지 종류의 레고블록 분류 후 적재
2. 원하는 블록 출고
3. 재고 확인

## 동작 흐름

1. 모드 선택(1.분류 및 입고, 2.출고, 3.재고 확인)
2. 1번 선택 시 블록 자동 분류하여 각 위치에 적재
3. 2번 선택 시 선택한 블록 출고 위치로 이동
4. 3번 선택 시 선택한 블록 개수 확인
5. 각 동작 종료 후 또는 종료 번호 터미널 입력 시 대기 상태

- 전체 동작 흐름
<img src="https://github.com/daeyeong-choi/Warehouse-Management-System-with-co-robot/blob/main/images/flow1.png" width="500" />

- 분류 동작 흐름 
<img src="https://github.com/daeyeong-choi/Warehouse-Management-System-with-co-robot/blob/main/images/flow2.png" width="500" />

- 너비 측정 시퀸스
<img src="https://github.com/daeyeong-choi/Warehouse-Management-System-with-co-robot/blob/main/images/flow3.png" width="500" />

## 주요 코드

- 두산 로보틱스 배포
![코드 베이스](https://github.com/DoosanRobotics/doosan-robot2)

1. **블록별 객체 생성**  
   생성 시 필요한 정보:
   - 블록 이름
   - 창고 이름
   - 블록을 쌓을 위치
   - 쌓기 전 이동할 위치
   - 쌓은 후 이동할 위치
   - 초기 재고 수량
   - 블록을 빼낼 위치

2. **블록 분류 및 동작 수행**  
   - 블록을 분류하거나 사용자가 입력한 블록 모양에 따라  
     해당 위치에서 블록을 쌓거나 이동하는 동작.

- 분류 및 입고 코드 및 동작 사진
<img src="https://github.com/daeyeong-choi/WMS/blob/main/images/inbound_code.png" width="600" />
<img src="https://github.com/daeyeong-choi/WMS/blob/main/images/inbound_code2.png" width="600" />

```python
def __move_to_pos_stack(self, target_pos, target_pos_up):

        z1=posx(661.400, -48.260,70.550, 126.42, 179.69, 35.9)# 높이 측정하려 내려갈 위치
        print("moving to target_pos_up")
        movel(target_pos_up, vel=VELOCITY, acc=ACC, mod=0)
        print("target_pos_up:", target_pos_up)
        mwait()

        if self.stock == 1:
            print("moving to target_pos")
            movel(target_pos[0], vel=VELOCITY, acc=ACC, mod=0)
            print("target_pos:", target_pos[0])
            mwait()

        elif self.stock ==2:
            print("moving to target_pos")
            movel(target_pos[1], vel=VELOCITY, acc=ACC, mod=0)
            print("target_pos:", target_pos[1])
            mwait()

        ##########################################################힘제어
        time.sleep(0.5)
        task_compliance_ctrl(stx=[500, 500, 500, 100, 100, 100])
        time.sleep(1)
        set_desired_force(fd=[0, 0, -15, 0, 0, 0], dir=[0, 0, 1, 0, 0, 0], mod=DR_FC_MOD_REL)
        time.sleep(1)
        force_condition = check_force_condition(DR_AXIS_Z, max=15)
        time.sleep(1)

        print("force_condition Start : ", force_condition)
        while (force_condition > -1):
            force_condition = check_force_condition(DR_AXIS_Z, max=15)
            time.sleep(2)
        time.sleep(1)
        release_force()
        release_compliance_ctrl()
        release()
        ###########################################################
        movel(target_pos_up, vel=VELOCITY, acc=ACC, mod=0)
        movel(z1, vel=VELOCITY, acc=ACC)

def stack(self):
    if not self.position:
        print("No position set for stacking.")
        return
    self.__move_to_pos_stack(self.position, self.position_up)
    self.stacked=True
    self.set_stock(self.stock + 1)
    print(f'stock: {self.stock}')
```

- 출고 코드 및 동작 사진
<img src="https://github.com/daeyeong-choi/WMS/blob/main/images/outbound_code.png" width="600" />

```python
def __move_to_pos_unstack(self, target_pos, target_pos_up, unstack_pos_list):
        p_out=posx(647.28, 198.80, 51.03, 4.75, -178.89, -84.33)
        p_out_up=posx(647.28, 198.80, 120.03, 4.75, -178.89, -84.33)
        release()
        print("moving to target_pos_up")
        movel(target_pos_up, vel=VELOCITY, acc=ACC, mod=0)
        print("target_pos_up:", target_pos_up)
        mwait()


        if self.stock == 2:
            print("moving to grip")
            movel(unstack_pos_list[1][0], vel=VELOCITY, acc=ACC, mod=0)
            grip()
            wait(1)
            movel(unstack_pos_list[1][1], vel=VELOCITY, acc=ACC, mod=0)
            movel(unstack_pos_list[1][2], vel=VELOCITY, acc=ACC, mod=0)
             
        elif self.stock ==3:
            print("moving to grip")
            movel(unstack_pos_list[0][0], vel=VELOCITY, acc=ACC, mod=0)
            grip()
            wait(1)
            movel(unstack_pos_list[0][1], vel=VELOCITY, acc=ACC, mod=0)
            movel(unstack_pos_list[0][2], vel=VELOCITY, acc=ACC, mod=0)

        movel(target_pos_up, vel=VELOCITY, acc=ACC, mod=0)
        movel(p_out_up, vel=VELOCITY, acc=ACC)
        movel(p_out, vel=VELOCITY, acc=ACC)
        release()

def unstack(self):
    if self.stock <= 0:
        print(f"Box {self.id} is out of stock!")
        return
    
    print(f'stock: {self.stock}')
    self.__move_to_pos_unstack(self.position, self.position_up, self.unstack_pos_list)
    self.set_stock = self.stock - 1
    print(f'stock: {self.stock}')
```

- 재고 체크 코드 및 사진

```python
def info(self):
    return f"id : {self.id}\nstock : {self.stock}\nposition : {self.pos_id}\n=====\n"
~~~
elif mode_select == 3:
    while True:
        movej(HOME_READY, vel=VELOCITY, acc=ACC)
        select_wh = int(input('select_wh_number :'))

        if select_wh == 1:  # small sq
            print(aa.info())
        elif select_wh == 2:  # medium sq
            print(bb.info())
        elif select_wh == 3:  # large sq
            print(cc.info())
        elif select_wh == 4:  # round sq
            print(dd.info())
        elif select_wh == 5:  # high sq
            print(ee.info())
        elif select_wh == 6:  # change to mode_select
            break
        else:
            print('wrong number!')
```
<img src="https://github.com/daeyeong-choi/WMS/blob/main/images/check.png" width="600" />

## Demo video link
[![YouTube](https://img.shields.io/badge/YouTube-FF0000?logo=youtube&logoColor=white)](https://youtube.com/shorts/2GCx_hT8v0I?feature=share)

