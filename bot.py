import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import language_tool_python

# Enable logging to catch errors on Render
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize the grammar checker (it will download its language files automatically)
tool = language_tool_python.LanguageTool('en-US')

# Command handler for when someone starts the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"Hello {user_name}! 👋 I am your English Grammar Assistant.\n\n"
        "Send me any long or short message, and I will check it for spelling, "
        "punctuation, and grammar errors!"
    )

# Handler that processes all text messages from any user
async def check_grammar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    
    # Ignore commands like /start
    if user_text.startswith('/'):
        return

    # Let the user know the bot is analyzing
    await update.message.reply_chat_action(action="typing")

    try:
        # Check for errors
        matches = tool.check(user_text)
        
        if len(matches) == 0:
            await update.message.reply_text("✨ Your grammar looks perfect! No mistakes found.")
            return

        # Get the auto-corrected text
        corrected_text = tool.correct(user_text)

        # Build a helpful breakdown of mistakes
        breakdown = "📝 **Here are the corrections:**\n\n"
        for i, match in enumerate(matches[:5], 1): # Limit to first 5 errors to avoid huge spam
            breakdown += f"{i}. ❌ *\"{match.context}\"*\n   💡 {match.message}\n\n"

        if len(matches) > 5:
            breakdown += f"...and {len(matches) - 5} more corrections applied.\n\n"

        breakdown += f"✅ **Corrected Version:**\n{corrected_text}"

        # Send the corrections back to the user
        await update.message.reply_text(breakdown, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error checking text: {e}")
        await update.message.reply_text("Sorry, I encountered an error processing your text.")

def main():
    # Retrieve the token from environmental variables (safest method)
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    if not TOKEN:
        logger.error("No bot token found! Make sure TELEGRAM_BOT_TOKEN is set.")
        return

    # Build the application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT, check_grammar))

    # Run using polling (simplest way to keep it listening continuously)
    logging.info("Starting bot polling...")
    application.run_polling()

if __name__ == '__main__':
    main()
