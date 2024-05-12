import serial
import math
import glob
import time
import firebase_admin
from firebase_admin import credentials, firestore

class LidarData:
    def __init__(self, FSA, LSA, CS, Speed, TimeStamp, Degree_angle, Angle_i, Distance_i):
        self.FSA = FSA  # Front Start Angle 감지 시작 각도
        self.LSA = LSA  # Last Start Angle 감지 마지막 각도
        self.CS = CS    # Checksum
        self.Speed = Speed  # 센서 회전 속도
        self.TimeStamp = TimeStamp  # 데이터 생성 시간
        self.Degree_angle = Degree_angle    # Degree 각도(측정 지점의)
        self.Angle_i = Angle_i  # Radian 각도(측정 지점의)
        self.Distance_i = Distance_i    # 물체까지의 거리

def CalcLidarData(data_str):
    data_str = data_str.replace(' ', '')

    Speed = int(data_str[2:4] + data_str[0:2], 16) / 100
    FSA = float(int(data_str[6:8] + data_str[4:6], 16)) / 100
    LSA = float(int(data_str[-8:-6] + data_str[-10:-8], 16)) / 100
    TimeStamp = int(data_str[-4:-2] + data_str[-6:-4], 16)
    CS = int(data_str[-2:], 16)

    Confidence_i = list()
    Angle_i = list()
    Distance_i = list()
    Degree_angle = list()

    if(LSA - FSA > 0):
        angleStep = float(LSA - FSA) / 12
    else:
        angleStep = float((LSA + 360) - FSA) / 12

    counter = 0
    circle = lambda deg: deg - 360 if deg >= 360 else deg

    for i in range(0, 6 * 12, 6):
        Distance_i.append(int(data_str[8+i+2 : 8+i+4] + data_str[8+i : 8+i+2], 16) / 1000)
        Degree_angle.append(circle(angleStep * counter + FSA))
        Angle_i.append(circle(angleStep * counter + FSA) * math.pi / 180.0)
        counter += 1

    lidar_data = LidarData(FSA, LSA, CS, Speed, TimeStamp, Degree_angle, Angle_i, Distance_i)
    return lidar_data

def choice_weight(ser, tmpString, flag2c):
    start = None
    count_jb = 0
    finish = False
    end = None
    default_value = 40
    wd = {'right_60' : default_value,
          'right_45' : default_value ,
          'right_30' : default_value,
          'right_15' : default_value,
          'right' : default_value,
          'left' : default_value,
          'left_15' : default_value,
          'left_30' : default_value,
          'left_45' : default_value,
          'left_60' : default_value
         }

    while True:
       
        b = ser.read()
        tmpInt = int.from_bytes(b, 'big')

        # 0x54 바이트: 데이터 패킷의 시작을 나타내는 바이트
        if (tmpInt == 0x54):
            tmpString += b.hex() + " "  # b를 16진수로 변환하여 문자열에 추가
            flag2c = True   # 데이터 패킷의 시작을 나타냄
            continue

        # 0x2c 바이트: 데이터 패킷의 길이를 나타내는 고정된 값
        elif (tmpInt == 0x2c and flag2c):
            tmpString += b.hex() # b를 16진수로 변환하여 문자열에 추가

            # 데이터 패킷의 길이가 예상과 다르면(90이 아니면) 이전에 저장된 데이터를 초기화
            if (not len(tmpString[0:-5].replace(' ','')) == 90):
                tmpString = ""
                flag2c = False
                continue

            lidar_data = CalcLidarData(tmpString[0:-5]) # 데이터 패킷의 마지막에는 0x2c 바이트가 오므로, 이를 제외한 데이터만을 파싱하기 위해 [0:-5]

            end = lidar_data.Degree_angle[len(lidar_data.Degree_angle)-1] # 마지막으로 파싱된 라이다 데이터의 각도 저장

            if count_jb == 0:
                start = lidar_data.Degree_angle[0]

            elif count_jb >= 1:
                for _ in range(len(lidar_data.Degree_angle) - 1):
                    if (end <= start <= lidar_data.Degree_angle[0] and False) or (lidar_data.Degree_angle[_] <= start <= lidar_data.Degree_angle[_+1]):
                        print(f'start = {start} lidar_data.Degree_angle[_] = {lidar_data.Degree_angle[_]}  lidar_data.Degree_angle[_+1] = {lidar_data.Degree_angle[_+1]}')
                        finish = True

            if finish:
                break

            for _ in range(len(lidar_data.Degree_angle)):
                if 15 <= lidar_data.Degree_angle[_] <= 30 and lidar_data.Distance_i[_] <= 1:
                    wd['right_60'] -= 1

                elif 30 <= lidar_data.Degree_angle[_] <= 45 and lidar_data.Distance_i[_] <= 1:
                    wd['right_60'] -= 1
                    wd['right_45'] -= 1

                elif 45 <= lidar_data.Degree_angle[_] <= 60 and lidar_data.Distance_i[_] <= 1:
                    wd['right_45'] -= 1
                    wd['right_30'] -= 1

                elif 60 <= lidar_data.Degree_angle[_] <= 75 and lidar_data.Distance_i[_] <= 1:
                    wd['right_30'] -= 1
                    wd['right_15'] -= 1

                elif 75 <= lidar_data.Degree_angle[_] <= 90 and lidar_data.Distance_i[_] <= 1:
                    wd['right_15'] -= 1
                    wd['right'] -= 1

                elif 90 <= lidar_data.Degree_angle[_] <= 105 and lidar_data.Distance_i[_] <= 1:
                    wd['right'] -= 1

                elif 255 <= lidar_data.Degree_angle[_] <= 270 and lidar_data.Distance_i[_] <= 1:
                    wd['left'] -= 1

                elif 270 <= lidar_data.Degree_angle[_] <= 285 and lidar_data.Distance_i[_] <= 1:
                    wd['left'] -= 1
                    wd['left_15'] -= 1

                elif 285 <= lidar_data.Degree_angle[_] <= 300 and lidar_data.Distance_i[_] <= 1:
                    wd['left_15'] -= 1
                    wd['left_30'] -= 1

                elif 300 <= lidar_data.Degree_angle[_] <= 315 and lidar_data.Distance_i[_] <= 1:
                    wd['left_30'] -= 1
                    wd['left_45'] -= 1

                elif 315 <= lidar_data.Degree_angle[_] <= 330 and lidar_data.Distance_i[_] <= 1:
                    wd['left_45'] -= 1
                    wd['left_60'] -= 1

                elif 330 <= lidar_data.Degree_angle[_] <= 345 and lidar_data.Distance_i[_] <= 1:
                    wd['left_60'] -= 1

            tmpString = ""
            count_jb += 1

        else:
            tmpString += b.hex()+ " "

        b = ''
        flag2c = False

    print(wd)

    max_value = max(wd.values())
    if max_value <= 20:
        print('avoid direction : back')
        return 'back'
    max_weight_direction = [key for key,value in wd.items() if value == max(wd.values())]

    if len(max_weight_direction) == 1:
        print(f'avoid direction : {max_weight_direction[0]}')
        print('--------------------------------------------------------------------')
        return max_weight_direction[0]
    else:
        order_p = ['left_60', 'right_60', 'left_45', 'right_45', 'left_30', 'right_30', 'left_15', 'right_15', 'left', 'right']
        for direction in order_p:
            if direction in max_weight_direction:
                print(f'avoid direction : {direction}')
                print('--------------------------------------------------------------------')
                return direction
def main():
   
    port_list = None
   
    while port_list is None:
        port_list = glob.glob('/dev/ttyUSB*')
    if not port_list:
        print("no serial port")
        exit()

    port12 = port_list[0]
    ser = False

    while True and not ser:
        ser = serial.Serial(port=port12,
                        baudrate=230400,
                        timeout=5.0,
                        bytesize=8,
                        parity='N',
                        stopbits=1)

    print('connection')

    tmpString = ""
    lines = list()
    angles = list()
    distances = list()
    flag2c = False
    direction = None

    cred = credentials.Certificate('/home/wook/Desktop/CapDrone_key.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    doc_ref_avoid = db.collection("Capston").document("drone")

    #avoid_start = {"header": "avoid_start"}
    #avoid_finish = {"header": "avoid_finish"}
   
    max_iterations = 5  # 5번 반복
    # 최종 방향 결정을 위한 변수 추가
   
    start_avoid = False
    end_avoid = False
    trying_avoid = 2
    count_avoid = 0
    count_list = 2
    start_while = 0
   
    while True:
       
        b = ser.read()
        tmpInt = int.from_bytes(b, 'big')

        # 0x54 바이트: 데이터 패킷의 시작을 나타내는 바이트
        if (tmpInt == 0x54):
            tmpString += b.hex() + " "  # b를 16진수로 변환하여 문자열에 추가
            flag2c = True   # 데이터 패킷의 시작을 나타냄
            continue

        # 0x2c 바이트: 데이터 패킷의 길이를 나타내는 고정된 값
        elif (tmpInt == 0x2c and flag2c):
            tmpString += b.hex() # b를 16진수로 변환하여 문자열에 추가

            # 데이터 패킷의 길이가 예상과 다르면(90이 아니면) 이전에 저장된 데이터를 초기화
            if (not len(tmpString[0:-5].replace(' ','')) == 90):
                tmpString = ""
                flag2c = False
                continue
           
            lidar_data = CalcLidarData(tmpString[0:-5]) # 데이터 패킷의 마지막에는 0x2c 바이트가 오므로, 이를 제외한 데이터만을 파싱하기 위해 [0:-5]
           
           
            count_list = 2
           
            for _ in range(len(lidar_data.Degree_angle)):
                if (lidar_data.Degree_angle[_] >= 355) or (lidar_data.Degree_angle[_] <= 5):
                    count_list = 0  
                    if lidar_data.Distance_i[_] <= 0.2:
                         count_avoid += 1
                         start_avoid = True
                         print('avoid')
                         count_list = 1
               
               
            if (count_list == 0):
                print('No avoid')
                if start_while == 0:
                    continue
                elif start_while >= 1:
                    trying_avoid = 1
           
           
           
               
            tmpString = ""
           
        else:
            tmpString += b.hex()+ " "

        b = ''
        flag2c = False
       
       
        if start_avoid:
            header_avoid_start = {"header": "avoid_start"}
            doc_ref_avoid.update(header_avoid_start)
            final_direction_count = {'back': 0, 'right_60': 0, 'right_45': 0, 'right_30': 0, 'right_15': 0, 'right': 0,
                                    'left': 0, 'left_15': 0, 'left_30': 0, 'left_45': 0, 'left_60': 0}
           
            for _ in range(max_iterations):
                direction = choice_weight(ser, tmpString, flag2c)
                final_direction_count[direction] += 1

            print("Result:", final_direction_count)
            print('--------------------------------------------------------------------')

            # 누적 변수를 기준으로 최종 회피 방향 결정
            final_direction = max(final_direction_count, key=final_direction_count.get)
            print("Final avoidance direction:", final_direction)

            # Firebase에 최종 회피 방향 업데이트
            avoid_direction = {"header": final_direction}
            header_wait = {"header": "Waiting..."}
            doc_ref_avoid.update(avoid_direction)
            doc_ref_avoid.update(header_wait)
            start_avoid = False
            end_avoid = True
            time.sleep(1)
            count_avoid = 0
            start_while += 1
       
        if end_avoid and trying_avoid == 1:
            header_avoid_finish = {"header": "avoid_finish"}
            doc_ref_avoid.update(header_avoid_finish)
            end_avoid = False
            trying_avoid = 0
             
         

if __name__ == "__main__":
    main()