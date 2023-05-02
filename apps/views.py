from django.shortcuts import render,HttpResponse,redirect
import mysql.connector
from django.conf import settings
from django.core.mail import send_mail
from cryptography.fernet import Fernet
from datetime import date
Address = "No.5, Cholan Street, \nRedhills,\nChennai - 600052,\nTamil Nadu, India"
code = "<center><h1>Invalid Session</h1><br> <a href = '/login'>Login Page</a></center>"
key = Fernet.generate_key()
fernet = Fernet(key)

def dbconnect():
    dataBase = mysql.connector.connect(
        host ="localhost",
        user ="root",
        passwd ="admin",
        database = "circuiters"
    )
    return dataBase

def toencrpyt(message):
    print(message)
    enmsg = fernet.encrypt(message.encode())
    return enmsg

def mailsent(subject,message,email):
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email, ]
    send_mail( subject, message, email_from, recipient_list )

def inactive(request):
    dataBase = dbconnect()
    c = dataBase.cursor()
    sql = f"select * from users where flag = '0';"
    c.execute(sql)
    t = c.fetchall()
    if t == []:
        pass
    else:
        ld = t[0][7]
        today = str(date.today())
        sql = f"delete from users where flag = '0' and updated_on < '{today}';"
        c.execute(sql)
        dataBase.commit()
def validate(request):
    try:
        print(request.session['value'])
        return True
    except:
        return False

def logout(request):
    c = False
    l = False
    try:
        del request.session['value']
        request.session['lmsg'] = "Logged out successfully !"
    except:
        print("unable to delete the session value")
    try:
        del request.session['loginmsg']
    except:
        pass
    return redirect(login)

def login(request):
    try:
        l = request.session['lmsg']
    except:
        l = False
    if request.method == 'POST':
        email = request.POST['email']
        pwd = request.POST['pwd']
        if email =='admin@a.com' and pwd == 'admin':
            request.session['value'] = "admin"
            return redirect(admin)
        dataBase = dbconnect()
        c = dataBase.cursor()
        sql = f"select * from users where Email = '{email}';"
        c.execute(sql)
        t = c.fetchall()
        if t == []:
            c = 'Email not registered with us'
            return render(request,"login.html",{'msg':c,'lmsg':l})
        else:
            if t[0][5] != 1:
                print("hida",t)
                c = 'Account is not confirmed. Kindly check you email inbox'
                return render(request,"login.html",{'msg':c,'lmsg':l})
            elif t[0][4] == pwd:
                request.session['value'] = [t[0][0] , t[0][1] ]
                #print(t)
                request.session['loginmsg'] = f"Logged in as {t[0][1]}"
                return redirect(index)
            else:
                c = 'Incorrect Password '
                return render(request,"login.html",{'msg':c,'lmsg':l})
    return render(request,"login.html",{'msg':False,'lmsg':l})

def index(request):
    id = ""
    try:
        v = request.session['value']
        value =v[1]
        id = v[0]
        msg = request.session['loginmsg']
    except:
        value = False
        data = False
        try:
            msg = request.session['loginmsg']
        except:
            msg=False

    if value != False:
        dataBase = dbconnect()
        c = dataBase.cursor()
        sql = f"select * from details where id = '{id}' order by order_id desc;"
        c.execute(sql)
        t = c.fetchall()
        if t == []:
            data = False
        else:
            data = list()
            lt  = 10
            if len(t)<10:
                lt = len(t)
            for i in range(0,lt):
                temp = dict()
                temp["device_name"] = t[i][1]
                temp["model"] = t[i][2]
                temp["status"] = t[i][4]
                temp["adds"] = t[i][7]
                temp["oid"] = t[i][0]
                data.append(temp)
                print(data)
        if request.method == 'POST':
            n = request.POST['named']
            model = request.POST['model']
            rd = request.POST['rd']
            adds = request.POST['adds']
            sql = f"insert into details (device_name,model,message,id,flag,address) values('{n}','{model}','{rd}','{id}','uc','{adds}');"
            c.execute(sql)
            dataBase.commit()
            request.session['loginmsg'] = "Your Order Was Placed successfully"
            return redirect(index)
    else:
        if request.method == 'POST':
            name = request.POST['name']
            email = request.POST['email']
            phone = request.POST['phone']
            message = request.POST['message']
            dataBase = dbconnect()
            c = dataBase.cursor()
            sql = f"insert into contact (name,email,phone,message) values('{name}','{email}','{phone}','{message}');"
            print(sql)
            c.execute(sql)
            dataBase.commit()
            request.session['loginmsg'] = "Sumbitted successfully "
            msg = request.session['loginmsg']
            return redirect(index)
    return render(request,"index.html",{'value':value,'data':data,'id':id,'msg':msg})

def signup(request):
    try:
        m = request.session['signup']
    except:
        m = False
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        pwd = request.POST['pwd']
        cpwd = request.POST['cpwd']
        try:
            c = int(phone)
        except:
            request.session['signup'] = "Invalid Phone Number"
            return redirect(signup)
        if pwd != cpwd :
            m = "Password and Confirm password should be same"
        elif len(pwd) < 8:
            m = "Password should have minimum 8 characters"
        elif len(phone) !=10:
            m = "Phone number should have 10 digits"
        else:
            dataBase = dbconnect()
            c = dataBase.cursor()
            ch = f"select * from users where Email = '{email}' or Phone = '{phone}';"
            c.execute(ch)
            t = c.fetchall()
            if t == []:
                link = hash(email)
                sql = f"insert into users (Name,Email,Phone,Password,flag,temp) values('{name}','{email}','{phone}','{pwd}','0','{link}');"
                c.execute(sql)
                dataBase.commit()
                request.session['lmsg'] = "Confirm Link sent to the registered mail Id.Link will be expired within 24 hours"
                subject = "Welcome to Circuiters "
                name=name.replace(" ","")
                message = f"Hi {name}, \n\nThank you for registering in Circuiters.\nKindly click the link to confirm \n\nhttp://localhost:8000/confirm/{email}/{link} \n\nThe Above link will expire within 24 Hours \n\nRegards, \nCircuiters"
                mailsent(subject,message,email)
                return redirect(login)
            else:
                m = "Email Id or Phone Number was alreday registered with us "
    return render(request,"signup.html",{'msg':m})

def info(request):
    return render(request,"info.html")

def admin(request):
    inactive(request)
    v = validate(request)
    if v == False:
        return HttpResponse(f"{code}")
    dataBase = dbconnect()
    c = dataBase.cursor()
    #message list
    sql = f"select * from contact order by id desc;"
    c.execute(sql)
    t = c.fetchall()
    data = []
    for i in range(0,len(t)):
        temp = dict()
        temp['name'] = t[i][1]
        temp['email'] = t[i][2]
        temp['phone'] = t[i][3]
        temp['message'] = t[i][4]
        data.append(temp)
        print(i)
        if i>=9:
            break
    #users list
    sql = f"select * from users where flag = '1' order by id desc;"
    c.execute(sql)
    t = c.fetchall()
    data1 = []
    for i in range(0,len(t)):
        temp = dict()
        sql = f"select * from details where id = '{t[i][0]}' and flag = 'uc' ;"
        c.execute(sql)
        r = c.fetchall()
        sql = f"select * from details where id = '{t[i][0]}' and flag = 'inp' ;"
        c.execute(sql)
        inp = c.fetchall()
        temp['name'] = t[i][1]
        temp['email'] = t[i][2]
        temp['id'] = t[i][0]
        temp['uc'] = len(r)
        temp['inp'] = len(inp)
        data1.append(temp)
        if i>=9:
            break
    return render(request,"admin.html",{'data':data,'data1':data1})

def pag(l):
    temp = list()
    r =l%10
    count = l//10
    if r>0:
        count+=1
    for i in range(1,count+1):
        temp.append(i)
    return temp

def cmsg(request,length):
    v = validate(request)
    if v == False:
        return HttpResponse(f"{code}")
    
    dataBase = dbconnect()
    c = dataBase.cursor()
    sql = f"select * from contact order by id desc;"
    c.execute(sql)
    t = c.fetchall()
    data = []
    #print(t)
    if length > 0:
        length = (length-1)*10
    print(length)
    for i in range(length,length+10):
        #print(i)
        if i>=len(t):
            break
        temp = dict()
        temp['name'] = t[i][0]
        temp['email'] = t[i][1]
        temp['phone'] = t[i][2]
        temp['message'] = t[i][3]
        data.append(temp)
    pg = pag(len(t))
    print(pg)
    return render(request,"cmsg.html",{'data':data,'num':pg})

def urec(request,id,length):
    v = validate(request)
    if v == False:
        return HttpResponse(f"{code}")
    
    dataBase = dbconnect()
    c = dataBase.cursor()
    sql = f"select * from details where id = '{id}' order by order_id desc;"
    c.execute(sql)
    t = c.fetchall()
    data = []
    if length > 0:
        length = (length-1)*10
    print(length)
    for i in range(length,length+10):
        #print(i)
        if i>=len(t):
            break
        temp = dict()
        temp['dname'] = t[i][1]
        temp['model'] = t[i][2]
        temp['message'] = t[i][3]
        temp['status'] = t[i][4]
        temp['adds'] = t[i][7]
        temp['oid'] = t[i][0]
        data.append(temp)
    pg = pag(len(t))
    print(pg)
    return render(request,"urec.html",{'data':data,'num':pg,'id':id})

def adminusers(request,length):
    v = validate(request)
    if v == False:
        return HttpResponse(f"{code}")

    dataBase = dbconnect()
    c = dataBase.cursor()
    sql = f"select * from users order by id desc;"
    c.execute(sql)
    t = c.fetchall()
    data = []
    #print(t)
    if length > 0:
        length = (length-1)*10
    print(length)
    for i in range(length,length+10):
        #print(i)
        if i>=len(t):
            break
        temp = dict()
        sql = f"select * from details where id = '{t[i][0]}' and flag = 'uc' ;"
        c.execute(sql)
        r = c.fetchall()
        sql = f"select * from details where id = '{t[i][0]}' and flag = 'inp' ;"
        c.execute(sql)
        inp = c.fetchall()
        temp['name'] = t[i][1]
        temp['email'] = t[i][2]
        temp['id'] = t[i][0]
        temp['uc'] = len(r)
        temp['inp'] = len(inp)
        data.append(temp)
    pg = pag(len(t))
    print(pg)
    return render(request,"adminusers.html",{'data':data,'num':pg})

def useroders(request,id,length):
    v = validate(request)
    if v == False:
        return HttpResponse(f"{code}")

    dataBase = dbconnect()
    c = dataBase.cursor()
    sql = f"select * from details where id = '{id}' order by order_id desc;;"
    c.execute(sql)
    t = c.fetchall()
    data = []
    if length > 0:
        length = (length-1)*10
    print(length)
    for i in range(length,length+10):
        #print(i)
        if i>=len(t):
            break
        temp = dict()
        temp['dname'] = t[i][1]
        temp['model'] = t[i][2]
        temp['message'] = t[i][3]
        temp['status'] = t[i][4]
        temp['adds'] = t[i][7]
        temp['oderid'] = t[i][0]
        data.append(temp)
    pg = pag(len(t))
    print(pg)
    return render(request,"userorders.html",{'data':data,'num':pg,'id':id})

def accept(request,id,uid):
    v = validate(request)
    if v == False:
        return HttpResponse(f"{code}")
    
    dataBase = dbconnect()
    c = dataBase.cursor()
    sql = f"update details set flag = 'wp' where order_id = '{id}'; "
    c.execute(sql)
    dataBase.commit()
    sql = f"select * from users where id ='{uid}';"
    c.execute(sql)
    t = c.fetchall()
    name = t[0][1]
    email = t[0][2]
    sql = f"select * from details where order_id ='{id}';"
    c.execute(sql)
    t = c.fetchall()
    msk = t[0][3]
    model = t[0][2]
    dname = t[0][1]
    subject = "Update from Cicruiters for your order"
    name = name.replace(" ","")
    message = f"Hi {name},\n\nYour Order id: {id} \nDevice Name: {dname} \nModel: {model} \nMessage: {msk} \n\nThe Above order is accepted by our Technical Team \nKindly send your product to Address:\n{Address} \n\nStatus of the order will be changed to 'Received(repair in process)' once we get your product. \n\nRegards,\nTechnical Team"
    mailsent(subject,message,email)
    return redirect(useroders,uid,0)

def received(request,id,uid):
    v = validate(request)
    if v == False:
        return HttpResponse(f"{code}")
    
    dataBase = dbconnect()
    c = dataBase.cursor()
    sql = f"update details set flag = 'inp' where order_id = '{id}'; "
    c.execute(sql)
    dataBase.commit()
    sql = f"select * from users where id ='{uid}';"
    c.execute(sql)
    t = c.fetchall()
    name = t[0][1]
    email = t[0][2]
    sql = f"select * from details where order_id ='{id}';"
    c.execute(sql)
    t = c.fetchall()
    msk = t[0][3]
    model = t[0][2]
    dname = t[0][1]
    subject = "Update from Cicruiters for your order"
    message = f"Hi {name},\n\nYour Order id: {id} \ndevice Name: {dname} \nModel: {model} \nMessage: {msk} \n\nWe Received your product and we've started our repairing process.\n \nRegards,\nTechnical Team"
    mailsent(subject,message,email)
    return redirect(useroders,uid,0)

def reject(request,id,uid):
    v = validate(request)
    if v == False:
        return HttpResponse(f"{code}")
    
    dataBase = dbconnect()
    c = dataBase.cursor()
    sql = f"update details set flag = 'rej' where order_id = '{id}'; "
    c.execute(sql)
    dataBase.commit()
    sql = f"select * from users where id ='{uid}';"
    c.execute(sql)
    t = c.fetchall()
    name = t[0][1]
    email = t[0][2]
    sql = f"select * from details where order_id ='{id}';"
    c.execute(sql)
    t = c.fetchall()
    msk = t[0][3]
    model = t[0][2]
    dname = t[0][1]
    message = f"Hi {name},\n\nYour Order id: {id} \ndevice Name: {dname} \nModel: {model} \nMessage: {msk} \n\nSorry, We are unable to continue with your above order. \n\nRegards,\nTechnical Team"
    subject= "Update from Cicruiters for your order"
    mailsent(subject,message,email)
    return redirect(useroders,uid,0)

def returned(request,id,uid):
    v = validate(request)
    if v == False:
        return HttpResponse(f"{code}")
    
    dataBase = dbconnect()
    c = dataBase.cursor()
    sql = f"update details set flag = 'ret' where order_id = '{id}'; "
    c.execute(sql)
    dataBase.commit()
    sql = f"select * from users where id ='{uid}';"
    c.execute(sql)
    t = c.fetchall()
    name = t[0][1]
    email = t[0][2]
    sql = f"select * from details where order_id ='{id}';"
    c.execute(sql)
    t = c.fetchall()
    msk = t[0][3]
    model = t[0][2]
    dname = t[0][1]
    message = f"Hi {name},\n\nYour Order id: {id} \ndevice Name: {dname} \nModel: {model} \nMessage: {msk} \n\nSorry, We've examined your product, Unfortunately we are unable to repair your product.So we've sent back the product to your address.\n\nRegards,\nTechnical Team"
    subject= "Update from Cicruiters for your order"
    mailsent(subject,message,email)
    return redirect(useroders,uid,0)

def com(request,id,uid):
    v = validate(request)
    if v == False:
        return HttpResponse(f"{code}")
    
    dataBase = dbconnect()
    c = dataBase.cursor()
    sql = f"update details set flag = 'com' where order_id = '{id}'; "
    c.execute(sql)
    dataBase.commit()
    sql = f"select * from users where id ='{uid}';"
    c.execute(sql)
    t = c.fetchall()
    name = t[0][1]
    email = t[0][2]
    sql = f"select * from details where order_id ='{id}';"
    c.execute(sql)
    t = c.fetchall()
    msk = t[0][3]
    model = t[0][2]
    dname = t[0][1]
    message = f"Hi {name},\n\nYour Order id: {id} \ndevice Name: {dname} \nModel: {model} \nMessage: {msk} \n\nYour product was repaired successfully  and we've sent the product to the given address.\n\nRegards,\nTechnical Team"
    subject= "Update from Cicruiters for your order"
    mailsent(subject,message,email)
    return redirect(useroders,uid,0)

def uedit(request,id):
    v = validate(request)
    if v == False:
        return HttpResponse(f"{code}")
    
    dataBase = dbconnect()
    c = dataBase.cursor()
    sql = f"select * from details where order_id = '{id}';"
    c.execute(sql)
    t = c.fetchall()
    dname = t[0][1]
    model= t[0][2]
    msg = t[0][3]
    adds = t[0][7]
    lmsg = False
    if request.method =='POST':
        dname = request.POST['dname']
        model = request.POST['model']
        msg = request.POST['msg']
        adds = request.POST['adds']
        sql = f"update details set device_name= '{dname}', model = '{model}', message = '{msg}',flag = 'uc', address = '{adds}' where order_id ={id};"
        c.execute(sql)
        dataBase.commit()
        lmsg = "Updated Succesfully "
    return render(request,"editrec.html",{'dname':dname,'model':model,'msg':msg,'adds':adds,'lmsg':lmsg})

def confirm(request,mail,msg):
    dataBase = dbconnect()
    c = dataBase.cursor()
    sql = f"select * from users where Email = '{mail}';"
    c.execute(sql)
    t= c.fetchall()
    if t[0][6] == msg:
        sql = f"update users set Flag = '1' where Email= '{mail}';"
        c.execute(sql)
        dataBase.commit()
        request.session['lmsg'] = "Confirmation done. Account created successfully "
        return redirect(login)
    else:
        return HttpResponse("Invalid Request")