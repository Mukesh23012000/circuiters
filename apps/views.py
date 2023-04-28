from django.shortcuts import render,HttpResponse,redirect
import mysql.connector


code = "<center><h1>Invalid Session</h1><br> <a href = '/login'>Login Page</a></center>"

def dbconnect():
    dataBase = mysql.connector.connect(
        host ="localhost",
        user ="root",
        passwd ="admin",
        database = "circuiters"
    )
    return dataBase

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
        request.session['lmsg'] = "Logged out Sucessfully!"
    except:
        print("unable to delete the session value")
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
            if t[0][4] == pwd:
                request.session['value'] = t[0][0] , t[0][1]  
                #print(t)
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
    except:
        value = False
        data = False
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
            for i in range(0,10):
                temp = dict()
                temp["device_name"] = t[i][1]
                temp["model"] = t[i][2]
                temp["status"] = t[i][5]
                temp["oid"] = t[i][0]
                data.append(temp)
                print(data)
        if request.method == 'POST':
            n = request.POST['named']
            model = request.POST['model']
            rd = request.POST['rd']
            sql = f"insert into details (device_name,model,message,id,flag) values('{n}','{model}','{rd}','{id}','uc');"
            c.execute(sql)
            dataBase.commit()
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
    return render(request,"index.html",{'value':value,'data':data,'id':id})

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
        else:
            dataBase = dbconnect()
            c = dataBase.cursor()
            ch = f"select * from users where Email = '{email}' or Phone = '{phone}';"
            c.execute(ch)
            t = c.fetchall()
            if t == []:
                sql = f"insert into users (Name,Email,Phone,Password) values('{name}','{email}','{phone}','{pwd}');"
                c.execute(sql)
                dataBase.commit()
                request.session['lmsg'] = "Account Created Sucessfully "
                return redirect(login)
            else:
                m = "Email Id or Phone Number was alreday registered with us "
    return render(request,"signup.html",{'msg':m})

def info(request):
    return render(request,"info.html")

def admin(request):
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
    sql = f"select * from users order by id desc;"
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
        temp['status'] = t[i][5]
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
        temp['status'] = t[i][5]
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
    sql = f"update details set flag = 'inp' where order_id = '{id}'; "
    c.execute(sql)
    dataBase.commit()
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
    return redirect(useroders,uid,0)

def uedit(request,id):
    v = validate(request)
    if v == False:
        return HttpResponse(f"{code}")
    
    dataBase = dbconnect()
    c = dataBase.cursor()
    sql = f"select * from details where order_id = {id};"
    c.execute(sql)
    t = c.fetchall()
    dname = t[0][1]
    model= t[0][2]
    msg = t[0][3]
    lmsg = False
    if request.method =='POST':
        dname = request.POST['dname']
        model = request.POST['model']
        msg = request.POST['msg']
        sql = f"update details set device_name= '{dname}', model = '{model}', message = '{msg}',flag = 'uc' where order_id ={id};"
        c.execute(sql)
        dataBase.commit()
        lmsg = "Updated Succesfully "
    return render(request,"editrec.html",{'dname':dname,'model':model,'msg':msg,'lmsg':lmsg})