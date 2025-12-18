import os
import requests
import asyncio
import edge_tts
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# API Tokens
TELEGRAM_TOKEN = '7956289526:AAGmCT8KT2CSpHYeVI7-cr2GJdbB7UflFBk'
GEMINI_API_KEY = 'AIzaSyCsdDBVFNAQe8ueqDzMCtRce_2519UTYtc'

MYANMAR_VOICE = "my-MM-NilarNeural"

async def get_ai_script(text):
    # Google API ကို Proxy မပါဘဲ တိုက်ရိုက်ခေါ်ခြင်း
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    prompt = (
        f"အောက်ပါအချက်အလက်ကို သုံးပြီး ဗီဒီယိုကြော်ငြာအတွက် ဆွဲဆောင်မှုရှိတဲ့ Script တစ်ခု ရေးပေးပါ။ "
        f"မိန်းကလေးတစ်ယောက်က သာယာပျူငှာစွာ ပြောနေတဲ့ပုံစံ ဖြစ်ရမယ်။ "
        f"စာသားသက်သက်ပဲ ပြန်ပေးပါ။ အချက်အလက်: {text}"
    )
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    # ဤနေရာတွင် VPN မလိုဘဲ ချိတ်ဆက်နိုင်ရန် timeout နှင့် retry ကို သုံးထားသည်
    response = requests.post(url, headers=headers, json=data, timeout=60)
    result = response.json()
    return result['candidates'][0]['content']['parts'][0]['text']

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    chat_id = update.message.chat_id
    
    status_msg = await update.message.reply_text("🪄 စာသားပြင်ဆင်နေပါတယ်...")
    
    try:
        ai_script = await get_ai_script(user_input)
        await status_msg.edit_text("🎙️ အသံဖိုင် လုပ်နေပါပြီ...")
        
        filename = f"voice_{chat_id}.mp3"
        communicate = edge_tts.Communicate(ai_script, MYANMAR_VOICE)
        await communicate.save(filename)

        with open(filename, 'rb') as audio:
            await context.bot.send_audio(chat_id=chat_id, audio=audio, caption=f"✨ Script:\n\n{ai_script}")
        
        os.remove(filename)
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"⚠️ Error: {str(e)}\n(အင်တာနက် လိုင်းမကောင်းတာ သို့မဟုတ် IP ပိတ်ထားတာ ဖြစ်နိုင်ပါတယ်)")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot started...")
    app.run_polling()

if __name__ == '__main__':
    main()
      
