import time
import threading
import os
import webbrowser
import socket
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QMessageBox, QFileDialog
from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from tkinter import *
from tkinter import ttk
from bs4 import BeautifulSoup


def site_kinds(input_data):
    site_adress = ''
    # 북앤 라이프 (도서문화상품권)
    if input_data == 'book_and_life_book_pin' or input_data == 'book_and_life_book_inherence' or input_data == 'book_and_life_mobile' or input_data == 'book_and_life_online':
        site_adress = 'https://www.booknlife.com/hp/giftUseConfirm.do'
    return site_adress


class MyUI:
    def __init__(self):
        root = Tk()
        root.title("크롤링 서버")
        root.geometry("200x200")

        number_entry = ttk.Entry(root, width=20)
        number_entry.grid(row=0, columnspan=1)

        self.craw = Crawling()

        # command=lambda: 뒤에 명령 작성.
        button1 = ttk.Button(root, text="서버 시작",
                             command=lambda: self.craw.crawling(b'happy_money_gift_num#1234#1234#2345#4567#21222122'))
        button1.grid(row=1, column=0)

        root.mainloop()



class MyApp(QWidget):
    btnControl: bool
    server_ip: socket.gethostbyname((socket.gethostname()))
    print(socket.gethostbyname((socket.gethostname())))
    server_port: str
    user_id: str
    user_pw: str
    driver_path: str

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.FileInit()     # 설정 파일 초기화

        if os.path.isfile(self.driver_path) == False:  # 크롬 드라이버 세팅이 되어있지 않을 경우 설정 안내
            chrome_site = 'https://chromedriver.storage.googleapis.com/index.html?path=72.0.3626.69/'
            webbrowser.open(chrome_site)

            self.setWindowTitle('웹 크롤링')
            self.move(400, 300)
            self.resize(400, 200)

            label1 = QLabel('크롤링 서버를 위한 크롬 드라이버 설치가 필요합니다', self)
            label1.move(20, 20)
            label2 = QLabel('chromedriver_win32.zip 파일을 다운 받고', self)
            label2.move(20, 40)
            label2 = QLabel('chromedriver.exe 실행파일의 경로를 설정해주시길 바랍니다.', self)
            label2.move(20, 60)
            label2 = QLabel('(프로그램 설치 폴더 권장)', self)
            label2.move(20, 80)

            pushButton = QPushButton("파일 경로 세팅", self)
            pushButton.clicked.connect(self.FilePathSetting)
            pushButton.move(20, 100)
            self.show()

        else:
            craw = Crawling(self.user_id, self.user_pw, self.driver_path)   # 크롤링 클래스 생성 -> 초기화 진행

            craw.refresh_happy_site()   # 자동 로그아웃 방지를 위한 15분 간격 새로고침 실행

            server = Server(craw, self.server_ip, self.server_port)
            server.server_start()

            self.setWindowTitle('웹 크롤링')
            self.move(800, 300)
            self.resize(400, 300)

            label1 = QLabel('크롤링 서버 시작 중입니다', self)
            label1.move(20, 20)
            label2 = QLabel('해피 머니 상품권은 보안 번호 입력이 필요합니다', self)
            label2.move(20, 40)

            label3 = QLabel('서버 아이피', self)
            label3.move(20, 60)
            edit3 = QLineEdit(self.server_ip, self)
            edit3.move(160, 60)

            label4 = QLabel('서버 포트', self)
            label4.move(20, 80)
            edit4 = QLineEdit(self.server_port, self)
            edit4.move(160, 80)

            label5 = QLabel('해피머니 아이디', self)
            label5.move(20, 100)
            edit5 = QLineEdit(self.user_id, self)
            edit5.move(160, 100)

            label6 = QLabel('해피머니 패스워드', self)
            label6.move(20, 120)
            edit6 = QLineEdit(self.user_pw, self)
            edit6.move(160, 120)

            changebtn = QPushButton('설정 변경', self)
            changebtn.move(160, 140)
            changebtn.clicked.connect(self.configChange)

            label7 = QLabel('오류가 발생할 경우 프로그램 재설치를 권장합니다', self)
            label7.move(20, 180)

            label8 = QLabel('가동 중인 서버 아이피 ' + socket.gethostbyname((socket.gethostname())), self)
            label8.move(20, 200)

            rebootbtn = QPushButton('재시작', self)
            rebootbtn.move(160, 220)
            rebootbtn.clicked.connect(self.program_reboot)

            self.show()
    def program_reboot(self):
        # 프로그램 재 시작
        executable = sys.executable
        args = sys.argv[:]
        args.insert(0, sys.executable)
        os.execvp(executable, args)


    def FilePathSetting(self):
        self.driver_path = QFileDialog.getOpenFileName(self)
        print('파일 경로 설정 시작')
        self.configChange()
        print('파일 경로 설정 완료')
        
        # 프로그램 재 시작
        executable = sys.executable
        args = sys.argv[:]
        args.insert(0, sys.executable)
        os.execvp(executable, args)

    def configChange(self):
        if os.path.isfile('app.config'):    # 설정 파일이 있을 경우 입력한 인풋값으로 초기화
            f = open('app.config', 'w')
            f.writelines(['server_ip:' + self.server_ip + '\n', 'server_port:' + self.server_port + '\n', 'user_id:' + self.user_id + '\n', 'user_pw:' + self.user_pw + '\n', 'driver_path:' + self.driver_path[0]])
            f.close()
        else:   # 설정 파일이 없을 경우(처음 프로그램 가동시) 설정 파일 생성
            f = open('app.config', 'w')
            f.writelines(['server_ip:' + self.server_ip + '\n', 'server_port:' + self.server_port + '\n', 'user_id:' + self.user_id + '\n', 'user_pw:' + self.user_pw + '\n', 'driver_path:' + self.driver_path[0]])
            f.close()
        msgbox = QMessageBox(self)
        msgbox.question(self, '알림', '설정 변경이 완료되었습니다.', QMessageBox.Yes)

        print('설정변경완료')

    def FileInit(self):
        if os.path.isfile('app.config'):
            try:     # 설정 파일이 존재할 경우 읽어옴
                f = open('app.config', 'r')
                lines = f.readlines()
                self.server_ip = lines[0].replace('server_ip:', '')
                self.server_ip = self.server_ip.replace('\n', '')
                self.server_port = lines[1].replace('server_port:', '')
                self.server_port = self.server_port.replace('\n', '')
                self.user_id = lines[2].replace('user_id:', '')
                self.user_id = self.user_id.replace('\n', '')
                self.user_pw = lines[3].replace('user_pw:', '')
                self.user_pw = self.user_pw.replace('\n', '')
                self.driver_path = lines[4].replace('driver_path:', '')
                self.driver_path = self.driver_path.replace('\n', '')
                f.close()
            except:     # 예외 발생시 디폴트 값으로 재 작성
                f = open('app.config', 'w')
                data = 'server_ip:' + socket.gethostbyname((socket.gethostname())) + '\nserver_port:9000\nuser_id:dhdldhdl45\nuser_pw:emperor01!@\ndriver_path:' + os.getcwd() + '\chromedriver.exe'  # 디폴트 값
                f.write(data)
                f.close()
        else:   # 설정 파일이 없을 경우(처음 프로그램 가동시) 설정 파일 생성
            f = open('app.config', 'w')
            data = 'server_ip:' + socket.gethostbyname((socket.gethostname())) +'\nserver_port:9000\nuser_id:dhdldhdl45\nuser_pw:emperor01!@\ndriver_path:' + os.getcwd() + '\chromedriver.exe'    # 디폴트 값
            f.write(data)
            f.close()

            f = open('app.config', 'r')
            lines = f.readlines()
            self.server_ip = lines[0].replace('server_ip:', '')
            self.server_ip = self.server_ip.replace('\n', '')
            self.server_port = lines[1].replace('server_port:', '')
            self.server_port = self.server_port.replace('\n', '')
            self.user_id = lines[2].replace('user_id:', '')
            self.user_id = self.user_id.replace('\n', '')
            self.user_pw = lines[3].replace('user_pw:', '')
            self.user_pw = self.user_pw.replace('\n', '')
            self.driver_path = lines[4].replace('driver_path:', '')
            self.driver_path = self.driver_path.replace('\n', '')
            f.close()

class Server:
    happy_init_bool = False

    def __init__(self, craw, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = int(server_port)
        self.craw = craw

    #  서버 스레드 시작
    def server_start(self):
        t = threading.Thread(target=self.server_open, args=())
        t.start()

    #  서버 스레드에 의한 초기화 시작
    def server_open(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.server_ip, self.server_port))

        print("대기중")

        while True:
            s.listen(100)
            conn, addr = s.accept()

            print('접속')
            if self.craw.driver_happy.current_url != 'http://www.happymoney.co.kr/svc/card/useCardSearch.hm' and not self.happy_init_bool:    # 해피머니 사이트 로그아웃 상태
                message = 'happy_money_gift_num_error'
                sbuf = bytes(message, encoding='utf-8')
                conn.send(sbuf)

            print('초기화 완료')

            recv_data = conn.recv(1024)  # 상품권 종류 확인(ex 도서문화상품권, 주유상품권 etc)
            print(recv_data)
            crawling_return_value = self.craw.crawling(recv_data)  # 크롤링

            sbuf = bytes(crawling_return_value, encoding='utf-8')
            conn.send(sbuf)
            conn.close()
            print('접속종료')

class Crawling:
    def __init__(self, user_id:str, user_pw:str, driver_path: str):
        # 북앤라이프 상품권 초기화
        self.driver = webdriver.Chrome(driver_path)
        self.driver.maximize_window()
        self.driver.implicitly_wait(3)
        self.driver.get('https://www.booknlife.com/hp/giftUseConfirm.do')

        # 해피머니 상품권 초기화
        self.driver_happy = webdriver.Chrome(driver_path)
        self.driver_happy.implicitly_wait(3)
        self.driver_happy.maximize_window()
        self.driver_happy.get('http://www.happymoney.co.kr/svc/card/useCardSearch.hm')
        time.sleep(1)  # 조회 임의 대기시간

        ar = Alert(self.driver_happy)
        ar.accept()

        time.sleep(5)  # 조회 임의 대기시간

        try:
            user_id = user_id
            user_pw = user_pw

            self.driver_happy.find_element_by_id('memberId').send_keys('')
            time.sleep(0.1)  # 조회 임의 대기시간
            self.driver_happy.find_element_by_id('memberId').send_keys('')
            time.sleep(0.1)  # 조회 임의 대기시간
            self.driver_happy.find_element_by_id('memberId').send_keys('')
            for id in user_id:
                self.driver_happy.find_element_by_id('memberId').send_keys(id)
                time.sleep(0.1)  # 조회 임의 대기시간

            self.driver_happy.find_element_by_id('memberPwd').send_keys('')
            time.sleep(0.1)  # 조회 임의 대기시간
            self.driver_happy.find_element_by_id('memberPwd').send_keys('')
            for pw in user_pw:
                self.driver_happy.find_element_by_id('memberPwd').send_keys(pw)
                time.sleep(0.1)  # 조회 임의 대기시간
        except:
            time.sleep(10)  # 조회 임의 대기시간
            self.__init__(user_id, user_pw, driver_path)

        print('초기화완료')

    # 15분 마다 페이지 새로고침
    def refresh_happy_site(self):
        if self.driver_happy.current_url == 'http://www.happymoney.co.kr/svc/card/useCardSearch.hm':
            print('새로고침')
            self.driver_happy.refresh()
        print('타이머실행중')
        timer = threading.Timer(900, self.refresh_happy_site)
        timer.start()




    def crawling(self, input_data):
        temp_array = input_data.decode('ascii').split('#')  # bytes
        input_data = temp_array[0]

        # 해피머니 상품권 사용여부조회
        if input_data == 'happy_money_gift_num':
            if self.driver_happy.current_url != 'http://www.happymoney.co.kr/svc/card/useCardSearch.hm':
                crawling_value: str = 'happy_money_gift_num_error'
                return crawling_value

            pin1: str = temp_array[1]
            pin2: str = temp_array[2]
            pin3: str = temp_array[3]
            pin4: str = temp_array[4]
            pinAuth: str = temp_array[5]

            print(pin1)

            time.sleep(0.1)  # 조회 임의 대기시간
            self.driver_happy.find_element_by_id('pinNumber1').send_keys(' ')
            time.sleep(0.1)  # 조회 임의 대기시간
            self.driver_happy.find_element_by_id('pinNumber1').send_keys('')
            time.sleep(0.1)  # 조회 임의 대기시간
            self.driver_happy.find_element_by_id('pinNumber1').send_keys('')
            # 핀번호 입력
            for pin in pin1:
                self.driver_happy.find_element_by_id('pinNumber1').send_keys(pin)
                time.sleep(0.1)  # 조회 임의 대기시간

            self.driver_happy.find_element_by_id('pinNumber2').send_keys('')
            time.sleep(0.1)  # 조회 임의 대기시간
            self.driver_happy.find_element_by_id('pinNumber2').send_keys('')
            for pin in pin2:
                self.driver_happy.find_element_by_id('pinNumber2').send_keys(pin)
                time.sleep(0.1)  # 조회 임의 대기시간

            self.driver_happy.find_element_by_id('pinNumber3').send_keys('')
            time.sleep(0.1)  # 조회 임의 대기시간
            self.driver_happy.find_element_by_id('pinNumber3').send_keys('')
            for pin in pin3:
                self.driver_happy.find_element_by_id('pinNumber3').send_keys(pin)
                time.sleep(0.1)  # 조회 임의 대기시간

            self.driver_happy.find_element_by_id('pinNumber4').send_keys('')
            time.sleep(0.1)  # 조회 임의 대기시간
            self.driver_happy.find_element_by_id('pinNumber4').send_keys('')
            for pin in pin4:
                self.driver_happy.find_element_by_id('pinNumber4').send_keys(pin)
                time.sleep(0.1)  # 조회 임의 대기시간

            self.driver_happy.find_element_by_id('printDate').send_keys('')
            time.sleep(0.1)  # 조회 임의 대기시간
            self.driver_happy.find_element_by_id('printDate').send_keys('')
            for pin in pinAuth:
                self.driver_happy.find_element_by_id('printDate').send_keys(pin)
                time.sleep(0.1)  # 조회 임의 대기시간

            self.driver_happy.find_element_by_id('usageStatusCheck').click()



            ar = Alert(self.driver_happy)
            alertText = ar.text
            print(alertText)
            time.sleep(1)  # 조회 임의 대기시간
            ar.accept()

            # 미사용
            if alertText == '발행일/인증번호를 확인하세요':
                crawling_value: str = 'happy_money_gift_num_none'
                return crawling_value
            else:
                crawling_value: str = 'happy_money_gift_num_use'
                return crawling_value

        # =========================================================================

        # 북앤 라이프 도서 상품권 pin번호 조회
        if input_data == 'book_and_life_book_pin':
            pin1 = temp_array[1]
            pin2 = temp_array[2]
            pin3 = temp_array[3]
            pin4 = temp_array[4]
            pinAuth = temp_array[5]

            self.driver.find_element_by_id('radio1_gcct').click()  # 라디오 선택
            self.driver.find_element_by_id('selectType1').click()  # 라디오 선택

            # 핀번호 입력
            self.driver.find_element_by_id('PIN1').send_keys("8643")
            self.driver.find_element_by_id('PIN2').send_keys("9129")
            self.driver.find_element_by_id('PIN3').send_keys("2241")
            self.driver.find_element_by_id('PIN4').send_keys("4601")

            # 인증번호 입력
            self.driver.find_element_by_id('pinAuthNum').send_keys("4824")

            # 상품권 조회
            self.driver.find_element_by_id('useConfirmSelect').click()
            time.sleep(3)  # 조회 임의 대기시간

            req = self.driver.page_source
            soup = BeautifulSoup(req, "html.parser")
            price1 = soup.find('td', id="tdPrice1").get_text()
            price3 = soup.find('td', id="tdPrice3").get_text()
            if price1 != "" and price3 != "":   # 상품권 발행이 올바른 상태이고
                if price1 == price3:    # 액면금액과 현재잔액과 일치할 경우
                    crawling_value: str = 'book_and_life_book_pin_use'
                    return crawling_value
                else:                   # 일치하지 않을 경우
                    crawling_value: str = 'book_and_life_book_pin_none'
                    return crawling_value

            ar = Alert(self.driver)
            alertText = ar.text
            print(alertText)
            time.sleep(1)  # 조회 임의 대기시간
            ar.accept()

            # 미사용
            if alertText == '고객님, 상품권 번호가 잘못되었거나, 이미 사용된 것 같습니다. 계속 발생하면 고객센터(1544-5111)로 연락 부탁 드려도 될까요?' or alertText == '발행일/인증번호를 확인하세요' or alertText == '핀번호/바코드를 확인하세요':
                crawling_value: str = 'book_and_life_book_pin_none'
                return crawling_value

        # 북앤 라이프 도서 상품권 고유 번호 조회
        if input_data == 'book_and_life_book_inherence':
            uniqNum = temp_array[1]

            self.driver.find_element_by_id('radio1_gcct').click()  # 라디오 선택
            self.driver.find_element_by_id('selectOnlyNum').click()  # 라디오 선택

            # 상품권 고유 번호 입력
            self.driver.find_element_by_id('uniqNum').send_keys(uniqNum)

            # 상품권 조회
            self.driver.find_element_by_id('useConfirmSelect').click()
            time.sleep(3)  # 조회 임의 대기시간

            ar = Alert(self.driver)
            alertText = ar.text
            print(alertText)
            ar.accept()

            # 미사용
            if alertText == '고객님, 상품권 번호가 잘못되었거나, 이미 사용된 것 같습니다. 계속 발생하면 고객센터(1544-5111)로 연락 부탁 드려도 될까요?' or alertText == '발행일/인증번호를 확인하세요' or alertText == '핀번호/바코드를 확인하세요':
                crawling_value = 'book_and_life_book_pin_none'
                return crawling_value
            else:
                crawling_value = 'book_and_life_book_pin_use'
                return crawling_value

        # 북앤 라이프 모바일 도서 상품권 조회
        if input_data == 'book_and_life_mobile':
            pin1 = temp_array[1]
            pin2 = temp_array[2]
            pin3 = temp_array[3]
            pin4 = temp_array[4]
            pinAuth = temp_array[5]
            self.driver.find_element_by_id('radio3_gcct').click()  # 라디오 선택

            # 핀번호 입력
            self.driver.find_element_by_id('PIN1').send_keys(pin1)
            self.driver.find_element_by_id('PIN2').send_keys(pin2)
            self.driver.find_element_by_id('PIN3').send_keys(pin3)
            self.driver.find_element_by_id('PIN4').send_keys(pin4)

            # 인증번호 입력
            self.driver.find_element_by_id('pinAuthNum').send_keys(pinAuth)

            # 상품권 조회
            self.driver.find_element_by_id('useConfirmSelect').click()
            time.sleep(3)  # 조회 임의 대기시간

            ar = Alert(self.driver)
            alertText = ar.text
            print(alertText)
            ar.accept()
            # 미사용
            if alertText == '고객님, 상품권 번호가 잘못되었거나, 이미 사용된 것 같습니다. 계속 발생하면 고객센터(1544-5111)로 연락 부탁 드려도 될까요?' or alertText == '발행일/인증번호를 확인하세요' or alertText == '핀번호/바코드를 확인하세요':
                crawling_value = 'book_and_life_mobile_none'
                return crawling_value
            else:
                crawling_value = 'book_and_life_mobile_use'
                return crawling_value

        # 북앤 라이프 온라인 도서 상품권 조회
        if input_data == 'book_and_life_online':
            pin1 = temp_array[1]
            pin2 = temp_array[2]
            pin3 = temp_array[3]
            pin4 = temp_array[4]
            pinAuth = temp_array[5]
            self.driver.find_element_by_id('radio2_gcct').click()  # 라디오 선택

            # 핀번호 입력
            self.driver.find_element_by_id('PIN1').send_keys(pin1)
            self.driver.find_element_by_id('PIN2').send_keys(pin2)
            self.driver.find_element_by_id('PIN3').send_keys(pin3)
            self.driver.find_element_by_id('PIN4').send_keys(pin4)

            # 인증번호 입력
            self.driver.find_element_by_id('pinAuthNum').send_keys(pinAuth)

            # 상품권 조회
            self.driver.find_element_by_id('useConfirmSelect').click()
            time.sleep(3)  # 조회 임의 대기시간

            ar = Alert(self.driver)
            alertText = ar.text
            print(alertText)
            ar.accept()
            # 미사용
            if alertText == '고객님, 상품권 번호가 잘못되었거나, 이미 사용된 것 같습니다. 계속 발생하면 고객센터(1544-5111)로 연락 부탁 드려도 될까요?' or alertText == '발행일/인증번호를 확인하세요' or alertText == '핀번호/바코드를 확인하세요':
                crawling_value = 'book_and_life_online_none'
                return crawling_value
            else:
                crawling_value = 'book_and_life_online_use'
                return crawling_value


if __name__ == '__main__':
    # app_console = MyUI()
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
    sys.exit()
    app.quit()
