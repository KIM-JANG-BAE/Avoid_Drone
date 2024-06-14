## 드론 파일

### Droncontroller.py
* 드론의 제어와 데이터 전송의 역할을 담당하는 파일

### LidarData.py
* LD19 라이다 데이터를 정제하며 해당 데이터값을 이용하여 회피알고리즘 판단 및 제어명령 전달

### ZED.py
* ZED Camera를 이용하여 실시간 상황을 보여주며 해당 데이터를 obj파일로 변환하는 파일

### objsender.py
* ZED.py에서 만들어진 obj파일을 서버로 전달하는 파일 
