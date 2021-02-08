from pynotifier import Notification
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support import ui
from time import time, sleep, ctime
import re
import tkinter
import tkinter.messagebox
import pandas
import sqlite3

def saveToDb(data, dbname, tablename):
    with sqlite3.connect(dbname) as db:
        data.to_sql(tablename, con = db, if_exists = 'replace')

def readFromDb(dbname, tablename):
    with sqlite3.connect(dbname) as db:
        return pandas.read_sql_query('SELECT * FROM {tablename}'.format(tablename = tablename), db)

def delDataInDb(dbname, tablename):
    with sqlite3.connect(dbname) as db:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM {tablename}'.format(tablename=tablename))
        db.commit()
        cursor.close()

def IsDbTableExist(dbname, tablename):
    with sqlite3.connect(dbname) as db:
        c = db.cursor()
        c.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{tablename}'".format(tablename = tablename))
        if c.fetchone()[0]==1 : 
            return True
        return False

def windows_nodify(msg):
    root = tkinter.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", 1) 
    root.focus() 
    tkinter.messagebox.showinfo('訂餐',msg)
    root.destroy()

def fetch_bandon(url):

    username = "user"
    password = "password"

    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    option.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=option)
    driver.get(url)
    
    ui.WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "username")))
    driver.find_element_by_name("username").send_keys(username)
    driver.find_element_by_name("password").send_keys(password)
    ques = driver.find_elements_by_class_name("alignRight")[2].text
    temp = re.findall(r"\d+\.?\d*", ques)
    answer = int(temp[0]) + int(temp[1])
    driver.find_element_by_name("result").send_keys(answer)
    driver.find_element_by_name("submit").click()
    
    ui.WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[2]/div/div[1]/div/div[2]")))
    rows = driver.find_elements_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div[1]/div/div[2]")

    if len(rows) == 0:
        driver.close()
        return list()
    
    menu = rows[0].text.replace('管理…\n','').replace('»我也要訂','').replace(' 發起的 ','\n').split('\n')
    menu.append('0')
    
    counter = 0
    string = ""
    tmp = []
    final = []
    for row in menu:
        if row.isnumeric():
            tmp.append(string)
            counter = 0
            string = ""
            final.append(tmp)
            tmp=[]
            tmp.append(row)
        else:
            counter = counter+1
            if counter > 3 :
                string = string + str(row) + " #"
            else:
                tmp.append(row)
    del final[0]

    print(ctime())
    order = pandas.DataFrame (final,columns=['People','Price','Date','Title','Note'])
    order.sort_values(by=['Date'], inplace=True)
    print(order.to_string(index=False))
    
    driver.quit()
        
    return order

def main():
    url = 'https://dinbendon.net/do/login'
    dbname = 'order.sqlite'
    tablename = 'dinbandon'
    order = fetch_bandon(url)
    
    if order is None or len(order) == 0:
        print("目前沒有進行中的訂單\n")
        return False

    if IsDbTableExist(dbname, tablename) is False:
        print('資料庫無過往訂單，即將儲存目前訂單並退出\n')
        saveToDb(order, dbname, tablename)
        return False
    
    oldOrder = readFromDb(dbname, tablename)

    orderList = list(order['Title'])
    oldOrderList = list(oldOrder['Title'])

    delDataInDb(dbname, tablename)
    saveToDb(order, dbname, tablename)

    if oldOrder is None or len(oldOrder) == 0:
        print('資料庫無過往訂單\n')
    elif orderList == oldOrderList or len(orderList) < len(oldOrderList):
        print("訂單無變動\n")
    else:
        print("偵測到訂單變動！\n")
        windows_nodify(order.to_string(columns=['People','Price','Date','Title'],index=False))
    return True
    

if __name__ == '__main__':
    while True:
        main()
        sleep(900 - time() % 900)
        