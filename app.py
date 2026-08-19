from flask import Flask, request, jsonify
from flask_cors import CORS
import csv, os, json, hashlib, secrets
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)

BASE = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE, 'user_behaviour_data.csv')
USERS_FILE = os.path.join(BASE, 'users.csv')
ORDERS_FILE = os.path.join(BASE, 'orders.csv')

HEADERS = ['session_id','user_id','page_visited','device','screen_resolution','event_type','timestamp','element_id','form_id','scroll_depth','x_pos','y_pos','time_on_page']
USER_HEADERS = ['user_id','name','email','phone','password_hash','created_at','credits','orders_count','cart_items','product_views','tier']
ORDER_HEADERS = ['order_number','created_at','user_id','customer_name','customer_email','phone','address','outlet','order_type','payment_method','products','subtotal','tax','delivery_fee','urgent_fee','credits_earned','credits_redeemed','credits_used_value','total','notes']

PRODUCTS = {
    'House Espresso': {'price': 290, 'category': 'Coffee', 'rating': 4.8, 'offer': '10% OFF', 'trending': True},
    'Vanilla Latte': {'price': 370, 'category': 'Coffee', 'rating': 4.7, 'offer': '₹50 OFF', 'trending': True},
    'Nitro Cold Brew': {'price': 420, 'category': 'Coffee', 'rating': 4.9, 'offer': 'New', 'trending': True},
    'Almond Croissant': {'price': 310, 'category': 'Food', 'rating': 4.6, 'offer': 'Combo Deal', 'trending': False},
    'Cortado': {'price': 330, 'category': 'Coffee', 'rating': 4.7, 'offer': '', 'trending': False},
    'Seasonal Tonic': {'price': 450, 'category': 'Food', 'rating': 4.5, 'offer': '15% OFF', 'trending': True},
}

for path, headers in [(USERS_FILE, USER_HEADERS), (ORDERS_FILE, ORDER_HEADERS), (CSV_FILE, HEADERS)]:
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, 'w', newline='', encoding='utf-8') as f: csv.writer(f).writerow(headers)

def now(): return datetime.now(timezone.utc).isoformat()
def uid(): return 'usr_' + secrets.token_hex(8)
def hash_pw(p): return hashlib.sha256(p.encode()).hexdigest()
def read_users():
    with open(USERS_FILE, newline='', encoding='utf-8') as f: return list(csv.DictReader(f))
def user_by_id(user_id): return next((u for u in read_users() if u['user_id'] == user_id), None)
def user_by_email(email): return next((u for u in read_users() if u['email'].lower() == email.lower()), None)
def write_users(users):
    with open(USERS_FILE, 'w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=USER_HEADERS); w.writeheader(); w.writerows(users)
def tier(credits):
    c=int(credits)
    return 'Gold' if c >= 500 else ('Silver' if c >= 200 else 'Bronze')
def public_user(u):
    if not u: return None
    x={k:u.get(k,'') for k in USER_HEADERS if k!='password_hash'}
    x['credits']=int(float(x.get('credits') or 0)); x['orders_count']=int(float(x.get('orders_count') or 0)); x['cart_items']=int(float(x.get('cart_items') or 0)); x['product_views']=int(float(x.get('product_views') or 0)); x['tier']=tier(x['credits'])
    return x

@app.get('/api/health')
def health(): return jsonify({'status':'ok','service':'The Daily Grind API','time':now()})

@app.post('/api/signup')
def signup():
    d=request.get_json(silent=True) or {}
    name=(d.get('name') or '').strip(); email=(d.get('email') or '').strip(); phone=(d.get('phone') or '').strip(); password=d.get('password') or ''
    if not name or not email or not phone or len(password)<6: return jsonify({'error':'Name, email, phone and a 6+ character password are required'}),400
    if user_by_email(email): return jsonify({'error':'An account with this email already exists'}),409
    u={'user_id':uid(),'name':name,'email':email,'phone':phone,'password_hash':hash_pw(password),'created_at':now(),'credits':'0','orders_count':'0','cart_items':'0','product_views':'0','tier':'Bronze'}
    users=read_users(); users.append(u); write_users(users)
    return jsonify({'status':'success','user':public_user(u)}),201

@app.post('/api/login')
def login():
    d=request.get_json(silent=True) or {}; email=(d.get('email') or '').strip(); password=d.get('password') or ''
    u=user_by_email(email)
    if not u or u['password_hash'] != hash_pw(password): return jsonify({'error':'Invalid email or password'}),401
    return jsonify({'status':'success','user':public_user(u)})

@app.get('/api/user/<user_id>')
def get_user(user_id):
    u=user_by_id(user_id)
    return (jsonify({'user':public_user(u)}) if u else (jsonify({'error':'User not found'}),404))

@app.get('/api/products')
def products(): return jsonify(PRODUCTS)

@app.post('/api/activity')
def activity():
    d=request.get_json(silent=True) or {}; u=user_by_id(d.get('user_id',''))
    if not u: return jsonify({'error':'Login required'}),401
    users=read_users(); target=next(x for x in users if x['user_id']==u['user_id'])
    target['product_views']=str(int(float(target.get('product_views') or 0))+int(d.get('product_views',0) or 0))
    target['cart_items']=str(max(0,int(d.get('cart_items',target.get('cart_items') or 0))))
    target['tier']=tier(target['credits']); write_users(users)
    return jsonify({'status':'success','user':public_user(target)})

@app.post('/api/track')
def track_data():
    d=request.get_json(silent=True) or {}; user_id=d.get('user_id','')
    if not user_id or not user_by_id(user_id): return jsonify({'error':'Login required before tracking'}),401
    rows=[]
    for e in d.get('events',[]):
        rows.append([d.get('sessionId',''),user_id,d.get('pageVisited',''),d.get('device',''),d.get('screenResolution',''),e.get('eventType',''),e.get('timestamp',''),e.get('elementId',''),e.get('formId',''),e.get('depth',e.get('scroll_depth','')),e.get('x',''),e.get('y',''),d.get('timeOnPage','')])
    if rows:
        with open(CSV_FILE,'a',newline='',encoding='utf-8') as f: csv.writer(f).writerows(rows)
    return jsonify({'status':'success','events_saved':len(rows)})

@app.post('/api/order')
def create_order():
    d=request.get_json(silent=True) or {}; required=['order_number','user_id','customer_name','customer_email','phone','address','outlet','order_type','payment_method','products','subtotal','tax','delivery_fee','urgent_fee','total']
    if any(k not in d for k in required): return jsonify({'error':'Incomplete order data'}),400
    u=user_by_id(d['user_id'])
    if not u: return jsonify({'error':'Login required'}),401
    subtotal=float(d.get('subtotal',0)); credits_earned=int(subtotal//10); requested_redeem=max(0,int(d.get('credits_redeemed',0) or 0)); available=int(float(u.get('credits') or 0)); credits_redeemed=min(requested_redeem,available); redeem_value=credits_redeemed
    total=max(0, subtotal+float(d.get('tax',0))+float(d.get('delivery_fee',0))+float(d.get('urgent_fee',0))-redeem_value)
    with open(ORDERS_FILE,'a',newline='',encoding='utf-8') as f:
        csv.writer(f).writerow([d['order_number'],d.get('created_at',now()),d['user_id'],d['customer_name'],d['customer_email'],d['phone'],d['address'],d['outlet'],d['order_type'],d['payment_method'],json.dumps(d.get('products',[]),ensure_ascii=False),f'{subtotal:.2f}',f"{float(d.get('tax',0)):.2f}",f"{float(d.get('delivery_fee',0)):.2f}",f"{float(d.get('urgent_fee',0)):.2f}",credits_earned,credits_redeemed,f'{redeem_value:.2f}',f'{total:.2f}',d.get('notes','')])
    users=read_users(); target=next(x for x in users if x['user_id']==u['user_id']); target['credits']=str(available-credits_redeemed+credits_earned); target['orders_count']=str(int(float(target.get('orders_count') or 0))+1); target['tier']=tier(target['credits']); write_users(users)
    return jsonify({'status':'success','order_number':d['order_number'],'credits_earned':credits_earned,'credits_redeemed':credits_redeemed,'total':round(total,2),'user':public_user(target)}),201

@app.get('/api/orders/<user_id>')
def user_orders(user_id):
    if not user_by_id(user_id): return jsonify({'error':'User not found'}),404
    with open(ORDERS_FILE,newline='',encoding='utf-8') as f: rows=[r for r in csv.DictReader(f) if r['user_id']==user_id]
    for r in rows:
        try:r['products']=json.loads(r['products'])
        except:pass
    return jsonify({'orders':rows})

if __name__=='__main__': app.run(host='0.0.0.0',port=5000,debug=True)
