import os
from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

conversation_history = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ola! Sou seu assistente de IA. Como posso te ajudar?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    conversation_history[user_id].append(types.Content(role="user", parts=[types.Part(text=user_message)]))
    if len(conversation_history[user_id]) > 20:
        conversation_history[user_id] = conversation_history[user_id][-20:]
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=conversation_history[user_id],
            config=types.GenerateContentConfig(
                system_instruction="Voce e um assistente util. Responda sempre em portugues brasileiro.",
            )
        )
        assistant_message = response.text
        conversation_history[user_id].append(types.Content(role="model", parts=[types.Part(text=assistant_message)]))
        await update.message.reply_text(assistant_message)
    except Exception as e:
        await update.message.reply_text("Desculpe, ocorreu um erro. Tente novamente.")
        print(f"Erro: {e}")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conversation_history[update.effective_user.id] = []
    await update.message.reply_text("Historico limpo!")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot iniciado!")
    app.run_polling()
