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
    """Gemini API ကို အသုံးပြုပြီး Script ရေးခိုင်းခြင်း"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    # ဆွဲဆောင်မှုရှိသော Script ဖြစ်စေရန် Prompt ပေးခြင်း
    prompt = (
        f"အောက်ပါအချက်အလက်ကို အသုံးပြုပြီး ဆွဲဆောင်မှုရှိသော မြန်မာစကားပြော ကြော်ငြာ Script တစ်ခုကို မိန်းကလေးအသံဖြင့် ပြောရန် ရေးပေးပါ။ "
        f"စကားလုံးများကြားတွင် အသက်ရှူရပ်နားရန် ကော်မာ ( , ) များ သုံးပေးပါ။ စာသားသက်သက်သာ ပြန်ပေးပါ။ အချက်အလက်: {text}"
    )
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        result = response.json()
        
        # API Response ကို စစ်ဆေးခြင်း
        if 'candidates' in result and result['candidates']:
            return result['candidates'][0]['content']['parts'][0]['text']
        elif 'error' in result:
            return f"⚠️ API Error: {result['error']['message']}"
        else:
            return "⚠️ AI ဘက်က အဖြေပြန်မပေးပါဘူး။ စာသားကို ပြောင်းလဲပေးပို့ကြည့်ပါ။"
            
    except Exception as e:
        return f"⚠️ Connection Error: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    chat_id = update.message.chat_id
    
    status_msg = await update.message.reply_text("✨ AI က ဆွဲဆောင်မှုရှိတဲ့ Script ရေးနေပါတယ်...")
    
    try:
        # ၁။ AI ဆီက Script ယူခြင်း
        ai_script = await get_ai_script(user_input)
        
        if ai_script.startswith("⚠️"):
            await status_msg.edit_text(ai_script)
            return

        await status_msg.edit_text("🎙️ Realistic Voice ဖန်တီးနေပါတယ်...")

        # ၂။ Edge-TTS သုံးပြီး Memory ပေါ်မှာ အသံဖိုင်လုပ်ခြင်း
        communicate = edge_tts.Communicate(ai_script, MYANMAR_VOICE)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]

        # ၃။ Telegram သို့ ပို့ခြင်း
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "advertising_voice.mp3"
        
        await context.bot.send_audio(
            chat_id=chat_id, 
            audio=audio_file, 
            caption=f"✅ **AI Script:**\n\n{ai_script}"
        )
        
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"⚠️ ဖြစ်သွားတဲ့ Error: {str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is starting with Gemini AI...")
    app.run_polling()

if __name__ == '__main__':
    main()
