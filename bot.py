import os
import telebot
import requests
import time
from flask import Flask
from threading import Thread

# إعدادات البوت والعملة
API_TOKEN = '8783414839:AAHB7kEWEc9PMPbJ0mnAXl_Hk6U_Wmzlzz0'
CA = '4bpdQBtSGgJz1CqU1F52Ru3kegDJFHRGa7Fvsau81K7i'

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# لتخزين وقت آخر عملية تم تنبيهها لمنع التكرار
last_processed_timestamp = 0

@app.route('/')
def index():
    return "Buy Bot is Running Live!"

def get_coin_data():
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{CA}"
        res = requests.get(url).json()
        if 'pairs' in res and res['pairs']:
            return res['pairs'][0]
    except:
        return None

def check_buys():
    global last_processed_timestamp
    print("بدء مراقبة عمليات الشراء...")
    
    while True:
        try:
            pair_data = get_coin_data()
            if pair_data:
                # في النسخة المجانية من API سنعتمد على تغير السعر أو حجم التداول
                # لمحاكاة التنبيه، سنرسل تحديثاً دورياً بالسعر أو يمكنك ربطها بـ Webhook متقدم
                # هنا سنقوم بإرسال تحديث السعر كل 10 دقائق كمثال للمراقبة
                pass
            
            # ملاحظة: مراقبة "كل عملية شراء" في اللحظة الحالية تتطلب Webhook من Helius أو QuickNode
            # ولكن كحل مجاني وسريع للموبايل، سنفعل أمر /price ليعطي تفاصيل دقيقة
            time.sleep(60) # فحص كل دقيقة
        except Exception as e:
            print(f"Error in monitor: {e}")
            time.sleep(10)

@bot.message_handler(commands=['start', 'price'])
def send_price(message):
    data = get_coin_data()
    if data:
        # حساب عدد القلوب الخضراء بناءً على السعر (كمثال تعبيري)
        change = float(data.get('priceChange', {}).get('h24', 0))
        hearts = "💚" * min(int(abs(change) / 2) + 1, 15)
        
        text = (
            f"🚀 *{data['baseToken']['name']} Buy!* \n"
            f"{hearts}\n\n"
            f"💰 *Price:* ${data['priceUsd']}\n"
            f"📊 *MCap:* ${data.get('fdv', 'N/A')}\n"
            f"📈 *24h Change:* {change}%\n"
            f"💧 *Liquidity:* ${data.get('liquidity', {}).get('usd', 'N/A')}\n\n"
            f"🔗 *Contract:* \n`{CA}`\n\n"
            f" [DexScreener](https://dexscreener.com/solana/{CA})"
        )
        bot.reply_to(message, text, parse_mode='Markdown', disable_web_page_preview=True)
    else:
        bot.reply_to(message, "⚠️ تعذر جلب البيانات. تأكد أن العملة مدرجة ولها سيولة.")

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    # تشغيل خيط المراقبة
    Thread(target=check_buys).start()
    # تشغيل البوت
    Thread(target=run_bot).start()
    # تشغيل خادم Flask لـ Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
