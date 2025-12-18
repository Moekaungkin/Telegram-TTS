import io
import asyncio
import edge_tts
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Telegram Bot Token
TELEGRAM_TOKEN = '7956289526:AAGmCT8KT2CSpHYeVI7-cr2GJdbB7UflFBk'

# Realistic Myanmar Voice (နီလာ)
MYANMAR_VOICE = "my-MM-NilarNeural"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    chat_id = update.message.chat_id
    
    status_msg = await update.message.reply_text("🎙️ အသံဖိုင် ဖန်တီးနေပါတယ်...")
    
    try:
        # Edge-TTS သုံးပြီး အသံကို စက်ထဲမှာ ဖိုင်မသိမ်းဘဲ Memory ပေါ်မှာတင် လုပ်ခြင်း
        communicate = edge_tts.Communicate(user_input, MYANMAR_VOICE)
        
        # အသံဒေတာကို စုစည်းခြင်း
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]

        # Telegram ဆီသို့ တိုက်ရိုက်ပို့ခြင်း
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "voice.mp3"
        
        await context.bot.send_audio(
            chat_id=chat_id, 
            audio=audio_file, 
            caption="✅ အသံဖိုင် ရပါပြီရှင်။"
        )
        
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"⚠️ Error: {str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running in Direct Stream Mode...")
    app.run_polling()

if __name__ == '__main__':
    main()
  
