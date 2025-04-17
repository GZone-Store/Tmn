from flask import Flask, request, render_template
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os

app = Flask(__name__, template_folder="templates")

MY_PHONE_NUMBER = "0610876729"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/redeem', methods=['POST'])
def redeem_truemoney():
    link = request.form.get('link')

    if not link or not link.startswith("https://gift.truemoney.com/campaign/"):
        return render_template('index.html', result={"status": "error", "message": "ลิงก์ไม่ถูกต้อง"})

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(link)
        time.sleep(2)

        phone_input = driver.find_element(By.NAME, 'mobile')
        phone_input.send_keys(MY_PHONE_NUMBER)
        time.sleep(1)

        submit_btn = driver.find_element(By.CLASS_NAME, 'btn')
        submit_btn.click()
        time.sleep(2)

        page_source = driver.page_source

        if "รับเงินสำเร็จ" in page_source:
            status, message = "success", "รับเงินเรียบร้อยแล้ว"
        elif "ซองนี้หมดอายุแล้ว" in page_source:
            status, message = "expired", "ซองหมดอายุแล้ว"
        elif "มีคนรับซองนี้ไปแล้ว" in page_source:
            status, message = "used", "ซองถูกใช้ไปแล้ว"
        elif "ไม่พบซองนี้ในระบบ" in page_source:
            status, message = "invalid", "ลิงก์ไม่ถูกต้องหรือไม่มีอยู่จริง"
        else:
            status, message = "unknown", "ไม่สามารถระบุสถานะได้"

        return render_template('index.html', result={"status": status, "message": message})

    except Exception as e:
        return render_template('index.html', result={"status": "error", "message": str(e)})
    finally:
        driver.quit()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
