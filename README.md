# 🤖 Whatsay Bot

**Never have awkward conversations again!** Whatsay is a Telegram bot that helps you find perfect responses for any situation.

## ✨ Features

- 💬 3 AI-generated responses for every message
- 🎭 Multiple tones: Casual, Professional, Flirty
- 🌍 Multi-language: English, Dutch, Spanish
- 💎 Credit system with free starter credits
- 📚 Conversation history
- 📊 Usage statistics
- 🔄 "More options" functionality
- 📋 Easy copy buttons

## 🚀 Deployment to Railway (STEP BY STEP)

### Step 1: Create Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Start a chat and send: `/newbot`
3. Give your bot a name: `Whatsay Helper`
4. Give it a username: `whatsay_helper_bot` (must end in `_bot`)
5. You'll receive a **TOKEN** → save it!
   - Looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### Step 2: Get OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Log in to your OpenAI account
3. Click **"Create new secret key"**
4. Name it: `Whatsay Bot`
5. Copy the key (starts with `sk-...`)

### Step 3: Create GitHub Repository

1. Go to https://github.com
2. Log in (create account if needed)
3. Click `+` (top right) → `New repository`
4. Name: `whatsay-bot`
5. Choose Public or Private
6. Click **Create repository**

### Step 4: Upload Code to GitHub

**Option A: Via GitHub Web Interface (easiest)**

1. Go to your new repository on GitHub
2. Look for the blue link that says **"uploading an existing file"**
3. Click it
4. Upload ALL files from this folder:
   - `bot.py`
   - `database.py`
   - `requirements.txt`
   - `Procfile`
   - `.env.example`
   - `.gitignore`
   - `runtime.txt`
5. Click `Commit changes`

**Option B: Via Git (if you have Git installed)**

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-username/whatsay-bot.git
git push -u origin main
```

### Step 5: Railway Deployment

1. Go to https://railway.app
2. Click **"Start a New Project"**
3. Click **"Login with GitHub"**
4. Click **"Deploy from GitHub repo"**
5. Select `whatsay-bot` repository
6. Railway will start deploying automatically

### Step 6: Add Environment Variables

1. In Railway, click on your project
2. Go to **"Variables"** tab (at the top)
3. Click **"Variables"**

Add these variables:

**Variable 1:**
- Name: `TELEGRAM_BOT_TOKEN`
- Value: (your token from BotFather)

**Variable 2:**
- Name: `OPENAI_API_KEY`
- Value: (your OpenAI key)

4. Click **"Redeploy"** (top right)

### Step 7: Verify It Works

1. Go to **"Deployments"** tab
2. Click **"View Logs"**
3. Look for: `Bot started!`

**🎉 If you see "Bot started!" = SUCCESS!**

### Step 8: Test Your Bot!

1. Open Telegram
2. Search for your bot: `@whatsay_helper_bot` (or your username)
3. Click it and press **START**
4. Send a message
5. 🎉 **You're live!**

## 💰 Pricing Strategy

### Free Start
- 12 free credits on signup
- Credits expire after 7 days

### Credit Packs
- 50 credits - €7.99
- 150 credits - €19.99
- 500 credits - €49.99

### Subscriptions
- Pro - €14.99/month - 100 credits
- Ultimate - €29.99/month - Unlimited

## 💸 Costs

### Per Question
- OpenAI GPT-4o-mini: ~€0.0002 per question
- 50 questions = €0.01 cost
- **Profit margin: 95%+**

### Hosting
- Railway: €5/month for 24/7 uptime
- Free tier available for testing

## 🔧 Technical Details

### Stack
- **Bot Framework**: python-telegram-bot
- **AI**: OpenAI GPT-4o-mini
- **Database**: SQLite
- **Hosting**: Railway
- **Payments**: Stripe (optional, later)

### Database Schema

**Users**
- user_id, username, language
- free_credits, purchased_credits, subscription_credits
- total_used, created_at, last_active

**Conversations**
- user_id, incoming_message, responses
- tone, language, created_at

**Usage Stats**
- user_id, action, credits_used, created_at

## 📊 Monitoring

Railway gives you automatically:
- Logs (see all bot activity)
- Metrics (CPU, memory usage)
- Deployments (rollback capability)

## 🛠️ Local Testing (optional)

If you want to test locally for development:

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your keys

# Run the bot
python bot.py
```

## 🔐 Security Notes

- ❌ NEVER share your Telegram Bot Token
- ❌ NEVER share your OpenAI API key
- ✅ Environment variables are safe in Railway
- ✅ Database is local (no cloud needed for MVP)

## 📈 Next Steps

1. **Integrate payments** - Add Stripe payment links
2. **Marketing** - Create TikTok/Instagram content
3. **Analytics** - Track conversions and churn
4. **Features** - Voice messages, image analysis
5. **Scale** - More languages, niche modes

## 🐛 Troubleshooting

**Bot not responding:**
- Check Railway logs for errors
- Verify environment variables are correct
- Test with `/start` command

**OpenAI errors:**
- Check if you have credit on OpenAI account
- Verify API key is correct

**Database errors:**
- Railway persistent storage automatically enabled
- Database reset: delete `whatsay.db` and redeploy

## 💡 Marketing Tips

### TikTok/Reels Content Ideas
- "POV: You don't know what to reply" → show bot
- "Dating tips hack" → demo Flirty mode
- "Professional emails made easy" → show Professional mode

### Reddit
- r/socialskills - "Tool that helped my social anxiety"
- r/dating_advice - "Never be speechless again"
- r/GetMotivated - Productivity angle

### Discord/Telegram
- Join dating/social communities
- Offer value first, mention bot naturally

## 📞 Support

Questions? Check Railway docs: https://docs.railway.app

---

**Built by:** [Your name]
**Version:** 1.0
**Last updated:** December 2024

🚀 **Good luck with your bot!**
