from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from flask import request
from flask import jsonify
import joblib
import pandas as pd
import pickle
import re

app = Flask('__name__')
CORS(app)
app.config['CORS_HEADER']='Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp/test.db'
db=SQLAlchemy(app)

class TodoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(240),nullable=False)
    def __str__(self):
        return f'{self.text},{self.id}'

#load model AI
model_tfidf=joblib.load("./model_AI/model_tfidf.sav")
model_classify=pickle.load(open('./model_AI/model_classify.pkl','rb'))
model_label=joblib.load("./model_AI/model_label.sav")

file_colors=pd.read_csv('./data_label_entity/colors.csv')
global list_colors
list_color=file_colors["color"]


@app.route('/classify', methods=['POST','GET'])
@cross_origin(origin='*')
def classify_process():
    text=request.args.get("text")
    t_input=text
    text_data=text.lower()
    t=[text_data]
    X=model_tfidf.transform(t)
    y=model_classify.predict(X[0])
    y_result =model_label.inverse_transform(y)
    return {
        'text':t_input,
        'predict': y_result[0]
        }

@app.route('/getreponse', methods=['POST','GET'])
@cross_origin(origin='*')
def text_process():
    jsony=request.json
    text=jsony['msg']
    
    
    #preprocess
    def preprocess_ner(sentence):
        sentence=sentence.lower()
        sentence = re.sub(r'_',' ', sentence)
        sentence = re.sub(r'[!@#$%^&*<>?,.:;]+', '', sentence)
        ### remove multiple white spaces
        sentence = re.sub(r'\s+', ' ', sentence)
        ### remove start and end white spaces
        sentence = re.sub(r'^\s+', '', sentence) 
        sentence = re.sub(r'\s+$', '', sentence)
        return sentence
    #get intent
    def get_intent(t):
        X=model_tfidf.transform(t)
        y=model_classify.predict(X[0])
        y_result =model_label.inverse_transform(y)
        intent=y_result[0]
        return intent
    #get entity
    def label_entity(text):
        entity={
            "size":[],
            "height_customer":[],
            "ship_fee":[],
            "weight": [],
            "phone":[],
            "cost": [],
            "color":[]
        }
        size=label_entity_size(text)
        entity["size"]=size
        height_customer=label_entity_height(text)
        entity["height_customer"]=height_customer
        ship_fee=label_entity_shipfee(text)
        entity["ship_fee"]=ship_fee
        weight=label_entity_weight(text)
        entity["weight"]=weight
        phone=label_entity_phone(text)
        entity["phone"]=phone
        cost=label_entity_cost(text)
        entity["cost"]=cost
        color=label_entity_color(text)
        entity["color"]=color
        return entity
    def label_entity_size(text):
        size=re.findall('s[ize|ai|z]+ [x*s|m|x*l|a|nhỏ|lớn|nho|lon]+',text)
        return size
    def label_entity_height(text):
        height_customer=[]
        height_customer_=re.findall(r'((\dm|m)\d+|\d+cm)',text)
        if len(height_customer_)>0: 
            for h in height_customer_:

                if len(h)>1:
                    height_customer.append(h[0])
                else:
                    height_customer.append(h)
        return height_customer
    def label_entity_shipfee(text):
        ship_fee=[]
        p = re.search(r'((miễn|free|\d+k?)\s*)*ship(\s*\d+k?)*',text)
        if p is not None:
            index=p.span()
            ship_fee.append(text[index[0]:index[1]])
        p_=re.search(r'((\d+k*\s*)*(phí|giá|gia|phi|tiền|tien)\s*)ship(\s*\d+k*)*',text)
        if p_ is not None:
            index=p_.span()
            ship_fee.append(text[index[0]:index[1]])
        return ship_fee
    def label_entity_weight(text):
        weight=[]
        w=re.search(r'\d+\s*(kg|ky|ký|ki+|kí+)',text)
        if w is not None:
            index=w.span()
            weight.append(text[index[0]:index[1]])
        return weight
    def label_entity_phone(text):
        phone=[]
        p=re.search(r'[0-9]{4}\.*[0-9]{3}\.*[0-9]{2,}',text)
        if p is not None:
            index=p.span()
            phone.append(text[index[0]:index[1]])
        return phone
    def label_entity_cost(text):
        cost=[]
        c=re.search(r'\d+\s*(k|tr((iệ|ie)u)*(\s(đồng|dong|đ|dog|VND|VNĐ)|\s*\d*)*|ng[a|à]n(\s(đồng|dong|đ|dog|VND|VNĐ)|\s*\d*)*|t[ỉiỷy](\s(đồng|dong|đ|dog|VND|VNĐ)|\s*\d*)*|(đồng|dong|đ|dog|VND|VNĐ))',text)

        if c is not None:
            index=c.span()
            cost.append(text[index[0]:index[1]])
        return cost
    def label_entity_color(text):
        color=[]
        for c in list_color:
            c_=re.findall(c,text)
            if len(c_)>0:
                for c__ in c_:
                    color.append(c__)
        return color


    t=[text]
    t_input=text
    text=preprocess_ner(text)
    intent=get_intent(t)
    entity=label_entity(text)
    entity_list=["size","height_customer","ship_fee","weight","phone","cost","color"]
    result_entity=[]
    for i in entity_list:
        if len(entity[i])>0:
            iis=[]
            for j in entity[i]:
                iis.append(j)
                t=""
                t="{}: {}".format(i,iis)
            result_entity.append(t)
    
    
                

    def add_to_db(text,option,entity):
        if option==1:
            data="Khách: "+text
        elif option==2:            
            data="Chatbot:"
        elif option==3:
            data="      Intent: {}".format(text)
        elif option==4:
            ent=""
            for i in result_entity:
                ent=ent+" "+i  
            data="      Entity: {}".format(ent)
        else:
            data="********"
        data=TodoModel(text=data)
        db.session.add(data)
        db.session.commit()
        
    
        
    add_to_db("",5,[])
    add_to_db(text,1,[])
    add_to_db("",2,[])
    add_to_db(intent,3,[])
    add_to_db("",4,entity)
    
    # y_return=""
    # kichban={
    #     "hello":["hi ban",'xin chao ban'],
    #     "connect": ["ban can giup gi","ban doi minh ti nha"]
    # }
    # intent_list=["hello","connect"]
    # for i in range(0,2):
    #     if intent==intent_list[i]:
    #         index=random.randint(0,1)
    #         y_return=kichban[intent_list[i]][index]
    return {
        "intent":intent,
        "entity":result_entity
    }


@app.route('/viewdatabase')
def get_conversation():
    data_base=TodoModel().query.all()
    return render_template('viewdatabase.html',data_base=data_base)


@app.route('/',methods=['POST','GET'])    
def home():
    return "Flask API Thanh_TTS_AI "

    
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0',port='9999')