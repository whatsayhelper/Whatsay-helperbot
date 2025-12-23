import os
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import openai
from database import Database

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# OpenAI setup
openai.api_key = os.getenv('OPENAI_API_KEY')

# Database
db = Database()

# Constants
FREE_CREDITS = 12
CREDIT_EXPIRY_DAYS = 7

# Language support for responses
LANGUAGES = {
    'en': {'name': '🇬🇧 English', 'code': 'English'},
    'nl': {'name': '🇳🇱 Dutch', 'code': 'Dutch'},
    'es': {'name': '🇪🇸 Spanish', 'code': 'Spanish'}
}

# Tone options
TONES = {
    'casual': {'name': '😊 Casual', 'desc': 'friendly and relaxed'},
    'professional': {'name': '💼 Professional', 'desc': 'polite and respectful'},
    'flirty': {'name': '😏 Flirty', 'desc': 'playful and charming'}
}

# Interface text (English default, Dutch option)
TEXTS = {
    'en': {
        'welcome': """👋 Welcome to Whatsay!

Never have awkward conversations again! Send me a message you need to reply to and I'll give you 3 perfect responses.

💎 You have 12 free credits to try it out!
   (Credits expire after 7 days)

How it works:
1️⃣ Send me the message you want to reply to
2️⃣ Choose your desired tone (Casual/Professional/Flirty)
3️⃣ Choose the language for your response
4️⃣ Get 3 perfect answers!

Ready? Send me a message! 💬""",
        'no_credits': """😕 You're out of credits!

💎 Current credits: 0

Buy more credits to continue:
• 50 credits - €7.99
• 150 credits - €19.99
• 500 credits - €49.99

Or get a subscription:
• Pro - €14.99/month - 100 credits
• Ultimate - €29.99/month - Unlimited

Click the button below to buy! 👇""",
        'choose_tone': '🎭 What tone do you want for your response?',
        'choose_language': '🌍 What language do you want to reply in?',
        'generating': '✨ Generating... (costs 1 credit)',
        'error': '❌ Something went wrong. Please try again.',
        'credits_status': """💎 Your Credits:

Total: {total} credits
• Free: {free} (expires {expiry})
• Purchased: {purchased}

📊 Statistics:
• Used this month: {used_month}
• Total used: {total_used}

Average: {avg} per day""",
        'history_empty': '📚 You have no conversations yet.',
        'copied': '✅ Copied to clipboard!',
        'new_conversation': '✨ New conversation started!'
    },
    'nl': {
        'welcome': """👋 Welkom bij Whatsay!

Nooit meer awkward gesprekken! Stuur me een bericht waar je op moet reageren en ik geef je 3 perfecte antwoorden.

💎 Je hebt 12 gratis credits om te proberen!
   (Credits vervallen na 7 dagen)

Hoe werkt het?
1️⃣ Stuur me het bericht waar je op wilt reageren
2️⃣ Kies je gewenste tone (Casual/Professional/Flirty)
3️⃣ Kies de taal voor je antwoord
4️⃣ Krijg 3 perfecte antwoorden!

Ready? Stuur me een bericht! 💬""",
        'no_credits': """😕 Je hebt geen credits meer!

💎 Huidige credits: 0

Koop meer credits:
• 50 credits - €7.99
• 150 credits - €19.99
• 500 credits - €49.99

Of neem een subscription:
• Pro - €14.99/maand - 100 credits
• Ultimate - €29.99/maand - Unlimited

Klik hieronder! 👇""",
        'choose_tone': '🎭 Welke tone wil je?',
        'choose_language': '🌍 In welke taal wil je antwoorden?',
        'generating': '✨ Aan het genereren... (kost 1 credit)',
        'error': '❌ Er ging iets mis. Probeer opnieuw.',
        'credits_status': """💎 Je Credits:

Totaal: {total} credits
• Gratis: {free} (vervalt {expiry})
• Gekocht: {purchased}

📊 Statistieken:
• Gebruikt deze maand: {used_month}
• Totaal gebruikt: {total_used}

Gemiddeld: {avg} per dag""",
        'history_empty': '📚 Je hebt nog geen gesprekken.',
        'copied': '✅ Gekopieerd!',
        'new_conversation': '✨ Nieuw gesprek!'
    }
}

def get_text(user_lang, key, **kwargs):
    """Get translated text"""
    lang = user_lang if user_lang in TEXTS else 'en'
    text = TEXTS[lang].get(key, TEXTS['en'][key])
    return text.format(**kwargs) if kwargs else text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    # Create user if new
    user_data = db.get_user(user.id)
    if not user_data:
        db.create_user(user.id, user.username or user.first_name)
        user_data = db.get_user(user.id)
    
    user_lang = user_data.get('language', 'en')
    
    # Welcome message with buttons
    keyboard = [
        [InlineKeyboardButton("💎 Credits", callback_data="credits"),
         InlineKeyboardButton("📚 History", callback_data="history")],
        [InlineKeyboardButton("🌍 Language", callback_data="change_language"),
         InlineKeyboardButton("🛒 Buy Credits", url="https://buy.stripe.com/test_yourlink")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        get_text(user_lang, 'welcome'),
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages"""
    user = update.effective_user
    user_data = db.get_user(user.id)
    
    if not user_data:
        await start(update, context)
        return
    
    user_lang = user_data.get('language', 'en')
    
    # Check credits
    credits = db.get_credits(user.id)
    if credits['total'] <= 0:
        keyboard = [[InlineKeyboardButton("🛒 Buy Credits", url="https://buy.stripe.com/test_yourlink")]]
        await update.message.reply_text(
            get_text(user_lang, 'no_credits'),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    # Save message to context
    context.user_data['incoming_message'] = update.message.text
    context.user_data['conversation_history'] = db.get_conversation_history(user.id, limit=5)
    
    # Ask for tone
    keyboard = [
        [InlineKeyboardButton(TONES['casual']['name'], callback_data="tone_casual"),
         InlineKeyboardButton(TONES['professional']['name'], callback_data="tone_professional")],
        [InlineKeyboardButton(TONES['flirty']['name'], callback_data="tone_flirty")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        get_text(user_lang, 'choose_tone'),
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    user_data = db.get_user(user.id)
    user_lang = user_data.get('language', 'en')
    
    data = query.data
    
    # Handle tone selection
    if data.startswith('tone_'):
        tone = data.replace('tone_', '')
        context.user_data['selected_tone'] = tone
        
        # Ask for language
        keyboard = [
            [InlineKeyboardButton(LANGUAGES['en']['name'], callback_data="lang_en"),
             InlineKeyboardButton(LANGUAGES['nl']['name'], callback_data="lang_nl")],
            [InlineKeyboardButton(LANGUAGES['es']['name'], callback_data="lang_es")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            get_text(user_lang, 'choose_language'),
            reply_markup=reply_markup
        )
    
    # Handle language selection
    elif data.startswith('lang_'):
        response_lang = data.replace('lang_', '')
        context.user_data['response_language'] = response_lang
        
        # Show generating message
        await query.edit_message_text(get_text(user_lang, 'generating'))
        
        # Generate responses
        await generate_responses(query, context, user, user_lang)
    
    # Handle copy button
    elif data.startswith('copy_'):
        await query.answer(get_text(user_lang, 'copied'), show_alert=True)
    
    # Handle more options
    elif data == 'more_options':
        await query.edit_message_text(get_text(user_lang, 'generating'))
        await generate_responses(query, context, user, user_lang)
    
    # Handle new conversation
    elif data == 'new_conversation':
        await query.answer(get_text(user_lang, 'new_conversation'))
        context.user_data.clear()
    
    # Handle credits view
    elif data == 'credits':
        credits = db.get_credits(user.id)
        stats = db.get_user_stats(user.id)
        
        expiry_date = (datetime.now() + timedelta(days=CREDIT_EXPIRY_DAYS)).strftime('%Y-%m-%d')
        avg_per_day = round(stats['total_used'] / max(stats['days_active'], 1), 1)
        
        text = get_text(user_lang, 'credits_status',
            total=credits['total'],
            free=credits['free'],
            purchased=credits['purchased'],
            expiry=expiry_date,
            used_month=stats['used_this_month'],
            total_used=stats['total_used'],
            avg=avg_per_day
        )
        
        keyboard = [[InlineKeyboardButton("🛒 Buy Credits", url="https://buy.stripe.com/test_yourlink")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    # Handle history view
    elif data == 'history':
        history = db.get_conversation_history(user.id, limit=10)
        if not history:
            await query.edit_message_text(get_text(user_lang, 'history_empty'))
            return
        
        text = "📚 **Recent conversations:**\n\n"
        for i, conv in enumerate(history[:5], 1):
            text += f"{i}. {conv['message'][:50]}...\n"
            text += f"   ↳ {conv['responses'][0][:50]}...\n\n"
        
        keyboard = [[InlineKeyboardButton("« Back", callback_data="back_to_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    # Handle language change
    elif data == 'change_language':
        keyboard = [
            [InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en")],
            [InlineKeyboardButton("🇳🇱 Nederlands", callback_data="set_lang_nl")]
        ]
        await query.edit_message_text("Choose your language:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data.startswith('set_lang_'):
        new_lang = data.replace('set_lang_', '')
        db.update_user_language(user.id, new_lang)
        await query.answer(f"Language set to {LANGUAGES.get(new_lang, {}).get('name', 'English')}", show_alert=True)

async def generate_responses(query, context, user, user_lang):
    """Generate AI responses using OpenAI"""
    incoming_message = context.user_data.get('incoming_message', '')
    tone = context.user_data.get('selected_tone', 'casual')
    response_lang = context.user_data.get('response_language', 'en')
    conversation_history = context.user_data.get('conversation_history', [])
    
    # Build context
    history_context = ""
    if conversation_history:
        history_context = "Previous conversation context:\n"
        for conv in conversation_history[-3:]:
            history_context += f"- Them: {conv['message']}\n  You: {conv['responses'][0]}\n"
    
    # Build prompt
    system_prompt = f"""You are Whatsay, an expert conversation coach. Generate natural, authentic responses in {LANGUAGES[response_lang]['code']}.

Rules:
- Sound like the user would naturally speak, not like AI
- Match the {TONES[tone]['desc']} tone
- Keep responses 1-3 sentences max
- Be culturally appropriate for {LANGUAGES[response_lang]['code']} speakers
- Avoid clichés and obvious AI phrasing

Provide 3 distinct options:
1. Safe/balanced - works in most situations
2. Bold/direct - more personality
3. Warm/engaging - builds connection

Format: Return ONLY the 3 responses, numbered 1-3, nothing else."""

    user_prompt = f"""{history_context}

LAST MESSAGE RECEIVED:
"{incoming_message}"

Generate 3 {TONES[tone]['desc']} responses in {LANGUAGES[response_lang]['code']}."""

    try:
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Cheap and good quality
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            max_tokens=300
        )
        
        # Parse responses
        ai_response = response.choices[0].message.content.strip()
        responses = []
        
        for line in ai_response.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering
                clean_line = line.lstrip('123456789.-) ').strip()
                if clean_line:
                    responses.append(clean_line)
        
        # Ensure we have 3 responses
        if len(responses) < 3:
            responses = ai_response.split('\n\n')[:3]
        
        # Deduct credit
        db.use_credit(user.id)
        
        # Save to history
        db.save_conversation(user.id, incoming_message, responses, tone, response_lang)
        
        # Build response message
        text = f"💬 **{TONES[tone]['name']} responses ({LANGUAGES[response_lang]['name']}):**\n\n"
        
        keyboard = []
        for i, resp in enumerate(responses[:3], 1):
            text += f"{i}. _{resp}_\n\n"
            keyboard.append([
                InlineKeyboardButton(f"📋 {i}", callback_data=f"copy_{i}"),
            ])
        
        # Add action buttons
        keyboard.append([
            InlineKeyboardButton("🔄 More options", callback_data="more_options"),
            InlineKeyboardButton("✨ New chat", callback_data="new_conversation")
        ])
        keyboard.append([
            InlineKeyboardButton("📚 History", callback_data="history"),
            InlineKeyboardButton("💎 Credits", callback_data="credits")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error generating responses: {e}")
        await query.edit_message_text(get_text(user_lang, 'error'))

def main():
    """Start the bot"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
    
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start bot
    logger.info("Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
