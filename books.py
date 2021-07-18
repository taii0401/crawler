# -*- coding: utf-8 -*-
"""
網路爬蟲
自動取得博客來電腦程式的書籍，並存入資料表
"""

import sys,os,requests,time
import pandas as pd


from bs4 import BeautifulSoup
from selenium import webdriver
from db_init import *


#圖片儲存路徑
save_path = "books_imgs/"

#開啟分頁
page_reamining = True
page_num = serial = 1
page_i = 10

#所有資料
datas = []

url = "https://www.books.com.tw/web/books_bmidm_1906/?o=1&v=1&page=2"
driver = webdriver.Chrome("chromedriver")
time.sleep(5)
driver.implicitly_wait(1000)
driver.get(url)

while page_reamining:
    sp = BeautifulSoup(driver.page_source,"lxml")
    sp.prettify()
    
    rows = sp.find_all("div",class_="msg")
    #print(rows)
    
    i = 0
    for row in rows:
        if i == 2:
            break
        
        #單筆資料
        list_data = {}
        list_data["serial"] = serial

        print("===========START 抓取資料===========")
        #書名
        book_name = row.find("a").text
        list_data["book_name"] = book_name
        
        row_li = row.find("li",class_="info")
        #作者
        book_author = row_li.find("a").text
        list_data["book_author"] = book_author
        #出版社
        book_office = row_li.find("span").find("a").text
        list_data["book_office"] = book_office
        #出版日期
        span_text = row_li.find("span").text.split("：")
        book_date = span_text[1]
        list_data["book_date"] = book_date
        
        
        book_img_name = "" #圖片名稱
        book_price = book_sales = 0 #定價、優惠價
        book_content = book_category = "" #內容簡介、目錄
        
        #詳細頁面連結
        book_link = row.find("a").get("href")
        print(book_link)
        
        r = requests.get(book_link)
        time.sleep(5)
        
        if r.status_code == 200:
            sp_detail = BeautifulSoup(r.text,"lxml")
            sp_detail.prettify()
            
            print("已取得內容頁面！")
            
            book_price_ul = sp_detail.find("ul",class_="price")
            book_price_lis = book_price_ul.find_all("li")
            
            #定價
            book_price_all = book_price_lis[0].text.split("：")
            book_price = book_price_all[1].replace("元","")
            #print(book_price)
            
            #優惠價
            book_sales_alls = book_price_lis[1].text.split("：")
            if "折" in book_sales_alls[1]:
                book_sales_all = book_sales_alls[1].split("折")
                book_sales = book_sales_all[1].replace("元","")
            else:
                book_sales = book_sales_alls[1].replace("元","")
            #print(book_sales)
            
            #內容簡介、目錄
            div_contents = sp_detail.find_all("div",class_="type02_m057")
            #print(div_contents)
            for div_content in div_contents:
                h3 = div_content.find("h3")
                content = div_content.find("div",class_="content").text
                #content = content.replace("\xa0","").replace("\t","").replace(" ","")
                if h3.text == "內容簡介":
                    book_content = content
                elif h3.text == "目錄":
                    book_category = content
            #print(book_content)
            #print(book_category) 
            
            
            #取得最後編號
            book_serial_num = int(getSerial("proweb","proweb_books"))
            book_serial_num = book_serial_num+1
            #編號
            book_serial = "B"+str(book_serial_num).zfill(4)
            
            
            ###圖片###
            img_link = "";
            cover_img = sp_detail.find("img",class_="M201106_0_getTakelook_P00a400020052_image_wrap")
            if cover_img.has_attr("src"):
                img_link = cover_img["src"]
                img_r = requests.get(img_link)
                #圖片名稱
                now = time.strftime("%Y%m%d%H%M%S",time.localtime())
                #隨機產生6位屬
                ran_str = getRandom(6)
                book_img_name = now+ran_str
                file_name = os.path.join(save_path,book_img_name+".jpg")
                #wb => 讀寫二進制文件
                with open(file_name,"wb") as f:
                    f.write(img_r.content)
            else:
                book_img_name = "無法取到圖片！"
                print("無法取到圖片！")
            
        else:
            print("無法取到內容頁面！")
            content = "無法取到內容頁面！"
        
        
        list_data["book_price"] = book_price #定價
        list_data["book_sales"] = book_sales #優惠價
        list_data["book_content"] = book_content #內容簡介
        list_data["book_category"] = book_category #目錄
        list_data["book_img_name"] = book_img_name #圖片名稱
        
        print(list_data)
        
        datas.append(list_data)
        #datas[serial] = list_data
        
        print("===========END 抓取資料===========")
        i += 1
        serial += 1
        #print(list_data)
        #sys.exit(0)
    
    #換頁
    try:
        if page_num < 1:
            print("===========換下一頁===========")
            a = []
            a.append(page_i)
            
            #xath://*[@id="index-page"]/body/div[4]/div[1]/div[2]/div[2]/div[1]/div/div[126]/div/a[10]
            xpath_link = "//*[@id='index-page']/body/div[4]/div[1]/div[2]/div[2]/div[1]/div/div[126]/div/a"+str(a)
            next_link = driver.find_element_by_xpath(xpath_link)
            next_link.click()
            time.sleep(5)
            
            
            page_num = page_num+1
            page_i = page_i+1
        else:
            #關閉分頁
            page_reamining = False
    except Exception:
        #關閉分頁
        page_reamining = False

#關閉driver
driver.quit()
#print(datas)

#sys.exit(0)


#匯出CSV
cols = ["serial","book_name","book_author","book_office","book_date","book_price","book_sales","book_content","book_category","book_img_name"]
col_names = {"serial":"編號","book_name":"書名","book_author":"作者","book_office":"出版社","book_date":"出版日期","book_price":"定價","book_sales":"優惠價","book_content":"內容簡介","book_category":"目錄","book_img_name":"圖片名稱"}
#books = pd.DataFrame(columns=cols,data=datas)
books = pd.DataFrame(datas)
#將標題轉換成文字
books.rename(columns=col_names,inplace=True)
books.to_csv("books.csv",index=False,encoding="utf-8-sig")
#匯出JSON
#books.to_json("books.json")


#存入mysql
print("===========START 存入資料庫===========")
saveDataToBooks("proweb",datas)
print("===========END 存入資料庫===========")

