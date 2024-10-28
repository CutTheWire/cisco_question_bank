import random
import string
import time
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# Chrome 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # GUI 없이 실행
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--mute-audio")  # 소리 차단
chrome_options.add_argument("--disable-gpu")  # GPU 가속 비활성화


# ChromeDriver 경로
chrome_driver_path = "C:/Program Files/chromedriver-win64/chromedriver.exe"

# 랜덤 닉네임 생성 함수
def generate_random_nickname():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=9))

# Selenium 작업 함수
def simulate_user_action():
    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)
    driver.get("https://myaircon.online/")  # 사이트 주소로 이동

    try:
        # 닉네임 입력
        nickname_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='nickname']")
        nickname_input.send_keys(generate_random_nickname())

        # OK 버튼 클릭
        ok_button = driver.find_element(By.CLASS_NAME, "ok")
        ok_button.click()
        time.sleep(0.1)  # 짧은 대기

        # Online mode 버튼 클릭
        online_mode_button = driver.find_element(By.CLASS_NAME, "real-time")
        online_mode_button.click()
        time.sleep(0.1)  # 짧은 대기

        # Minus 버튼을 10번 클릭
        minus_button = driver.find_element(By.CLASS_NAME, "minus")
        while 1:
            minus_button.click()
            time.sleep(0.1)  # 클릭 간격
    finally:
        driver.quit()
        time.sleep(0.1)  # 새 접속을 위한 짧은 대기

# 다중 사용자 트래픽 시뮬레이션
def run_simulation(user_count):
    with ThreadPoolExecutor(max_workers=user_count) as executor:
        futures = [executor.submit(simulate_user_action) for _ in range(user_count)]
        try:
            for future in futures:
                future.result()  # 예외가 발생하면 표시됨
        except KeyboardInterrupt:
            print("Simulation stopped by user.")

if __name__ == "__main__":
    # 트래픽을 발생시킬 사용자 수 설정
    user_count = 10
    run_simulation(user_count)
