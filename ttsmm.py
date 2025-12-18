import io
import os
import requests
import asyncio
import edge_tts
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Token များကို သေချာစစ်ဆေးပါ
TELEGRAM_TOKEN = '7956289526:AAGmCT8KT2CSpHYeVI7-cr2GJdbB7UflFBk'
GEMINI_API_KEY = 'AIzaSyCsdDBVFNAQe8ueqDzMCtRce_2519UTYtc'

MYANMAR_VOICE = "my-MM-NilarNeural"

async def get_ai_script(text):
    """Gemini API URL ကို v1 သို့ ပြောင်းလဲပြီး Model နာမည်ပြင်ဆင်ခြင်း"""
    # URL ကို v1 သို့မဟုတ် v1beta ဟု စမ်းကြည့်နိုင်သည် (ဒီမှာ v1 ကို အရင်စမ်းပါမယ်)
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    prompt = (
        f"အောက်ပါအချက်အလက်ကို အသုံးပြုပြီး ဆွဲဆောင်မှုရှိသော မြန်မာစကားပြော ကြော်ငြာ Script တစ်ခုကို မိန်းကလေးအသံဖြင့် ပြောရန် ရေးပေးပါ။ "
        f"စာသားသက်သက်သာ ပြန်ပေးပါ။ အချက်အလက်: {text}"
    )
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        result = response.json()
        
        # အကယ်၍ gemini-pro မတွေ့ပါက gemini-1.5-flash-latest ကို ထပ်စမ်းပါမည်
        if 'error' in result and "not found" in result['error']['message']:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
            response = requests.post(url, headers=headers, json=data, timeout=30)
            result = response.json()

        if 'candidates' in result and result['candidates']:
            return result['candidates'][0]['content']['parts'][0]['text']
        elif 'error' in result:
            return f"⚠️ API Error: {result['error']['message']}"
        else:
            return "⚠️ AI ဘက်က အဖြေပြန်မပေးပါဘူး။"
            
    except Exception as e:
        return f"⚠️ Connection Error: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    chat_id = update.message.chat_id
    
    status_msg = await update.message.reply_text("✨ AI က Script ရေးနေပါတယ်...")
    
    try:
        ai_script = await get_ai_script(user_input)
        
        if ai_script.startswith("⚠️"):
            await status_msg.edit_text(ai_script)
            return

        await status_msg.edit_text("🎙️ Realistic Voice ဖန်တီးနေပါတယ်...")

        communicate = edge_tts.Communicate(ai_script, MYANMAR_VOICE)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]

        audio_file = io.BytesIO(audio_data)
        audio_file.name = "advertising_voice.mp3"
        
        await context.bot.send_audio(
            chat_id=chat_id, 
            audio=audio_file, 
            caption=f"✅ **AI Script:**\n\n{ai_script}"
        )
        
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"⚠️ Error: {str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is starting...")
    app.run_polling()

if __name__ == '__main__':
    main()
