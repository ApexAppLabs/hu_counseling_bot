# HU Counseling Service Bot 🙏

**Anonymous peer counseling platform for student gospel fellowship**

A safe, confidential space where students can receive biblical guidance and support from trained peer counselors. All conversations are completely anonymous.

---

## 🌟 Features

### For Users
- 🆘 **Request Anonymous Counseling** - Select from 14 topic categories
- 💬 **Private Chat Sessions** - Real-time anonymous messaging
- 🔒 **Complete Privacy** - No personal information exposed
- ⭐ **Rate Sessions** - Provide feedback on counseling quality
- 🆘 **Crisis Support** - Priority matching for emergencies

### For Counselors
- 👨‍⚕️ **Counselor Dashboard** - Manage sessions and availability
- 📊 **Statistics & Ratings** - Track your impact and performance
- 🎯 **Specialization-Based** - Matched to topics you're trained in
- ✅ **Accept/Decline** - Control your workload
- 🟢 **Availability Toggle** - Go online/offline anytime

### For Admins
- 🛡️ **Admin Panel** - Complete system oversight
- 📋 **Approve Counselors** - Review and approve applications
- 📊 **System Statistics** - Monitor usage and performance
- 👥 **User Management** - Handle issues and moderation

---

## 🎯 Counseling Topics

The bot supports 14 specialized counseling areas:

| Icon | Topic | Description |
|------|-------|-------------|
| 🙏 | Spiritual Growth & Faith | Prayer, Bible study, spiritual struggles |
| 🧠 | Mental Health & Wellness | Anxiety, depression, stress, emotions |
| 💑 | Relationships & Dating | Dating, friendships, family issues |
| 📚 | Academic Struggles | Study stress, exam anxiety, time management |
| 🎯 | Identity & Purpose | Life purpose, calling, self-worth |
| 🚫 | Addiction & Habits | Addictions, bad habits, temptations |
| 💔 | Grief & Loss | Loss, grief, mourning, trauma |
| 💰 | Financial Concerns | Money issues, financial stress, budgeting |
| 👨‍👩‍👧‍👦 | Family Issues | Family conflicts, parental pressure |
| 💼 | Career & Future | Career guidance, future planning |
| ✝️ | Ministry & Service | Leadership, evangelism questions |
| ❓ | Doubt & Questions | Faith doubts, theological questions |
| 🆘 | **Crisis & Emergency** | **PRIORITY** - Immediate help needed |
| 💬 | General Counseling | General advice and support |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Telegram Bot Token
- Your Telegram User ID

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/counseling_bot.git
cd counseling_bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**

Create `.env` file:
```env
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_IDS=your_telegram_user_id
```

4. **Run the bot**
```bash
python main_counseling_bot.py
```

5. **Approve first counselor**
- Have someone register as counselor
- Approve them via Admin Panel
- Start accepting sessions!

📖 **For detailed instructions, see [QUICK_START.md](QUICK_START.md)**

---

## 🏗️ Architecture

### Core Components

```
counseling_bot/
├── main_counseling_bot.py          # Entry point - run this!
├── counseling_database.py          # Database management (SQLite)
├── matching_system.py              # Advanced matching algorithm
├── hu_counseling_bot.py            # Main bot logic
├── hu_counseling_bot_part2.py      # Counselor & admin functions
├── requirements.txt                # Python dependencies
├── .env                            # Configuration (create this)
└── hu_counseling.db               # Database (auto-created)
```

### Database Schema

**8 Tables:**
- `users` - User profiles and settings
- `counselors` - Counselor profiles and specializations
- `counseling_sessions` - Session requests and history
- `session_messages` - Chat message history
- `counselor_availability` - Scheduling (future feature)
- `bot_stats` - System statistics
- `admins` - Admin access control

---

## 🎯 Advanced Matching Algorithm

The bot uses a sophisticated scoring system to match users with the best counselor:

**Scoring Criteria:**
1. **Specialization Match** (40 pts) - Counselor expertise in topic
2. **Load Balancing** (20 pts) - Fair distribution of sessions
3. **Rating Quality** (20 pts) - Counselor performance ratings
4. **Experience Bonus** (10 pts) - Veteran counselor advantage
5. **Crisis Priority** (10 pts) - Emergency response bonus

**Result:** Users get the most qualified, available counselor for their needs.

---

## 🔒 Privacy & Security

### Anonymity Features
- ✅ No names exchanged between parties
- ✅ Users see only "User #ID"
- ✅ Counselors see only "Counselor #ID"
- ✅ All messages relayed through bot
- ✅ No direct contact information shared

### Data Protection
- ✅ Local SQLite database (no cloud by default)
- ✅ Session messages stored securely
- ✅ Optional: Implement message encryption
- ✅ Admin-only access to system data

---

## 📊 System Statistics

The bot tracks:
- Total users and active users
- Number of counselors and availability
- Total, active, and completed sessions
- Topic distribution and trends
- Counselor ratings and performance
- System health metrics

---

## 🛠️ Configuration

### Environment Variables

```env
# Required
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# Required - Comma-separated admin user IDs
ADMIN_IDS=123456789,987654321

# Optional - For webhook deployment
WEBHOOK_URL=https://your-app.herokuapp.com
PORT=8443
```

### Bot Commands

Set these in @BotFather:
```
start - Start the bot
help - Show help information
about - About HU Counseling Service
```

---

## 🚀 Deployment

### Local Development
```bash
python main_counseling_bot.py
```

### Heroku
```bash
# Create Procfile
echo "worker: python main_counseling_bot.py" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
heroku ps:scale worker=1
```

### Railway.app
1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically

### VPS/Server
```bash
# Using systemd
sudo systemctl enable counseling-bot
sudo systemctl start counseling-bot

# Or using nohup
nohup python main_counseling_bot.py > bot.log 2>&1 &
```

📖 **For complete deployment guide, see [SETUP_GUIDE.md](SETUP_GUIDE.md)**

---

## 📝 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Get running in 5 minutes
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup and configuration
- **[APP_ANALYSIS.md](APP_ANALYSIS.md)** - System architecture and design decisions

---

## 🤝 Contributing

This bot is designed for the student gospel fellowship community. Contributions welcome!

### To Contribute:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request

---

## 🆘 Support & Resources

### Crisis Guidance
If you are in immediate danger or feel you might harm yourself or someone else, please seek help around you immediately:

- Go to the nearest clinic, hospital, or health centre
- Reach out to a trusted friend, family member, fellowship leader, or university staff
- Contact your university clinic, counseling office, or campus security
- Use any available local emergency numbers in your area

### Technical Support
- Check logs for errors
- Review [SETUP_GUIDE.md](SETUP_GUIDE.md) troubleshooting section
- Open GitHub issue for bugs

---

## 📜 License

This project is open source and available for use by gospel fellowship communities.

---

## 🙏 Acknowledgments

Built with:
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- SQLite - Lightweight database
- Love and prayer from the fellowship community

---

## 📞 Contact

For questions, suggestions, or support:
- Open a GitHub issue
- Contact fellowship leadership
- Email: [Your contact email]

---

**"Carry each other's burdens, and in this way you will fulfill the law of Christ."**
*- Galatians 6:2*

---

## ✅ Project Status

**Status:** ✅ Production Ready

**Version:** 3.0 - HU Counseling Service

**Last Updated:** 2024

**Features Complete:**
- ✅ User counseling request system
- ✅ Advanced matching algorithm
- ✅ Anonymous messaging relay
- ✅ Counselor registration & approval
- ✅ Admin management panel
- ✅ Rating & feedback system
- ✅ Crisis priority handling
- ✅ 14 specialized counseling topics

---

Made with ❤️ and faith for the student gospel fellowship community.
