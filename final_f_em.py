import rclpy
import DR_init

# for single robot
ROBOT_ID = "dsr01"
ROBOT_MODEL = "m0609"
VELOCITY, ACC = 200, 150
DR_init.__dsr__id = ROBOT_ID
DR_init.__dsr__model = ROBOT_MODEL

rclpy.init()
node = rclpy.create_node("rokey_stacking", namespace=ROBOT_ID)
DR_init.__dsr__node = node

ON, OFF = 1, 0
HOME_READY = [0, 0, 90, 0, 90, 0]

import time

try:
    from DSR_ROBOT2 import (
        get_digital_input,
        set_digital_output,
        get_current_posx,
        trans,
        set_tool,
        set_tcp,
        movej,
        movel,
        wait,
        mwait,
        task_compliance_ctrl,
        release_compliance_ctrl,
        set_desired_force,
        release_force,
        check_force_condition,
        DR_FC_MOD_REL,
        DR_AXIS_Z,
    )
    from DR_common2 import posx, posj
except ImportError as e:
    print(f"Error importing DSR_ROBOT2 : {e}")
    exit()

set_tool("Tool Weight_2FG")
set_tcp("2FG_TCP")


def release():
    set_digital_output(2, ON)
    set_digital_output(1, OFF)

def grip():
    set_digital_output(1, ON)
    set_digital_output(2, OFF)   


class Box:
    def __init__(self, id, pos_id, position, position_up, stock,unstack_pos_list):
        self.id = id
        self.pos_id = pos_id
        self.stock = stock
        self.position = position
        self.position_up = position_up
        self.unstack_pos_list = unstack_pos_list
        self.target_offset = 100
        self.stacked = stock > 0

    def set_pos_id(self, pos_id):
        self.pos_id = pos_id

    def set_box_id(self, id):
        self.id = id
    
    def set_position(self, pos):
        self.position = pos

    def set_position_up(self, pos_up):
        self.position_up = pos_up
    
    def set_stock(self, stock):
        self.stock = stock
    
    def info(self):
        return f"id : {self.id}\nstock : {self.stock}\nposition : {self.pos_id}\n=====\n"

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
    

    def stack(self):
        if not self.position:
            print("No position set for stacking.")
            return
        self.__move_to_pos_stack(self.position, self.position_up)
        self.stacked=True
        self.set_stock(self.stock + 1)
        print(f'stock: {self.stock}')

    def unstack(self):
        if self.stock <= 0:
            print(f"Box {self.id} is out of stock!")
            return
        
        print(f'stock: {self.stock}')
        self.__move_to_pos_unstack(self.position, self.position_up, self.unstack_pos_list)
        self.set_stock = self.stock - 1
        print(f'stock: {self.stock}')

def measure():
        a = get_digital_input(1)
        b = get_digital_input(2)
        print(a,b)
        return a, b


def main():
    # --초기 위치----초기 위치----초기 위치----초기 위치----초기 위치----초기 위치----초기 위치----초기 위치--
    z1=posx(661.400, -48.260,70.550, 126.42, 179.69, 35.9)# 높이 측정하려 내려갈 위치
    z1_up = posx(661.400, -48.260,150.550, 126.42, 179.69, 35.9)
    p1=posx(657.140, -32.270, 24.0, 167.81, 178.44, 77.45)# 세로 위치
    p_out=posx(647.28, 198.80, 44.03, 4.75, -178.89, -84.33)
    #위치
    spose1=posx(382.29, 117.04, 33, 84.38, 179.04, 84.71)#medium block
    spose2=posx(389.68, 165.02, 33, 156.84, 179.45, 156.95)#largeblock
    spose3=posx(373.68, 69.35, 31, 111.72, 178.83, 110.53)#small
    spose4=posx(520.17, 233.30, 33, 102.88, -179.35, -167.02)#tapor
    spose5=posx(457.52, 233.76, 33, 153.38, -178.77, -117.94) # round
  


    spose1_up=posx(382.29, 117.04, 150, 84.38, 179.04, 84.71)#medium block
    spose2_up=posx(389.68, 165.02, 150, 156.84, 179.45, 156.95)#largeblock
    spose3_up=posx(373.68, 69.35, 150, 111.72, 178.83, 110.53)
    spose4_up=posx(520.17, 233.30, 150, 102.88, -179.35, -167.02)#tapor
    spose5_up=posx(457.52, 233.76, 150, 153.38, -178.77, -117.94)
    
    taperdown=posx(657.140, -32.270, 24.50, 167.81, 178.44, 77.45)

    spose1_in=posx(382.29, 117.04, 52, 84.38, 179.04, 84.71)#medium block
    spose2_in=posx(389.68, 165.02, 52, 156.84, 179.45, 156.95)#largeblock
    spose3_in=posx(373.68, 69.35, 52, 111.72, 178.83, 110.53)#small
    spose4_in=posx(520.17, 233.30, 65, 102.88, -179.35, -167.02)#tapor
    spose5_in=posx(457.52, 233.76, 52, 153.38, -178.77, -117.94) 
    
    spose1_out_1=posx(382.29, 119.34, 46.27, 12.69, -178.71, 12.40)#medium block
    spose1_out_2=posx(382.29, 119.34, 46.27, 2.55, -173.61, 2.55)#medium block
    spose1_out_3=posx(382.29, 119.34, 66.65, 2.55, -173.61, 2.55)#medium block

    spose1_out1_1=posx(382.29, 119.34, 26.27, 12.69, -178.71, 12.40)#medium block
    spose1_out1_2=posx(382.29, 119.34, 26.27, 2.55, -173.61, 2.55)#medium block
    spose1_out1_3=posx(382.29, 119.34, 46.65, 2.55, -173.61, 2.55)#medium block

    spose2_out_1=posx(390.15, 168.41, 45.65,138.83, -179.84, 138.58)#largeblock
    spose2_out_2=posx(390.15, 168.41, 45.65,177.83, -173.70, 177.56)#largeblock
    spose2_out_3=posx(390.15, 168.41, 71.65,177.83, -173.70, 177.56)#largeblock

    spose2_out1_1=posx(390.15, 168.41, 25.65,138.83, -179.84, 138.58)#largeblock
    spose2_out1_2=posx(390.15, 168.41, 25.65,177.83, -173.70, 177.56)#largeblock
    spose2_out1_3=posx(390.15, 168.41, 51.65,177.83, -173.70, 177.56)#largeblock


    spose3_out_1=posx(373.40, 69.88, 51.58, 4.55, -179.41, 3.98)#small
    spose3_out_2=posx(373.40, 69.88, 51.58, 0.23, -168.04, -0.35)#small
    spose3_out_3=posx(373.40, 69.88, 60.30, 0.23, -168.04, -0.35)#small
    spose4_out=posx(527.39, 237.00, 56.93, 162.94, 179.74, 73.21)#tapor
    spose5_out=posx(460.31, 234.65, 40.64, 11.96, -178.47, -77.17) #round

    spose3_out1_1=posx(373.40, 69.88, 31.58, 4.55, -179.41, 3.98)#small
    spose3_out1_2=posx(373.40, 69.88, 31.58, 0.23, -168.04, -0.35)#small
    spose3_out1_3=posx(373.40, 69.88, 30.30, 0.23, -168.04, -0.35)#small
    spose4_out1=posx(527.39, 237.00, 27.93, 162.94, 179.74, 73.21)#tapor
    spose5_out1=posx(460.31, 234.65, 20.64, 11.96, -178.47, -77.17) #round

   
    unstack_list1=[[spose1_out_1, spose1_out_2, spose1_out_3],[spose1_out1_1, spose1_out1_2, spose1_out1_3]]#medium
    unstack_list2=[[spose2_out_1, spose2_out_2, spose2_out_3],[spose2_out1_1, spose2_out1_2, spose2_out1_3]]#large
    unstack_list3=[[spose3_out_1, spose3_out_2, spose3_out_3],[spose3_out1_1, spose3_out1_2, spose3_out1_3]]#small
    unstack_list4=[[spose4_out,spose4_out,spose4_out],[spose4_out1,spose4_out1,spose4_out1]]#tapor
    unstack_list5=[[spose5_out,spose5_out,spose5_out],[spose5_out1,spose5_out1,spose5_out1]]#round
    spose1_list=[spose1, spose1_in]
    spose2_list=[spose2, spose2_in]
    spose3_list=[spose3, spose3_in]
    spose4_list=[spose4, spose4_in]
    spose5_list=[spose5, spose5_in]
    #창고 정의
    aa=Box('small_block', 'SHELF_3', spose3_list, spose3_up,1,unstack_list3)
   

    bb=Box('medium_block', 'SHELF_1', spose1_list, spose1_up,1,unstack_list1)
   
    cc=Box('large_block', 'SHELF_2', spose2_list, spose2_up,1,unstack_list2)

    dd=Box('round_block', 'SHELF_5', spose5_list, spose5_up,1,unstack_list5)

    ee=Box('tapor', 'SHELF_4', spose4_list, spose4_up,1,unstack_list4)

    
    large=[1,0]
    small=[1,1]
    medium=[0,1]
    round=[0,0]
    signal_list=[large, small,large, medium, round,small,medium]





    print("Moving to JReady...")
    movej(HOME_READY, vel=VELOCITY, acc=ACC)
    release()
    while rclpy.ok():
##분류모드##분류모드##분류모드##분류모드##분류모드##분류모드##분류모드##분류모드##분류모드##분류모드##분류모드##분류모드##분류모드##분류모드
        mode_select=int(input('typing 1 or 2\n1: Classification and IN-warehouse, 2: EX-warehouse, 3: Checking-warehouse  :'))
        if mode_select == 1:
            while True:
                # rclpy.spin_once(node) # wait() 함수가 spin을 포함 안 하면 추가 고려
                print("\n--- Starting Cycle ---")
                # 첫 번째 위치 (JReady)로 이동
                # 높이 측정
                grip()
                movel(z1, vel=VELOCITY, acc=ACC)
                time.sleep(0.5)
                task_compliance_ctrl(stx=[500, 500, 500, 100, 100, 100])
                time.sleep(1)
                set_desired_force(fd=[0, 0, -15, 0, 0, 0], dir=[0, 0, 1, 0, 0, 0], mod=DR_FC_MOD_REL)
                time.sleep(1)
                force_condition = check_force_condition(DR_AXIS_Z, max=10)
                time.sleep(1)
                print("force_condition Start : ", force_condition)
                while (force_condition > -1):
                    force_condition = check_force_condition(DR_AXIS_Z, max=10)
                    time.sleep(2)
                    bbb = get_current_posx()[0]
                    print(bbb[2])
                release_force()
                time.sleep(1)
                release_compliance_ctrl()
                time.sleep(1)
                # 그리퍼 릴리즈
                print("Executing release sequence...")
                movel(z1, vel=VELOCITY,acc=ACC)#높이 측정 위치로
                print("Moving to second position")        # measure 결과에 따른 로직
                if 61>=bbb[2] >= 53: #높이 높은거
                    print('tapor')
                    release()
                    movel(taperdown, vel=VELOCITY,acc=ACC)
                    grip()
                    time.sleep(1)
                    movel(z1_up,vel=VELOCITY,acc=ACC)
                    # movel(spose4_up,vel=VELOCITY,acc=ACC)
                    ee.stack()

                elif 51 >= bbb[2] >= 47:
                    release()
                    movel(p1, vel=VELOCITY,acc=ACC)#세로 측정 위치로
                    print("Executing grip sequence")
                    grip()
                    wait(1)
                    # measure 함수 호출 (디지털 입력 상태 확인)
                    print("Measuring ...")
                    for signal in signal_list:
                        a_1=signal[0]
                        b_1=signal[1]
                    wait(1)
                    movel(z1, vel=VELOCITY,acc=ACC)#높이 측정 위치로
                    if a_1 == 1 and b_1 == 1:
                        print('small square block')
                        movel(z1_up,vel=VELOCITY, acc=ACC)
                        # movel(spose3_up, vel=VELOCITY, acc=ACC)
                        aa.stack()
                    elif a_1 == 1 and b_1 == 0:
                        print('Large square block')
                        movel(z1_up,vel=VELOCITY, acc=ACC)
                        # movel(spose2_up, vel=VELOCITY, acc=ACC)
                        cc.stack()
                    elif a_1 == 0 and b_1 == 1:
                        print('medium square block')
                        movel(z1_up,vel=VELOCITY, acc=ACC)
                        # movesl(spose1_up, vel=VELOCITY, acc=ACC)
                        bb.stack()
                    elif a_1 == 0 and b_1 == 0:
                        print('round square block')
                        movel(z1_up,vel=VELOCITY, acc=ACC)
                        # movel(spose5_up,vel=VELOCITY, acc=ACC)
                        dd.stack()
                else:
                    print('nothing in gripper')
                    print('classification stop')
                    release()
                    break
                print("Executing final release in cycle...")
                release()
                print("--- Cycle finished ---")
            # 한 번만 실행하려면 여기에 break를 추가해 주세요!=0
            # break # 예시: 한 번만 실행하고 싶을 때 이 주석을 풀어주세요!

            
######출고모드######출고모드######출고모드######출고모드######출고모드######출고모드######출고모드

        elif mode_select == 2:
            while True:
                movej(HOME_READY,vel=VELOCITY, acc=ACC)
                select_wh=int(input('select_wh_number :'))
                if select_wh == 1:#small sq
                    # movel(spose3_up, vel=VELOCITY, acc=ACC)
                    aa.unstack()
                elif select_wh == 2:#medium sq
                    # movel(spose2_up, vel=VELOCITY, acc=ACC)
                    bb.unstack()
                elif select_wh == 3:#large sq
                    # movel(spose1_up, vel=VELOCITY, acc=ACC)
                    cc.unstack()
                elif select_wh == 4:#round sq
                    # movel(spose5_up, vel=VELOCITY, acc=ACC)
                    dd.unstack()
                elif select_wh == 5:#high sq
                    # movel(spose4_up, vel=VELOCITY, acc=ACC)
                    ee.unstack()
                elif select_wh == 6: #change to mode_select
                    break
                else:
                    print('wrong number!')
        
        elif mode_select == 3:
            while True:
                movej(HOME_READY,vel=VELOCITY, acc=ACC)
                select_wh=int(input('select_wh_number :'))

                if select_wh == 1:#small sq
                    print(aa.info())
                elif select_wh == 2:#medium sq
                    print(bb.info())
                elif select_wh == 3:#large sq
                    print(cc.info())
                elif select_wh == 4:#round sq
                    print(dd.info())
                elif select_wh == 5:#high sq
                    print(ee.info())
                elif select_wh == 6: #change to mode_select
                    break
                else:
                    print('wrong number!')
                


        else:
            print('wrong mode_select!')
    
    ## 3번에 재고 확인 코드?

    rclpy.shutdown()

if __name__ == "__main__":
    main()
