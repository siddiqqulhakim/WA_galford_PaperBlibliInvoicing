from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import string
import csv
from time import sleep
import pandas as pd
import datetime
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

def option_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("start-maximized")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--incognito")
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--disable-infobars")
        
    options.add_experimental_option("prefs",{'credentials_enable_service': False, 'profile': {'password_manager_enabled': False}})
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])

    return options

def paper_id(driver, paper_username, paper_password, array_price):
    
    try:
        print("LOGIN TO PAPER.iD")
        driver.get("https://www.paper.id/webappv1/#/invoicer/finance/digital-payment-out/payout")
        sleep(5)

        driver.find_element(By.CSS_SELECTOR, "input[name='email']").send_keys(paper_username)
        driver.find_element(By.CSS_SELECTOR, "button[data-cy='submit']").click()
        sleep(2)
        driver.find_element(By.CSS_SELECTOR, "input[data-cy='password']").send_keys(paper_password)
        driver.find_elements(By.CSS_SELECTOR, "button[data-cy='submit']")[1].click()
        sleep(3)

        print("CREATE PAYMENT CODE ON PAPER.ID")
        kode_pembayaran = []
        for price in array_price:
            driver.get("https://www.paper.id/webappv1/#/invoicer/finance/digital-payment-out/payout")
            driver.refresh()
            sleep(3)
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ng-select[role='listbox']"))).click()
            
            sleep(2)
            driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//*[contains(text(),'supplier01')]"))
            sleep(2)
            driver.find_element(By.ID, "payout-step5").click()
            sleep(3)

            random_string = ''.join(random.choice(string.ascii_uppercase) for i in range(5))

            driver.find_element(By.ID, "item_name").send_keys(random_string)
            driver.find_element(By.ID, "item_description").send_keys(random_string)
            driver.find_element(By.ID, "quantity").send_keys(1)
            driver.find_element(By.ID, "price").send_keys(price)
            sleep(1)
            driver.find_element(By.ID, "payout-step8").click()
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "payout-step9"))).click()

            sleep(3)
            driver.execute_script("arguments[0].click();", WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Mitra Pembayaran Digital')]"))))
            driver.execute_script("arguments[0].click();", WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "blibli"))))
            sleep(2)
            driver.find_element(By.CLASS_NAME, "paper-button.blue-button.confirmation-button").click()
            sleep(3)
            temp = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "font-20.ng-star-inserted"))).text
            kode_pembayaran.append(temp)

        print("LIST PAYMENT CODE : " + kode_pembayaran)
        return kode_pembayaran
   
    except Exception as e: 
        print('ERROR HAPPEN : ' + str(e))
        paper_id(driver, paper_username, paper_password, array_price)

def login_blibi(driver, email, password):
    print("LOGIN TO BLIBLI")
    driver.get("https://www.blibli.com/login")
    sleep(2)

    driver.find_element(By.CSS_SELECTOR, "input[class='form__input login__username']").send_keys(email)    
    driver.find_element(By.CSS_SELECTOR, "input[class='form__input login__password']").send_keys(password)
    sleep(2)

    driver.find_element(By.CLASS_NAME, "blu-btn.b-full-width.b-secondary").click()

    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Email/nomor HP-nya tidak valid')]")))
        return 'FAILED LOGIN BLIBLI, MESSAGE : Email/nomor HP-nya tidak valid'
    except:
        pass

    #Pilih button kirim verifikasi
    email_services = email.split('@')[1]
    driver.execute_script("arguments[0].click();", WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'"+email_services+"')]"))))

    sleep(30)
    return ''

def login_email(email, password, failed=0):
    if failed > 2:
        return "LOGIN FAILED 3 TIMES"
    else:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=option_driver())
        try:    
            kode_verifikasi = ''

            if 'gmail' in email:
                driver.get("https://accounts.google.com/v3/signin/identifier?continue=https%3A%2F%2Fmail.google.com%2Fmail%2F&rip=1&sacu=1&service=mail&flowName=GlifWebSignIn&flowEntry=ServiceLogin")    
                sleep(5)

                driver.find_element(By.CSS_SELECTOR, "input[name='identifier']").send_keys(email)
                driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//*[contains(text(),'Next')]"))
                sleep(3)
                driver.find_element(By.CSS_SELECTOR, "input[name='Passwd']").send_keys(password)
                driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//*[contains(text(),'Next')]"))
                sleep(7)

                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Verifikasi diri Anda')]")))
                    return email + ': CANNOT LOGIN WITH THIS ACCOUNT BECAUSE NEED VERIFICATION CODE'
                except:
                    pass

                try:
                    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//*[contains(text(),'Jangan sekarang')]"))
                except:
                    pass

                try:
                    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//*[contains(text(),'Not now')]"))
                except:
                    pass

                try:
                    driver.execute_script("arguments[0].click();", WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span/*[contains(text(),'Verifikasi untuk masuk')]"))))
                except:
                    error = driver.find_element(By.XPATH, "//*[contains(text(),'Tidak dapat membuat Anda login')]").text
                    print("Account : " + email + " Tidak dapat membuat Anda login")
                    return "Account : " + email + " Tidak dapat membuat Anda login"
                
                sleep(3)
                driver.refresh()
                sleep(3)
                kode_verifikasi = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, '//strong[contains(@style, "font-size:24px")]')))[-1].text

                print("Email verification code : " + kode_verifikasi)

            elif 'yahoo' in email:
                driver.get('https://login.yahoo.com/?.src=ym&activity=mail-direct&.lang=en-US&.intl=us&.done=https%3A%2F%2Fmail.yahoo.com%2Fd%2F')
                sleep(3)

                driver.find_element(By.CSS_SELECTOR, 'input[name="username"]').send_keys(email)
                driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR, 'input[id="login-signin"]'))
                sleep(3)

                driver.find_element(By.CSS_SELECTOR, 'input[name="password"]').send_keys(password)
                driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR, 'button[id="login-signin"]'))
                sleep(7)

                try:
                    driver.execute_script("arguments[0].click();", WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Verifikasi untuk masuk')]"))))      
                    
                    sleep(3)
                    driver.refresh()
                    sleep(3)
                    kode_verifikasi = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, '//strong[contains(@style, "font-size:24px")]')))[-1].text
                    print("Email verification code : " + kode_verifikasi)
                except Exception as e:
                    driver.execute_script("arguments[0].click();", WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Verifikasi untuk masuk')]"))))      
                    
                    sleep(3)
                    driver.refresh()
                    sleep(3)
                    kode_verifikasi = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, '//strong[contains(@style, "font-size:24px")]')))[-1].text
                    print("Email verification code : " + kode_verifikasi)

            elif 'outlook' in email:
                driver.get('https://login.live.com/login.srf?wa=wsignin1.0&wreply=https%3a%2f%2foutlook.live.com%2fowa')
                sleep(5)

                driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys(email)
                driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]'))
                sleep(3)

                driver.find_element(By.CSS_SELECTOR, 'input[name="passwd"]').send_keys(password)
                driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]'))
                sleep(3)

                try:
                    driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]'))
                    sleep(3)
                except Exception as e:
                    pass            
                
                try:
                    driver.execute_script("arguments[0].click();", WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Verifikasi untuk masuk')]"))))      
                    
                    sleep(3)
                    driver.refresh()
                    sleep(3)
                    kode_verifikasi = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, '//strong[contains(@style, "font-size:24px")]')))[-1].text
                    print("Email verification code : " + kode_verifikasi)
                except Exception as e:
                    driver.execute_script("arguments[0].click();", WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Verifikasi untuk masuk')]"))))      
                    
                    sleep(3)
                    driver.refresh()
                    sleep(3)
                    kode_verifikasi = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, '//strong[contains(@style, "font-size:24px")]')))[-1].text
                    print("Email verification code : " + kode_verifikasi)

            driver.quit()
            return kode_verifikasi
        
        except Exception as e:
            driver.quit()
            print("FAILED LOGIN EMAIL, RE-TRYING")
            login_email(email, password, failed+1)

def blibli_input_verif(driver, kode_verifikasi):
    print('BACK TO BLIBLI AND INPUT VERIFICATION CODE')

    for kode in kode_verifikasi:
        driver.find_element(By.CSS_SELECTOR, ".otp__textField.not-active").send_keys(kode)
        sleep(0.5)
    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//*[contains(text(),'Verifikasi')]"))
    sleep(5)
    
    try:
        error = driver.find_element(By.CLASS_NAME, "ticker__content.tx-error").text
        if error:
            print('ERROR HAPPEN, CANNOT LOGIN TO BLIBLI, RE-TRYING')
            return 'ERROR'
    except:
        return ''
    

def proses(driver, email, mode_pembayaran, kode_pembayaran, is_voucher, username_klikBCA):    
    try:

        print('PROCESS INVOICE PAYMENT ON BLIBLI')
            
        for kode in kode_pembayaran:
            driver.get("https://www.blibli.com/digital/p/invoicing/paper-id")
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "textbox-nopel"))).send_keys(kode)
            sleep(1)
            driver.find_element(By.ID, "btn-info").click()
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "btn-payNow"))).click()
            sleep(5)

            if mode_pembayaran == 1:
                driver.execute_script("arguments[0].click();", WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "label[for='InternetBanking']"))))
                driver.execute_script("arguments[0].click();", WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "blu-dropdown__trigger"))))
                sleep(1.5)
                driver.execute_script("arguments[0].click();", WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//label[contains(text(),'KlikBCA')]"))))
                sleep(1.5)
                driver.find_element(By.CSS_SELECTOR, "input[placeholder='User ID KlikBCA anda']").send_keys(username_klikBCA)
                sleep(3)

                if is_voucher == 1:
                    try:
                        print("Trying to select voucher")
                        driver.execute_script("arguments[0].click();", driver.find_element(By.CLASS_NAME, "voucher__arrow"))
                        sleep(2)
                        driver.find_element(By.CSS_SELECTOR, "div.blu-card__content.coupon__code.member > div > a").click()
                        sleep(3)
                    except:
                        pass

                try:
                    driver.execute_script("arguments[0].click();", driver.find_element(By.CLASS_NAME, "blu-btn.buyNow--btn.b-primary"))
                except:
                    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//button[contains(text(),'Bayar sekarang')]"))
                sleep(7)
            
            elif mode_pembayaran == 2:
                driver.execute_script("arguments[0].click();", WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "label[for='Transfer']"))))
                driver.execute_script("arguments[0].click();", WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Opsi pembayaran')]"))))
                driver.execute_script("arguments[0].click();", WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Bank BCA')]"))))
                sleep(2)

                if is_voucher == 1:
                    try:
                        print("TRYING TO SELECT VOUCHER")
                        driver.execute_script("arguments[0].click();", driver.find_element(By.CLASS_NAME, "voucher__arrow"))
                        sleep(2)
                        driver.find_element(By.CSS_SELECTOR, "div.blu-card__content.coupon__code.member > div > a").click()
                        sleep(3)
                    except:
                        pass

                try:
                    driver.execute_script("arguments[0].click();", driver.find_element(By.CLASS_NAME, "blu-btn.buyNow--btn.b-primary"))
                except:
                    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//button[contains(text(),'Bayar sekarang')]"))

                kode_va = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "order-status__payment-code-values__value"))).text
                
                data_csv = []
                data_csv.append(email)
                data_csv.append(kode_va)
                with open("data_VABCA.csv", "a+", newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(data_csv)

                sleep(5)

    except Exception as e:
        print('ERROR HAPPEN : ' + str(e))
        proses(driver, email, mode_pembayaran, kode_pembayaran, is_voucher, username_klikBCA)

def blibi_change_birth(driver):
    driver.get('https://www.blibli.com/member/profile')
    sleep(3)

    next_date = datetime.datetime.now() + datetime.timedelta(days=1)
    bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']

    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//label[contains(text(),'Laki-Laki')]"))

    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//label[contains(text(),'Tahun')]"))
    sleep(1.5)
    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//label[contains(text(),'1990')]"))
    sleep(1.5)

    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//label[contains(text(),'Bulan')]"))
    sleep(1.5)
    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//label[contains(text(),'"+bulan[next_date.month-1]+"')]"))
    sleep(1.5)

    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//label[contains(text(),'Hari')]"))
    sleep(1.5)
    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//label[contains(text(),'"+str(next_date.day)+"')]"))
    sleep(1.5)

    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//div[contains(text(),'Simpan')]"))
    sleep(5)

if __name__ == '__main__':
    df = pd.read_csv("PaperBlibliInvoice_account.csv", header=0)
    print(df)

    infile = open('PaperBlibliInvoice_setting.txt', 'r')
    firstLine = infile.readline()
    paper_username = firstLine.split(';')[0]
    paper_password = firstLine.split(';')[1]
    username_klikBCA = firstLine.split(';')[2]

    print("\nCek angka paling kiri dari tabel diatas")

    # index = 34
    # start = int(input("Mulai dari akun ke? "))
    # end = int(input("Sampai akun ke? "))
    # mode_pembayaran = int(input("Masukan mode pembayaran (1. KlikBCA | 2. Virtual Account BCA) ? "))
    # total_payment_code = int(input("Masukan total kode yang ingin diproses oleh setiap akun ? "))
    # is_voucher = int(input("Apakah menggunakan voucher (1. Iya | 2. Tidak) ? "))
    # array_price = []
    # for i in range(total_payment_code):
    #     array_price.append(int(input("Masukan nominal ke-" + str(i+1) + " : ")))

    # for index in range(start, end+1):
    #     driver = webdriver.Chrome(ChromeDriverManager().install(), options=option_driver())
    #     kode_pembayaran = paper_id(driver, paper_username, paper_password, array_price)
    #     proses(driver, df, index, mode_pembayaran, kode_pembayaran, is_voucher, username_klikBCA, 0)
    #     blibi_change_birth(driver)
    #     driver.quit()

    start = 16
    end = 16
    
    for index in range(start, end+1):
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=option_driver())
        login_blibli_result = login_blibi(driver, df["Email"][index], df["Pass Email"][index])
        if 'FAILED LOGIN BLIBLI' in login_blibli_result:
            print(login_blibli_result)
            print('CONTINUE TO NEXT ACCOUNT')
            driver.quit()
            continue
        else:
            kode_verifikasi = login_email(df["Email"][index], df["Pass Email"][index])
            if 'CANNOT LOGIN WITH THIS ACCOUNT' in kode_verifikasi:
                print (kode_verifikasi)
                print('CONTINUE TO NEXT ACCOUNT')
                driver.quit()
                continue
            else:
                blibli_input_verif(driver, kode_verifikasi)
                blibi_change_birth(driver)

    k = input("\nPress enter to exit...")