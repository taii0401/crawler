# -*- coding: utf-8 -*-
"""
共用函式
"""

#取得數字和字母隨機位數
def getRandom(num):
    import random
    ran_str = ""
    for i in range(0,num): 
        #定義一個隨機範圍，去猜i的值。
        current = random.randint(0,num) 
        if current == i:                                
            #生成一個隨機的數字
            current_code = random.randint(0,9)
        else:                                           
            #生成一個隨機的字母，這裡一定要主義chr（）轉換一下
            current_code = chr(random.randint(65,90))
        ran_str += str(current_code)
    
    return ran_str




######################資料庫共用函式######################
#檢查資料庫連線
def checkDbLink(db_name):
    import pymysql
    
    dbhost = "localhost"
    dbuser = "root"
    dbpass = "root"
    dbname = db_name
    dbport = 3306
    
    try:
        db_conn = pymysql.connect(host=dbhost,port=dbport,user=dbuser,password=dbpass,database=dbname)
        #print("連接資料庫成功")
        return True,db_conn
    except pymysql.Error as e:
        #print("連接資料庫失敗："+str(e))
        return False,e

#取得最後編號
def getSerial(db_name,table_name):
    #檢查資料庫連線
    isSuccess,db_conn = checkDbLink(db_name)
    if isSuccess:
        serial_num = 0
        with db_conn.cursor() as cursor:
            sql = "SELECT serial_num FROM "+table_name+" ORDER BY serial_num DESC"
            cursor.execute(sql)
            if cursor.rowcount > 0:
                data = cursor.fetchone()
                #print(data)
                serial_num = data[0]
        
        #print(serial_num)
        return serial_num
    else:
        print("連接資料庫失敗")
    
    #關閉資料連線
    db_conn.close()
    

#資料寫入
def saveDataToBooks(db_name,datas):
    import uuid
    import datetime
    
    #檢查資料庫連線
    isSuccess,db_conn = checkDbLink(db_name)
    #建立時間
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if isSuccess:
        #print("連接資料庫成功")
        with db_conn.cursor() as cursor:
            #資料表名稱
            table_name = db_name+"_books"
            #新增
            sql_insert = "INSERT INTO "+table_name+" (uuid,serial_code,serial_num,serial,name,author,office,date,price,sales,content,category,account,img_name,create_time,modify_time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            #更新
            sql_update = "UPDATE "+table_name+" SET price = %s,sales = %s,content = %s,category = %s,img_name = %s,modify_time = %s WHERE id = %s"
            
            for data in datas:
                #定價
                data["book_price"] = int(data["book_price"])
                #優惠價
                data["book_sales"] = int(data["book_sales"])
                #取得最後編號
                serial_num = int(getSerial(db_name,table_name))
                serial_num = serial_num+1
                #編號
                serial = "B"+str(serial_num).zfill(4)
                
                if "book_id" in data: #更新
                    sql = sql_update
                    args = (data["book_price"],data["book_sales"],data["book_content"],data["book_category"],data["book_img_name"],now,int(data["book_id"]))
                else: #新增
                    sql = sql_insert
                    args = (uuid.uuid4(),"B",serial_num,serial,data["book_name"],data["book_author"],data["book_office"],data["book_date"],data["book_price"],data["book_sales"],data["book_content"],data["book_category"],"admin",data["book_img_name"],now,now)
                
                
                try:
                    cursor.execute(sql,args)
                    db_conn.commit()
                    print("新增成功")
                except:
                    db_conn.rollback()
                    print("新增失敗")
    else:
        print("連接資料庫失敗")
    
    #關閉資料連線
    db_conn.close()