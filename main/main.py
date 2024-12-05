import json
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

# Biến toàn cục
login_count = 0
viotp_over_10k = 0
viotp_under_10k = 0
viotp_under_1k = 0
thatbai_count = 0

# Cấu hình ChromeDriver
def configure_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Chạy chế độ không giao diện (bỏ nếu muốn giao diện)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=720,1280")  # Kích thước phù hợp cho điện thoại
    chrome_options.add_argument('--log-level=3')  # Tắt log không cần thiết
    return chrome_options

# Kiểm tra lỗi "Bad access !" và đăng nhập lại
def check_bad_access(driver, login_button):
    while True:
        time.sleep(3)
        current_url = driver.current_url
        if current_url == "https://viotp.com/en/Dash/Index":
            return True  # Đăng nhập thành công

        try:
            error_message = driver.find_element(By.XPATH, "//b[contains(@class, 'text-danger') and text()='Bad access !']")
            print("Lỗi 'Bad access !' - Thử lại đăng nhập.")
            login_button.click()  # Nhấn nút đăng nhập lại
        except NoSuchElementException:
            return False

# Xử lý tài khoản đơn lẻ
def process_single_account(driver, account):
    global thatbai_count, login_count
    username_input, password_input = account.split(':')
    try:
        driver.get("https://viotp.com/en//api/AccountAPI/GetAPIToken")

        # Tìm và điền tên đăng nhập và mật khẩu
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input#UserName"))
        )
        username_field = driver.find_element(By.CSS_SELECTOR, "input#UserName")
        password_field = driver.find_element(By.CSS_SELECTOR, "input#Password")
        username_field.send_keys(username_input)
        password_field.send_keys(password_input)
        time.sleep(3)
        login_button = driver.find_element(By.CSS_SELECTOR, "button#kt_sign_in_submit")
        login_button.click()
        time.sleep(5)  # Chờ trang phản hồi

        # Kiểm tra và xử lý 'Bad access !' nếu có
        if check_bad_access(driver, login_button):
            login_count += 1
            print(f"Đăng nhập thành công cho tài khoản: {account}")
            balance_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.fs-2.fw-bolder.ng-binding"))
            )
            balance = int(balance_element.get_attribute("data-kt-countup-value"))
            print(f"Số dư tài khoản {username_input}: {balance} đ")
            process_login_and_save(driver, account, balance)
        else:
            thatbai_count += 1
            print(f"Đăng nhập thất bại cho tài khoản: {account}")

    except TimeoutException:
        print(f"Có thời gian chờ hết cho tài khoản: {account}")
        thatbai_count += 1

# Lấy token từ API
def get_token_from_api(driver):
    api_url = "https://viotp.com/en//api/AccountAPI/GetAPIToken"
    driver.get(api_url)
    time.sleep(3)
    response_text = driver.find_element(By.CSS_SELECTOR, "body").text
    response_json = json.loads(response_text)
    return response_json["Data"]["Token"]

# Phân loại tài khoản theo số dư và lưu
def process_login_and_save(driver, account, balance):
    global viotp_over_10k, viotp_under_10k, viotp_under_1k
    username_input, password_input = account.split(':')
    if balance is not None:
        file_name = classify_balance(balance)
        formatted_balance = f"{balance:,} đ".replace(',', '.')
        with open(file_name, 'a', encoding='utf-8') as f:
            if balance > 10000:
                token = get_token_from_api(driver)
                f.write(f'Tài khoản: {username_input}:{password_input}\nSố dư: {formatted_balance}\nToken: {token}\n')
                viotp_over_10k += 1
            elif balance >= 1000:
                f.write(f'Tài khoản: {username_input}:{password_input}\nSố dư: {formatted_balance}\n')
                viotp_under_10k += 1
            else:
                f.write(f'Tài khoản: {username_input}:{password_input}\nSố dư: {formatted_balance}\n')
                viotp_under_1k += 1

# Phân loại tài khoản theo số dư
def classify_balance(balance):
    if balance > 100000:
        return 'Viotp_over_100k.txt'
    elif balance > 10000:
        return 'Viotp_over_10k.txt'
    elif balance >= 1000:
        return 'Viotp_under_10k.txt'
    else:
        return 'Viotp_under_1k.txt'

# Đọc danh sách tài khoản từ file
def read_accounts(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as log_file:
            return [account.strip() for account in log_file.readlines()]
    except Exception as e:
        print(f"Error reading accounts: {e}")
        return []

# Lưu lại danh sách tài khoản còn lại
def save_accounts(filename, accounts):
    try:
        with open(filename, 'w', encoding='utf-8') as log_file:
            log_file.write('\n'.join(accounts) + '\n')
    except Exception as e:
        print(f"Error saving accounts: {e}")

# Hàm mở lại tài khoản
def reopen_code(account):
    driver = webdriver.Chrome(executable_path="./chromedriver", options=configure_chrome_options())
    process_single_account(driver, account)
    driver.quit()

# Chương trình chính
if __name__ == "__main__":
    accounts = ["0378588867:160299"]
    print(f"[+] Thành công: {login_count}")
    print(f"[!] Thất bại: {thatbai_count}")
    print(f"[+] Tổng số acc viotp trên 10k: {viotp_over_10k}")
    print(f"[+] Tổng số acc viotp dưới 10k: {viotp_under_10k}")
    print(f"[+] Tổng số acc dưới 1k: {viotp_under_1k}")
    account = accounts.pop(0)
    reopen_code(account)
    save_accounts(accounts_file, accounts)
