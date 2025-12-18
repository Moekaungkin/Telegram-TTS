import os
import asyncio
import edge_tts
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Telegram Bot Token (ဒါကတော့ မှန်အောင် ထည့်ပေးပါ)
TELEGRAM_TOKEN = '7956289526:AAGmCT8KT2CSpHYeVI7-cr2GJdbB7UflFBk'

# အသံရွေးချယ်မှု (နီလာ - Realistic Myanmar Voice)
MYANMAR_VOICE = "my-MM-NilarNeural"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    chat_id = update.message.chat_id
    
    # စာသားလက်ခံရရှိကြောင်း အကြောင်းပြန်ခြင်း
    status_msg = await update.message.reply_text("🎙️ အသံဖိုင် ဖန်တီးနေပါတယ်... ခဏစောင့်ပါရှင်။")
    
    try:
        # အသံဖိုင်အမည် သတ်မှတ်ခြင်း
        filename = f"voice_{chat_id}.mp3"
        
        # Edge-TTS သုံးပြီး တိုက်ရိုက်အသံပြောင်းခြင်း (AI မပါတော့ပါ)
        communicate = edge_tts.Communicate(user_input, MYANMAR_VOICE)
        await communicate.save(filename)

        # Telegram ဆီ အသံဖိုင် ပို့ပေးခြင်း
        with open(filename, 'rb') as audio:
            await context.bot.send_audio(
                chat_id=chat_id, 
                audio=audio, 
                caption="✅ အသံဖိုင် အဆင်သင့်ဖြစ်ပါပြီရှင်။"
            )
        
        # ပို့ပြီးရင် ဖိုင်ကို ပြန်ဖျက်ခြင်း
        os.remove(filename)
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"⚠️ Error ဖြစ်သွားပါတယ်: {str(e)}")

def main():
    # Bot ကို စတင်နှိုးခြင်း
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # စာသားဝင်လာရင် handle_message ကို ခေါ်ခိုင်းခြင်း
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running without AI (Direct TTS Mode)...")
    app.run_polling()

if __name__ == '__main__':
    main()
