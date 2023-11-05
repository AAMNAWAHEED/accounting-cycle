from flask import Flask,render_template,request,redirect,url_for,session
from datetime import date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey,text
from sqlalchemy.orm import relationship
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']   ='mysql+pymysql://root:root@localhost/project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'my secret key'
db = SQLAlchemy(app)
#for create_all()
app.app_context().push() 
gt_id = 0
data =[]

def submit():
    print(equal_balance())
    #same_flag()
    #trial balance..........
    query = text("SELECT DISTINCT(head) FROM general")
    res = db.session.execute(query)
    rows = res.fetchall()
    string_list = [row[0] for row in rows]
    d =[]
    c =[]
    assets = ['cash','land','supplies','inventory','building','furniture','account receiveable','prepaid rent','prepaid adv','acc-dep-furniture','acc-dep-building','acc-dep-land'] 
    expense=['rent expense','utility expense','salary expense','interest expense','dep-expense-furniture','dep-expense-building','dep-expense-land','COGS']
    liability=['account payable','unearned']
    revenue = ['service revenue','rent revenue','interest revenue']
    for r in string_list:
        if r=='owner capital':
             query=text("SELECT *FROM general WHERE head=:r")
             res=db.session.execute(query,{"r":r})
             rows=res.fetchone()
             c.append(rows.balance)
             continue
        if r =='owner withdraw':
             query=text("SELECT *FROM general WHERE head=:r")
             res=db.session.execute(query,{"r":r})
             rows=res.fetchone()
             #for r in rows:
             #    d.append(r.balance)
             d.append(rows.balance)
             continue
        for a in assets:
            #assets or expenses
            if r == a:
                deb,cre=debit_return(r)
                if r == 'acc-dep-furniture' or r == 'acc-dep-building' or r =='acc-dep-land':
                   # print("yes")
                    c.append(cre)
                else:
                    #print("no")
                    d.append(deb-cre)
                break
        for a in expense:
            #assets or expenses
            if r == a:
                deb,cre=debit_return(r)
                d.append(deb-cre)
                break
        for a in liability:
            #assets or expenses
            if r == a:
                deb,cre=debit_return(r)
                c.append(cre-deb)
                break
        for a in revenue:
            #assets or expenses
            if r == a:
                deb,cre=debit_return(r)
                c.append(cre-deb)
                break
    total_deb = sum(d)
    total_cre = sum(c)
    print(total_cre,total_deb)
    #financial satemets
    #select revenue
    rev_dic ={}
    query = text("SELECT *FROM general where head like '%venue%'")
    row = db.session.execute(query)
    rows = row.fetchall()
    if len(rows)!=0:
        rev=0
        for r in rows:
            if r.head in rev_dic:
                rev_dic[r.head]= r.balance + rev_dic.get(r.head)
            else:
                rev_dic[r.head] = r.balance
            rev+= r.balance
    else:
        rev = 0
    #expense
    exp_dic = {}
    query = text("SELECT *FROM general where head like '%pense%'")
    row = db.session.execute(query)
    rows = row.fetchall()
    if len(rows)!=0:
        exp=0
        for r in rows:
            if r.head in exp_dic:
                exp_dic[r.head]= r.balance + exp_dic.get(r.head)
            else:
                exp_dic[r.head] = r.balance
            exp+= r.balance
        #net_inc = rev - exp
    else:
         exp = 0
    net_inc = rev - exp
         #net_inc = 0
    #owner capital
    query = text("SELECT *FROM general where head ='owner capital'")
    row = db.session.execute(query)
    rows = row.fetchone()
    if rows!= None:
        o_c = rows.balance
    else:
        o_c = 0
    #owner withfrw
    query = text("SELECT *FROM general where head = 'owner withdraw'")
    row = db.session.execute(query)
    rows = row.fetchall()
    if len(rows) != 0:
        o_w = 0
        for r in rows:
            o_w+=r.balance
    else:
        o_w = 0
    o_e = o_c +net_inc - o_w
    liab =0
    ass = 0
    ass_dic = {}
    liab_dic = {}
    ass_dic,ass=retrun_assets(assets)
    #liabilities
    liab_dic,liab = return_liab(liability)
    new_oe = liab+o_e        
    return locals()

def  displaydata(date,head,flag,type,balance,gt_id):
    global data
    data.append({
        'gt_id':gt_id,
        'date' :date,
        'head': head,
        'type': type,
        'flag': flag,
        'balance': balance
    })
    return data

def add():
    global gt_id
    exists = db.session.query(transaction.query.exists()).scalar()
    if exists:
        print("exist")
        if request.method == 'POST':
                query = text("SELECT date FROM general WHERE t_id=:gt_id")
                res = db.session.execute(query,{"gt_id":gt_id})
                rows = res.fetchone()
                if rows != None:
                    date = rows.date
                else:
                    date = request.form.get('date')
                head = request.form.get('head')
                flag = request.form.get('flag')
                type = request.form.get('type')
                balance = request.form.get('balance')
                entry_data(date,head,type,flag,balance,gt_id)
    else:
        #print(f"dont exist{gt_id}")
        if request.method == 'POST':
            flag = request.form.get('flag')
            new_transaction(flag)
            date = request.form.get('date')
            head = request.form.get('head')
            flag = request.form.get('flag')
            type = request.form.get('type')
            balance = request.form.get('balance')
            entry_data(date,head,type,flag,balance,gt_id)
    
    return(displaydata(date,head,flag,type,balance,gt_id))
class transaction(db.Model):
    __tablename__ = 'transaction'
    t_id = db.Column(db.Integer,primary_key =True)
    flag = db.Column(db.String(200),nullable=False)
    transactions = db.relationship('general',backref='transaction',lazy='select')
    def __repr__(self)->str:
        return f"{self.t_id},{self.flag}"

class general(db.Model):
    __tablename__ = 'general'
    id = db.Column(db.Integer,primary_key =True)
    date = db.Column(db.Date,default= date.today)
    head = db.Column(db.String(200),nullable = False)
    type = db.Column(db.String(200),nullable = False)
    flag = db.Column(db.String(200),nullable = False)
    balance = db.Column(db.Integer,nullable = False)
    t_id = db.Column(db.Integer,db.ForeignKey(transaction.t_id))
    def __repr__(self) ->str:
        return f"{self.t_id}and{self.head}"
    
def equal_balance():
     global gt_id
     deb = 0
     cre = 0
     #get debit value
     query=text("SELECT *FROM general WHERE type='debit' AND t_id=:gt_id")
     res=db.session.execute(query,{"gt_id":gt_id})
     rows=res.fetchall()
     for row in rows:
         deb += row.balance 
     #print(deb)
     #get credit value
     query=text("SELECT *FROM general WHERE type='credit' AND t_id=:gt_id")
     res=db.session.execute(query,{"gt_id":gt_id})
     rows=res.fetchall()
     for row in rows:
         cre += row.balance 
     print(f"debit{deb}credit{cre}")
     #print(deb) 
     if deb != cre:
         return 1
     else: 
         return 0
def same_flag():
    global gt_id
    query = text("SELECT *FROM general WHERE t_id=:gt_id")
    res = db.session.execute(query,{"gt_id": gt_id})
    rows = res.fetchall()
    flag = rows[0].flag
    for row in rows:
        if row.flag !=flag:
            print("not same")
    return
def debit_return(r):
                deb = 0
                cre = 0
                #get debit value
                query=text("SELECT *FROM general WHERE type='debit' AND head=:r")
                res=db.session.execute(query,{"r":r})
                rows=res.fetchall()
                for row in rows:
                    deb += row.balance 

                #get credit value
                query=text("SELECT *FROM general WHERE type='credit' AND head=:r")
                res=db.session.execute(query,{"r":r})
                rows=res.fetchall()
                for row in rows:
                    cre += row.balance
                return deb,cre
def new_transaction(flag):
    global gt_id
    print(f"before new transaction func{gt_id}")
    #gt_id +=1
    e = transaction(t_id=gt_id,flag=flag)
    db.session.add(e)
    db.session.commit()
    print(f"before new transaction func{gt_id}")
    #gt_id +=1
    return 
def entry_data(date,head,type,flag,balance,gt_id):
    entry = general(date=date,head=head,type=type,flag=flag,balance=balance,t_id=gt_id)
    db.session.add(entry)
    db.session.commit()
    return

def closing_entry(rows,head):
    global gt_id
    cur_date = date.today()
    #date = date.today
    for r in rows:
        gt_id +=1
        new_transaction('closing')
        #adding into new transaction
        if head == 'revenue':
             i_s_type = 'credit'
             type = 'debit'
             entry_data(cur_date,r.head,type,'closing',r.balance,gt_id)
             entry_data(cur_date,'income summary',i_s_type,'closing',r.balance,gt_id)
        else:
             i_s_type = 'debit'
             type= 'credit'
             entry_data(cur_date,'income summary',i_s_type,'closing',r.balance,gt_id)
             entry_data(cur_date,r.head,type,'closing',r.balance,gt_id)
    return 


def retrun_assets(assets):
    ass=0
    ass_dic ={}
    #assets 
    for a in assets:
         deb,cre=debit_return(a)
         ass_dic[a] = deb-cre
         ass+=(deb-cre)
    return ass_dic,ass
def return_liab(liab):
    ass=0
    ass_dic ={}
    #assets 
    for a in liab:
         deb,cre=debit_return(a)
         ass_dic[a] = cre-deb
         ass+=(cre-deb)
    return ass_dic,ass

@app.route('/')
def main():
    global data,gt_id
    session.clear()
    return render_template('main.html',data = data )
@app.route('/clear',methods =['Get','Post'])
def clear():
    global data 
    data =[]
    global gt_id
    gt_id = 1
    db.session.query(general).delete()
    db.session.query(transaction).delete()
    db.session.commit()
    s = text(('ALTER TABLE general AUTO_INCREMENT = 1'))
    db.session.execute(s)
    return redirect(url_for('main'))

@app.route('/add',methods =['Get','Post'])
def add_row():
    global data
    data=add()
    return render_template('main.html',data=data)
   # return redirect(url_for('main'))
@app.route('/adjustments/add',methods =['Get','Post'])
def add_adj_row():
    data = add()
    return render_template("adjustment_form.html",data=data)
@app.route('/new',methods =['Get','Post'])
def new():
     global gt_id
     global data
     if(equal_balance()==0):
        flag = request.form.get('flag')
        gt_id +=1
        new_transaction(flag)
        return redirect(url_for('main'))
     else:
         query = text("DELETE FROM general where t_id =:gt_id")
         db.session.execute(query,{"gt_id":gt_id})
         db.session.commit()
         data = [d for d in data if d['gt_id'] != gt_id]
         return render_template('main.html',data=data)
     
@app.route('/adjustments/new',methods =['Get','Post'])
def new_adj():
     global gt_id,data
     if(equal_balance()==0):
        flag = request.form.get('flag')
        gt_id +=1
        new_transaction(flag)
        return redirect(url_for('adjustments'))
     else:
         query = text("DELETE FROM general where t_id =:gt_id")
         db.session.execute(query,{"gt_id":gt_id})
         db.session.commit()
         data = [d for d in data if d['gt_id'] != gt_id]
         return render_template("adjustment_form.html",data = data)
@app.route("/submit",methods=['Get','Post'])
def abc():
    return render_template("statement.html",**submit())
@app.route("/adjustments")
def adjustments():
    global data
    return render_template("adjustment_form.html",data = data)

@app.route("/adjustments/submit",methods=['Get','Post'])
def helooo():
    return render_template("adjusted_trial.html",**submit())
@app.route("/closing")
def closing():
    global gt_id
    cur_date = date.today()
    if 'count' not in session:
        session['count'] = 0
        assets = ['cash','land','supplies','inventory','building','furniture','account receiveable','prepaid rent','prepaid adv','acc-dep-furniture','acc-dep-building','acc-dep-land']
        liability=['account payable','unearned']
        #revenue debit i/s credit
        query = text("SELECT *FROM general where head like '%venue%'")
        row = db.session.execute(query)
        rows = row.fetchall()
        if len(rows)!=0:
            closing_entry(rows,'revenue')
        #adding expense
        query = text("SELECT *FROM general where head like '%pense%'")
        row = db.session.execute(query)
        rows = row.fetchall()
        if len(rows)!=0:
            closing_entry(rows,'expense')
        #close income summary
        query=text("SELECT *FROM general WHERE head='income summary'")
        res=db.session.execute(query)
        rows=res.fetchall()
        i_s_balance = 0
        if len(rows)!=0:
            deb,cre=debit_return('income summary')
            i_s_balance = cre-deb
        gt_id +=1
        new_transaction('closing')
        entry_data(cur_date,'income summary','debit','closing',i_s_balance,gt_id)
        entry_data(cur_date,"retained earning",'credit','closing',i_s_balance,gt_id)
        #clear dividends
        query=text("SELECT *FROM general WHERE head='owner withdraw'")
        res=db.session.execute(query)
        rows=res.fetchone()
        if rows!=None:
            gt_id +=1
            new_transaction('closing')
            entry_data(cur_date,'retained earning','debit','closing',rows.balance,gt_id)
            entry_data(cur_date,'owner withdraw','credit','closing',rows.balance,gt_id)
        #ADD OWNER CAPITAL
        query=text("SELECT *FROM general WHERE head='owner capital'")
        res=db.session.execute(query)
        rows=res.fetchone()
        if rows!=None:
            gt_id +=1
            new_transaction('closing')
            entry_data(cur_date,'owner capital','debit','closing',rows.balance,gt_id)
            entry_data(cur_date,'retained earning','credit','closing',rows.balance,gt_id)

        #trial balance calculations
        ass_dic,ass=retrun_assets(assets)
        #liabilities
        liab_dic,liab = return_liab(liability)
        #retained earning
        deb,cre=debit_return('retained earning')
        r_e = cre-deb
        total_deb = ass
        total_cre = liab + r_e
        session['ass_dic'] = ass_dic
        session['liab_dic'] = liab_dic
        session['total_cre'] = total_cre
        session['total_deb'] = total_deb
        session['r_e'] = r_e
    return render_template('closing.html',total_deb=session['total_deb'],total_cre= session['total_cre'],ass_dic=session['ass_dic'],liab_dic = session['liab_dic'],r_e = session['r_e'])
if __name__ == "__main__":
    app.run(debug=True)