# Text Strings for Amharic Translation

This document contains all the user-facing text strings in the HU Counseling Service Bot that need to be translated to Amharic.

## Main Menu Buttons
- "🆘 Request Counseling"
- "ℹ️ About Us"
- "❓ Help"
- "👨‍⚕️ Counselor Dashboard"
- "📝 Become a Counselor"
- "🛡️ Admin Panel"

## Counseling Request Flow

### Topic Selection
```
**Request Counseling** 🆘

Please select the topic that best describes what you'd like to talk about:

💡 *Choose the category that fits best. Your counselor will be matched based on their expertise.*

🔒 *Remember: Everything is completely anonymous and confidential.*
```

### Gender Selection
```
**Topic Selected:** {topic_icon} **{topic_name}**

**Select Your Gender** 👤

Choose an option:
```

Gender options:
- "👨 Male"
- "👩 Female"
- "🔒 Prefer not to say (Anonymous)"
- "◀️ Back"

### Crisis Support
```
**🆘 CRISIS SUPPORT REQUESTED**

You've selected: {topic_icon} **{topic_name}**

⚠️ **If you are in immediate danger or feel you might harm yourself or someone else, please seek help around you immediately.**

You can:
• Go to the nearest clinic or health centre
• Reach out to a trusted person (friend, fellowship family, fellowship leader)
• Contact local emergency services or campus security in your area

We're connecting you with a counselor right now. If you'd like, you can briefly describe your situation while we find someone:

*Type your message or click "Skip" to connect immediately.*
```

Buttons:
- "⏭️ Skip - Connect Now"

### Regular Topics Description Request
```
**Topic Selected:** {topic_icon} **{topic_name}**

{topic_data.get('description', '')}

Would you like to briefly describe your situation? This helps us match you with the right counselor.

*Type your message or click "Skip" to proceed.*
```

Buttons:
- "⏭️ Skip"
- "❌ Cancel"

### Session Matching Messages
To user:
```
✅ **Match Found!**

We've matched you with a counselor specialized in **{topic_data.get('name', topic)}**.

Waiting for the counselor to accept...

🔒 Remember: Everything is anonymous and confidential.
```

To counselor:
```
🔔 New Counseling Request

Topic: {topic_data.get('icon', '💬')} {topic_data.get('name', topic_key)}
User Gender: {gender_display}
Description: {preview}

Would you like to accept this session?
```

Buttons:
- "✅ Accept Session"
- "❌ Decline"

## Session Management

### Session Started Messages
To user:
```
✅ Session Started!

Your counselor has joined. You can now begin your conversation.

Topic: {topic_data['icon']} {topic_data['name']}

🔒 Remember: Everything is anonymous and confidential.

Type your message below to start.
```

To counselor:
```
✅ Session Started!

Topic: {topic_data['icon']} {topic_data['name']}
User Gender: {gender_display}
User's Description: {safe_desc}

The user can now send messages. Wait for their first message.
```

### Session Ending Confirmation
```
**Are you sure you want to end this session?**

The conversation will be closed for both parties.
```

Buttons:
- "✅ Yes, End/Cancel"
- "❌ No, Continue"

### Session Ended Messages
To user (when cancelling before match):
```
✅ **Request Cancelled**

Your counseling request has been cancelled.

Feel free to request counseling again anytime you need support. 🙏
```

To user (when ending active session):
```
**Session Ended**

Thank you for using HU Counseling Service.

**Would you like to rate this session?**
```

Rating buttons:
- "⭐ Rate Session"
- "⏭️ Skip"

To counselor:
```
**Session Ended**

The user has ended the session. Great work! 🙏
```

## Counselor Registration

### Specialization Selection
```
**Become a Counselor** 👨‍⚕️

First, select your counseling specializations.

💡 *Choose all topics you're comfortable counseling on. You can update these later.*
```

Buttons:
- "✅ Done Selecting"
- "◀️ Back"

### Gender Selection for Counselors
```
**Select Your Gender** 👤

Choose an option:
```

### Bio Entry
```
**Great! Your expertise:** 👍

{topics_text}

Now, please share a brief bio (2-3 sentences) about yourself that will be shown to users when you're matched with them.

💡 *Include your year, faculty/department, and anything else you'd like users to know about you as a counselor.*

📝 *Type your bio below:*
```

### Application Submission
```
Thank you for applying to be a counselor. Your application has been sent to the admin team for review.

We'll notify you once your application is approved. This usually takes a short time.

**What happens next:**
1. Admins review your application
2. You may be contacted for a brief interview
3. Once approved, you'll receive access to the Counselor Dashboard

Thank you for your willingness to serve! 🙏
```

Notification to admins:
```
🔔 **New Counselor Application**

**Applicant:** {display_name}
**User ID:** `{user_id}`
**Specializations:** {topics_list}

**Bio:**
{bio}

📋 Go to Admin Panel → Pending Applications to review.
```

## Counselor Dashboard

```
**Counselor Dashboard** 👨‍⚕️

**Status:** {status_text}
**Total Sessions:** {stats.get('total_sessions', 0)}

Choose an option:
```

Status indicators:
- "🟢 Online" (when available)
- "🔴 Offline" (when not available)

Buttons:
- "🟢 Go Online" / "🔴 Go Offline"
- "📊 My Statistics"
- "📱 Go to Current Session View"
- "◀️ Back to Menu"

## Admin Panel

### Main Admin Panel
```
**Admin Panel** 🛡️

**System Statistics:**
👥 Total Users: {stats.get('total_users', 0)}
👨‍⚕️ Total Counselors: {stats.get('total_counselors', 0)}
🟢 Active Counselors: {stats.get('active_counselors', 0)}

**Sessions:**
📊 Total: {stats.get('total_sessions', 0)}
🔄 Active: {stats.get('active_sessions', 0)}
✅ Completed: {stats.get('completed_sessions', 0)}

**Choose an action:**
```

Buttons:
- "📋 Pending Applications"
- "📊 Detailed Statistics"
- "👥 Manage Counselors"
- "🔔 Pending Sessions"
- "◀️ Back"

### Pending Applications
```
**Pending Counselor Applications** ({len(pending)})

{application_details}
```

Buttons:
- "Review #{app['counselor_id']}"
- "◀️ Back"

### Detailed Statistics
```
**System Statistics** 📊

**👥 Users & Counselors:**
• Total Users: **{total_users}**
• Total Counselors: **{total_counselors}**
  ├─ ✅ Approved: {approved_counselors}
  ├─ 🟢 Currently Online: {online_counselors}
  ├─ ⏳ Pending: {pending_counselors}
  ├─ ❌ Rejected: {rejected_counselors}
  ├─ 🔴 Deactivated: {deactivated_counselors}
  └─ 🚫 Banned: {banned_counselors}

**📊 Sessions Overview:**
• Total Sessions: **{total_sessions}**
  ├─ 🔄 Active Now: {active_sessions}
  ├─ ✅ Completed: {completed_sessions}
  ├─ ⏳ Pending (waiting): {pending_sessions}
  └─ 🎯 Matched (not started): {matched_sessions}
• Completion Rate: **{completion_rate:.1f}%**

**💬 Messages:**
• Total Messages Exchanged: **{total_messages}**

**⭐ Quality Metrics:**
• Average Rating: **{avg_rating:.2f}/5.0**
• Total Ratings Received: **{total_ratings}**

**🔥 Top 5 Topics:**
{topics_text if topics_text else '• No sessions yet'}

**🏥 System Health:** ✅ Operational
```

Buttons:
- "🔄 Refresh"
- "◀️ Back to Admin Panel"

### Counselor Management
```
**Counselor Management** 👥

Click on a counselor to manage:

{counselor_list}
```

Buttons:
- Individual counselor buttons with status emojis
- "📋 View Pending Applications"
- "🔄 Refresh List"
- "◀️ Back"

### Pending Sessions
```
**Pending Sessions** 🔔

There are **{len(pending)}** sessions waiting for counselors:

{session_details}

💡 **Note:** These sessions are waiting for available counselors to come online.
```

Buttons:
- "🔄 Refresh"
- "◀️ Back"

## Help and About Sections

### Help Text
```
**How to use HU Counseling Service:**

**For Users Seeking Help:**
1️⃣ Click "Request Counseling"
2️⃣ Select a topic that fits your situation
3️⃣ Describe your situation (optional)
4️⃣ Wait to be matched with a counselor
5️⃣ Start your anonymous chat session

**During a Session:**
• All messages are private and anonymous
• You can end the session anytime
• Both parties remain anonymous

**For Counselors:**
• Click "Counselor Dashboard" to manage sessions
• Toggle your availability
• Accept or decline session requests

**Important:**
🆘 If you're in crisis or having suicidal thoughts, please select "Crisis & Substance Support" to be prioritized for support.
If you are in immediate danger, please seek help offline as well:
• Go to the nearest clinic, hospital, or health centre
• Reach out to a trusted person (friend, family, fellowship leader, or university staff)
• Contact local emergency services or campus security in your area

**Contact Admin:**
If you have issues, contact the administrators.
```

Buttons:
- "◀️ Back"

### About Text
```
**About HU Counseling Service** 🙏

A safe, confidential space where students can receive biblical guidance and support from trained peer counselors. All conversations are completely anonymous.

**Our Mission:**
To provide a supportive community where students can seek guidance and find encouragement through faith-centered counseling.

**How It Works:**
1. **Request Help** - Select a topic and describe your situation
2. **Get Matched** - We connect you with a trained peer counselor
3. **Chat Anonymously** - Have a private conversation in a safe space
4. **Get Support** - Receive guidance and encouragement

**Confidentiality:**
🔒 All conversations are completely anonymous
🔒 No personal information is shared between users
🔒 Counselors never see your identity
🔒 Your privacy is our top priority

**Counselor Training:**
All counselors are trained students who have completed our counseling program and are supervised by experienced mentors.

**Need Immediate Help?**
If you're in crisis or having thoughts of self-harm:
1. Select "Crisis & Substance Support" when requesting counseling
2. Reach out to a trusted person nearby
3. Contact local emergency services

**Contact:**
For technical issues or questions, please contact the administrators.
```

## Error Messages

- "⚠️ Session error: Topic not found. Please start over with /start"
- "⚠️ This session is no longer available."
- "⚠️ You don't have an active session."
- "⚠️ You don't have admin access."
- "⚠️ Session has already ended."
- "⚠️ You don't have an active session."

## Crisis Resources
Default crisis text:
```
⚠️ **If you are in immediate danger or feel you might harm yourself or someone else, please seek help around you immediately (nearby people, university clinic, health centre, hospital, or campus security).**

**Emergency:** Local emergency services / campus security

**Crisis Resources:**
• **Local crisis support:** Contact your university clinic, counseling office, or local health centre
• **Trusted people around you:** Reach out to a close friend, family member, fellowship leader, or university staff
```

## Session Timeout Messages

To user:
```
⏰ **Session Timeout**

Your counseling session has been automatically ended due to {self.timeout_hours} hours of inactivity.

If you still need support, feel free to request a new session anytime. 🙏
```

To counselor:
```
⏰ **Session Timeout**

Your counseling session (ID: #{session_id}) has been automatically ended due to inactivity.

No action needed from you.
```

## Rating System

Rating submission confirmation:
```
✅ **Thank you for your feedback!**

You rated this session: {'⭐' * rating}

Your feedback helps us improve our counseling service. 🙏
```

## Topic Names and Descriptions

1. Academic & Career:
   - Name: "Academic & Career"
   - Icon: "📚"
   - Description: "Academic struggles, exams, university life, career choices, work and finances"

2. Mental Health & Emotional:
   - Name: "Mental Health & Emotional"
   - Icon: "🧠"
   - Description: "Anxiety, depression, stress, grief, trauma, emotional struggles"

3. Relationships & Social Life:
   - Name: "Relationships & Social Life"
   - Icon: "�"
   - Description: "Friendships, family, dating, social life and community"

4. Life Skills & Personal Growth:
   - Name: "Life Skills & Personal Growth"
   - Icon: "🌱"
   - Description: "Identity, purpose, habits, faith walk, life decisions and personal growth"

5. Crisis & Substance Support:
   - Name: "Crisis & Substance Support"
   - Icon: "🆘"
   - Description: "Immediate crisis, safety concerns, suicidal thoughts, and substance use struggles"

6. Other Counseling:
   - Name: "Other Counseling"
   - Icon: "💬"
   - Description: "If you're not sure where your situation fits, choose this."

## System Messages

Bot startup message:
```
🚀 HU Counseling Service Bot is starting...
```

Database connection messages:
```
✅ Database connected successfully
❌ Database connection failed: {e}
```

Missing configuration messages:
```
❌ BOT_TOKEN not found in environment variables!
Please create a .env file with BOT_TOKEN=your_bot_token

❌ ADMIN_IDS not found or empty in environment variables!
Please set ADMIN_IDS in .env file (e.g., ADMIN_IDS=123456789)
Without ADMIN_IDS, the admin panel will NOT work!
```Text Strings for Amharic Translation
This document contains all the user-facing text strings in the HU Counseling Service Bot that need to be translated to Amharic.

Main Menu Buttons
"🆘 Request Counseling"

"🆘 የምክር አገልግሎት ይጠይቁ"

"ℹ️ About Us"

"ℹ️ ስለ እኛ"

"❓ Help"

"❓ እርዳታ"

"👨‍⚕️ Counselor Dashboard"

"👨‍⚕️ የአማካሪ ዳሽቦርድ"

"📝 Become a Counselor"

"📝 አማካሪ ይሁኑ"

"🛡️ Admin Panel"

"🛡️ የአስተዳዳሪ ፓነል"

Counseling Request Flow
Topic Selection
**Request Counseling** 🆘
**የምክር አገልግሎት ይጠይቁ** 🆘

Please select the topic that best describes what you'd like to talk about:
እባክዎ መወያየት የሚፈልጉትን ጉዳይ በተሻለ ሁኔታ የሚገልጸውን ርዕስ ይምረጡ፡

💡 *Choose the category that fits best. Your counselor will be matched based on their expertise.*
💡 *ጉዳይዎ የሚካተትበትን ትክክለኛ ምድብ ይምረጡ። አማካሪዎ የሚመደበው በመረጡት ዘርፍ ባላቸው ልምድ መሰረት ነው።*

🔒 *Remember: Everything is completely anonymous and confidential.*
🔒 *ያስታውሱ፡ ማንኛውም ነገር በምስጢር የሚጠበቅ እና ማንነትዎ የማይታወቅ ነው።*
Gender Selection
**Topic Selected:** {topic_icon} **{topic_name}**
**የተመረጠው ርዕስ:** {topic_icon} **{topic_name}**

**Select Your Gender** 👤
**ፆታዎን ይምረጡ** 👤

Choose an option:
አማራጭ ይምረጡ፡
Gender options:

"👨 Male"

"👨 ወንድ"

"👩 Female"

"👩 ሴት"

"🔒 Prefer not to say (Anonymous)"

"🔒 መግለጽ አልፈልግም (በምስጢር)"

"◀️ Back"

"◀️ ተመለስ"

Crisis Support
**🆘 CRISIS SUPPORT REQUESTED**
**🆘 አጣዳፊ የድጋፍ ጥያቄ**

You've selected: {topic_icon} **{topic_name}**
መርጠዋል: {topic_icon} **{topic_name}**

⚠️ **If you are in immediate danger or feel you might harm yourself or someone else, please seek help around you immediately.**
⚠️ **አጣዳፊ አደጋ ላይ ከሆኑ ወይም እራስዎን ወይም ሌላ ሰው ሊጎዱ እንደሚችሉ ከተሰማዎት፣ እባክዎ በአካባቢዎ ካሉ ሰዎች በአስቸኳይ እርዳታ ይጠይቁ።**

You can:
ማድረግ የሚችሏቸው ነገሮች፡
• Go to the nearest clinic or health centre
• በአቅራቢያዎ ወደሚገኝ ክሊኒክ ወይም ጤና ጣቢያ ይሂዱ
• Reach out to a trusted person (friend, fellowship family, fellowship leader)
• ለሚያምኑት ሰው (ጓደኛ፣ የፌሎውሺፕ ቤተሰብ፣ የፌሎውሺፕ መሪ) ያናግሩ
• Contact local emergency services or campus security in your area
• የአካባቢውን የድንገተኛ አደጋ አገልግሎቶች ወይም የግቢውን ጥበቃ ያግኙ

We're connecting you with a counselor right now. If you'd like, you can briefly describe your situation while we find someone:
አሁን ከአማካሪ ጋር እያገናኘንዎት ነው። ከአማካሪ ጋር እስክናገናኝዎት ድረስ ከፈለጉ ሁኔታዎን በአጭሩ መግለፅ ይችላሉ፡

*Type your message or click "Skip" to connect immediately.*
*መልእክትዎን ይጻፉ ወይም ወዲያውኑ ለመገናኘት "ለማለፍ" የሚለውን ይጫኑ።*
Buttons:

"⏭️ Skip - Connect Now"

"⏭️ ለማለፍ - አሁን አገናኝ"

Regular Topics Description Request
**Topic Selected:** {topic_icon} **{topic_name}**
**የተመረጠው ርዕስ:** {topic_icon} **{topic_name}**

{topic_data.get('description', '')}
*(This part pulls the description from the database, translations for descriptions are at the bottom)*

Would you like to briefly describe your situation? This helps us match you with the right counselor.
ሁኔታዎን በአጭሩ መግለጽ ይፈልጋሉ? ይህ ትክክለኛውን አማካሪ እንድንመድብልዎ ይረዳናል።

*Type your message or click "Skip" to proceed.*
*መልእክትዎን ይጻፉ ወይም ለመቀጠል "ለማለፍ" የሚለውን ይጫኑ።*
Buttons:

"⏭️ Skip"

"⏭️ ለማለፍ"

"❌ Cancel"

"❌ ሰርዝ"

Session Matching Messages
To user:

✅ **Match Found!**
✅ **ተዛማጅ አማካሪ ተገኝቷል!**

We've matched you with a counselor specialized in **{topic_data.get('name', topic)}**.
በ **{topic_data.get('name', topic)}** ላይ ከተካነ አማካሪ ጋር አገናኝተንዎታል።

Waiting for the counselor to accept...
አማካሪው እስኪቀበል በመጠበቅ ላይ...

🔒 Remember: Everything is anonymous and confidential.
🔒 ያስታውሱ፡ ማንኛውም ነገር በምስጢር የሚጠበቅ እና ማንነትዎ የማይታወቅ ነው።
To counselor:

🔔 New Counseling Request
🔔 አዲስ የምክር ጥያቄ

Topic: {topic_data.get('icon', '💬')} {topic_data.get('name', topic_key)}
ርዕስ: {topic_data.get('icon', '💬')} {topic_data.get('name', topic_key)}

User Gender: {gender_display}
የተጠቃሚ ፆታ: {gender_display}

Description: {preview}
መግለጫ: {preview}

Would you like to accept this session?
ይህን የምክር ክፍለ ጊዜ መቀበል ይፈልጋሉ?
Buttons:

"✅ Accept Session"

"✅ ክፍለ ጊዜውን ተቀበል"

"❌ Decline"

"❌ አትቀበል"

Session Management
Session Started Messages
To user:

✅ Session Started!
✅ ክፍለ ጊዜው ተጀምሯል!

Your counselor has joined. You can now begin your conversation.
አማካሪዎ ገብቷል። አሁን ውይይትዎን መጀመር ይችላሉ።

Topic: {topic_data['icon']} {topic_data['name']}
ርዕስ: {topic_data['icon']} {topic_data['name']}

🔒 Remember: Everything is anonymous and confidential.
🔒 ያስታውሱ፡ ማንኛውም ነገር በምስጢር የሚጠበቅ እና ማንነትዎ የማይታወቅ ነው።

Type your message below to start.
ለመጀመር መልእክትዎን ከታች ይጻፉ።
To counselor:

✅ Session Started!
✅ ክፍለ ጊዜው ተጀምሯል!

Topic: {topic_data['icon']} {topic_data['name']}
ርዕስ: {topic_data['icon']} {topic_data['name']}

User Gender: {gender_display}
የተጠቃሚ ፆታ: {gender_display}

User's Description: {safe_desc}
የተጠቃሚው መግለጫ: {safe_desc}

The user can now send messages. Wait for their first message.
ተጠቃሚው አሁን መልእክት መላክ ይችላል። የመጀመሪያ መልእክታቸውን ይጠብቁ።
Session Ending Confirmation
**Are you sure you want to end this session?**
**እርግጠኛ ነዎት ይህንን ክፍለ ጊዜ መጨረስ ይፈልጋሉ?**

The conversation will be closed for both parties.
ውይይቱ ለሁለቱም ወገኖች ይዘጋል።
Buttons:

"✅ Yes, End/Cancel"

"✅ አዎ፣ ጨርስ/ሰርዝ"

"❌ No, Continue"

"❌ አይ፣ ቀጥል"

Session Ended Messages
To user (when cancelling before match):

✅ **Request Cancelled**
✅ **ጥያቄው ተሰርዟል**

Your counseling request has been cancelled.
የምክር አገልግሎት ጥያቄዎ ተሰርዟል።

Feel free to request counseling again anytime you need support. 🙏
ድጋፍ በሚፈልጉበት በማንኛውም ጊዜ የምክር አገልግሎት መጠየቅ ይችላሉ። 🙏
To user (when ending active session):

**Session Ended**
**ክፍለ ጊዜው ተጠናቅቋል**

Thank you for using HU Counseling Service.
የ HU የምክር አገልግሎትን ስለተጠቀሙ እናመሰግናለን።

**Would you like to rate this session?**
**ለዚህ ክፍለ ጊዜ ደረጃ መስጠት ይፈልጋሉ?**
Rating buttons:

"⭐ Rate Session"

"⭐ ደረጃ ይስጡ"

"⏭️ Skip"

"⏭️ ለማለፍ"

To counselor:

**Session Ended**
**ክፍለ ጊዜው ተጠናቅቋል**

The user has ended the session. Great work! 🙏
ተጠቃሚው ክፍለ ጊዜውን አጠናቅቋል። ጥሩ ስራ! 🙏
Counselor Registration
Specialization Selection
**Become a Counselor** 👨‍⚕️
**አማካሪ ይሁኑ** 👨‍⚕️

First, select your counseling specializations.
በመጀመሪያ፣ የምክር አገልግሎት የሚሰጡበትን የትኩረት መስክ ይምረጡ።

💡 *Choose all topics you're comfortable counseling on. You can update these later.*
💡 *ምክር ለመስጠት ምቹ የሆኑበትን ሁሉንም ርዕሶች ይምረጡ። ይህንን በኋላ ማዘመን ይችላሉ።*
Buttons:

"✅ Done Selecting"

"✅ መርጠው ጨርሰዋል"

"◀️ Back"

"◀️ ተመለስ"

Gender Selection for Counselors
**Select Your Gender** 👤
**ፆታዎን ይምረጡ** 👤

Choose an option:
አማራጭ ይምረጡ፡
Bio Entry
**Great! Your expertise:** 👍
**በጣም ጥሩ! የእርስዎ የሙያ ዘርፎች:** 👍

{topics_text}

Now, please share a brief bio (2-3 sentences) about yourself that will be shown to users when you're matched with them.
አሁን፣ ከተጠቃሚዎች ጋር ሲገናኙ የሚታይ ስለ እርስዎ የሚገልጽ አጭር መግለጫ (ከ 2-3 ዓረፍተ ነገር) ያጋሩ።

💡 *Include your year, faculty/department, and anything else you'd like users to know about you as a counselor.*
💡 *የእርስዎን የትምህርት ዓመት፣ ፋኩልቲ/ዲፓርትመንት፣ እና ተጠቃሚዎች እንደ አማካሪ ስለ እርስዎ እንዲያውቁ የሚፈልጉትን ማንኛውንም ነገር ያካትቱ።*

📝 *Type your bio below:*
📝 *መግለጫዎን (Bio) ከታች ይጻፉ:*
Application Submission
Thank you for applying to be a counselor. Your application has been sent to the admin team for review.
አማካሪ ለመሆን ስላመለከቱ እናመሰግናለን። ማመልከቻዎ ለግምገማ ወደ አስተዳዳሪዎች ተልኳል።

We'll notify you once your application is approved. This usually takes a short time.
ማመልከቻዎ እንደፀደቀ እናሳውቅዎታለን። ይህ ብዙውን ጊዜ አጭር ጊዜ ይወስዳል።

**What happens next:**
**ቀጥሎ ምን ይሆናል:**
1. Admins review your application
1. አስተዳዳሪዎች ማመልከቻዎን ይገመግማሉ
2. You may be contacted for a brief interview
2. ለአጭር ቃለ መጠይቅ ሊጠሩ ይችላሉ
3. Once approved, you'll receive access to the Counselor Dashboard
3. አንዴ ከፀደቀ፣ የአማካሪ ዳሽቦርድን መጠቀም ይችላሉ

Thank you for your willingness to serve! 🙏
ለማገልገል ፈቃደኛ ስለሆኑ እናመሰግናለን! 🙏
Notification to admins:

🔔 **New Counselor Application**
🔔 **አዲስ የአማካሪ ማመልከቻ**

**Applicant:** {display_name}
**አመልካች:** {display_name}

**User ID:** `{user_id}`
**የተጠቃሚ መታወቂያ:** `{user_id}`

**Specializations:** {topics_list}
**የትኩረት መስኮች:** {topics_list}

**Bio:**
**መግለጫ (Bio):**
{bio}

📋 Go to Admin Panel → Pending Applications to review.
📋 ለመገምገም ወደ አስተዳዳሪ ፓነል → በመጠባበቅ ላይ ያሉ ማመልከቻዎች ይሂዱ።
Counselor Dashboard
**Counselor Dashboard** 👨‍⚕️
**የአማካሪ ዳሽቦርድ** 👨‍⚕️

**Status:** {status_text}
**ሁኔታ:** {status_text}

**Total Sessions:** {stats.get('total_sessions', 0)}
**ጠቅላላ ክፍለ ጊዜዎች:** {stats.get('total_sessions', 0)}

Choose an option:
አማራጭ ይምረጡ፡
Status indicators:

"🟢 Online"

"🟢 በመስመር ላይ"

"🔴 Offline"

"🔴 ከመስመር ውጭ"

Buttons:

"🟢 Go Online" / "🔴 Go Offline"

"🟢 ወደ መስመር ይግቡ" / "🔴 ከ መስመር ይውጡ"

"📊 My Statistics"

"📊 የእኔ ስታቲስቲክስ"

"📱 Go to Current Session View"

"📱 ወደ አሁኑ ክፍለ ጊዜ እይታ ይሂዱ"

"◀️ Back to Menu"

"◀️ ወደ ዋናው ዝርዝር ይመለሱ"

Admin Panel
Main Admin Panel
**Admin Panel** 🛡️
**የአስተዳዳሪ ፓነል** 🛡️

**System Statistics:**
**የሲስተም ስታቲስቲክስ:**
👥 Total Users: {stats.get('total_users', 0)}
👥 ጠቅላላ ተጠቃሚዎች: {stats.get('total_users', 0)}
👨‍⚕️ Total Counselors: {stats.get('total_counselors', 0)}
👨‍⚕️ ጠቅላላ አማካሪዎች: {stats.get('total_counselors', 0)}
🟢 Active Counselors: {stats.get('active_counselors', 0)}
🟢 ንቁ አማካሪዎች: {stats.get('active_counselors', 0)}

**Sessions:**
**ክፍለ ጊዜዎች:**
📊 Total: {stats.get('total_sessions', 0)}
📊 ጠቅላላ: {stats.get('total_sessions', 0)}
🔄 Active: {stats.get('active_sessions', 0)}
🔄 በሂደት ላይ ያሉ: {stats.get('active_sessions', 0)}
✅ Completed: {stats.get('completed_sessions', 0)}
✅ የተጠናቀቁ: {stats.get('completed_sessions', 0)}

**Choose an action:**
**ተግባር ይምረጡ:**
Buttons:

"📋 Pending Applications"

"📋 በመጠባበቅ ላይ ያሉ ማመልከቻዎች"

"📊 Detailed Statistics"

"📊 ዝርዝር ስታቲስቲክስ"

"👥 Manage Counselors"

"👥 አማካሪዎችን ማስተዳደሪያ"

"🔔 Pending Sessions"

"🔔 በመጠባበቅ ላይ ያሉ ክፍለ ጊዜዎች"

"◀️ Back"

"◀️ ተመለስ"

Pending Applications
**Pending Counselor Applications** ({len(pending)})
**በመጠባበቅ ላይ ያሉ የአማካሪ ማመልከቻዎች** ({len(pending)})

{application_details}
Buttons:

"Review #{app['counselor_id']}"

"ይገምግሙ #{app['counselor_id']}"

"◀️ Back"

"◀️ ተመለስ"

Detailed Statistics
**System Statistics** 📊
**የሲስተም ስታቲስቲክስ** 📊

**👥 Users & Counselors:**
**👥 ተጠቃሚዎች እና አማካሪዎች:**
• Total Users: **{total_users}**
• ጠቅላላ ተጠቃሚዎች: **{total_users}**
• Total Counselors: **{total_counselors}**
• ጠቅላላ አማካሪዎች: **{total_counselors}**
  ├─ ✅ Approved: {approved_counselors}
  ├─ ✅ የፀደቁ: {approved_counselors}
  ├─ 🟢 Currently Online: {online_counselors}
  ├─ 🟢 በአሁን ሰዓት መስመር ላይ ያሉ: {online_counselors}
  ├─ ⏳ Pending: {pending_counselors}
  ├─ ⏳ በመጠባበቅ ላይ ያሉ: {pending_counselors}
  ├─ ❌ Rejected: {rejected_counselors}
  ├─ ❌ ውድቅ የተደረጉ: {rejected_counselors}
  ├─ 🔴 Deactivated: {deactivated_counselors}
  ├─ 🔴 የታገዱ (Deactivated): {deactivated_counselors}
  └─ 🚫 Banned: {banned_counselors}
  └─ 🚫 ሙሉ በሙሉ የታገዱ (Banned): {banned_counselors}

**📊 Sessions Overview:**
**📊 የክፍለ ጊዜዎች አጠቃላይ እይታ:**
• Total Sessions: **{total_sessions}**
• ጠቅላላ ክፍለ ጊዜዎች: **{total_sessions}**
  ├─ 🔄 Active Now: {active_sessions}
  ├─ 🔄 አሁን በሂደት ላይ ያሉ: {active_sessions}
  ├─ ✅ Completed: {completed_sessions}
  ├─ ✅ የተጠናቀቁ: {completed_sessions}
  ├─ ⏳ Pending (waiting): {pending_sessions}
  ├─ ⏳ በመጠባበቅ ላይ ያሉ (የሚጠብቁ): {pending_sessions}
  └─ 🎯 Matched (not started): {matched_sessions}
  └─ 🎯 የተገናኙ (ያልተጀመሩ): {matched_sessions}
• Completion Rate: **{completion_rate:.1f}%**
• የማጠናቀቂያ መጠን: **{completion_rate:.1f}%**

**💬 Messages:**
**💬 መልእክቶች:**
• Total Messages Exchanged: **{total_messages}**
• ጠቅላላ የተለዋወጡት መልእክቶች: **{total_messages}**

**⭐ Quality Metrics:**
**⭐ የጥራት መለኪያ:**
• Average Rating: **{avg_rating:.2f}/5.0**
• አማካይ ደረጃ: **{avg_rating:.2f}/5.0**
• Total Ratings Received: **{total_ratings}**
• ጠቅላላ የተሰጡ ደረጃዎች: **{total_ratings}**

**🔥 Top 5 Topics:**
**🔥 ምርጥ 5 ርዕሶች:**
{topics_text if topics_text else '• No sessions yet'}
{topics_text if topics_text else '• እስካሁን ምንም ክፍለ ጊዜ የለም'}

**🏥 System Health:** ✅ Operational
**🏥 የሲስተም ጤና:** ✅ በመስራት ላይ
Buttons:

"🔄 Refresh"

"🔄 አድስ (Refresh)"

"◀️ Back to Admin Panel"

"◀️ ወደ አስተዳዳሪ ፓነል ይመለሱ"

Counselor Management
**Counselor Management** 👥
**አማካሪዎችን ማስተዳደሪያ** 👥

Click on a counselor to manage:
ለማስተዳደር አማካሪውን ይጫኑ:

{counselor_list}
Buttons:

"📋 View Pending Applications"

"📋 በመጠባበቅ ላይ ያሉ ማመልከቻዎችን ይመልከቱ"

"🔄 Refresh List"

"🔄 ዝርዝሩን አድስ"

"◀️ Back"

"◀️ ተመለስ"

Pending Sessions
**Pending Sessions** 🔔
**በመጠባበቅ ላይ ያሉ ክፍለ ጊዜዎች** 🔔

There are **{len(pending)}** sessions waiting for counselors:
ለአማካሪዎች የሚጠብቁ **{len(pending)}** ክፍለ ጊዜዎች አሉ:

{session_details}

💡 **Note:** These sessions are waiting for available counselors to come online.
💡 **ማስታወሻ:** እነዚህ ክፍለ ጊዜዎች የሚገኙ አማካሪዎች መስመር ላይ እስኪገቡ ድረስ እየጠበቁ ነው።
Buttons:

"🔄 Refresh"

"🔄 አድስ"

"◀️ Back"

"◀️ ተመለስ"

Help and About Sections
Help Text
**How to use HU Counseling Service:**
**የ HU የምክር አገልግሎትን እንዴት መጠቀም እንደሚቻል:**

**For Users Seeking Help:**
**እርዳታ ለሚፈልጉ ተጠቃሚዎች:**
1️⃣ Click "Request Counseling"
1️⃣ "የምክር አገልግሎት ይጠይቁ" የሚለውን ይጫኑ
2️⃣ Select a topic that fits your situation
2️⃣ ለሁኔታዎ የሚስማማውን ርዕስ ይምረጡ
3️⃣ Describe your situation (optional)
3️⃣ ሁኔታዎን ይግለጹ (አማራጭ)
4️⃣ Wait to be matched with a counselor
4️⃣ ከአማካሪ ጋር እስኪገናኙ ይጠብቁ
5️⃣ Start your anonymous chat session
5️⃣ ማንነቱ ያልታወቀ የውይይት ጊዜዎን ይጀምሩ

**During a Session:**
**በምክክር ወቅት:**
• All messages are private and anonymous
• ሁሉም መልእክቶች የግል እና ማንነታቸው የማይታወቅ ነው
• You can end the session anytime
• በማንኛውም ጊዜ ክፍለ ጊዜውን ማቋረጥ ይችላሉ።
• Both parties remain anonymous
• የሁለቱም ወገኖች ማንነት አይታወቅም

**For Counselors:**
**ለአማካሪዎች:**
• Click "Counselor Dashboard" to manage sessions
• ክፍለ ጊዜዎችን ለማስተዳደር "የአማካሪ ዳሽቦርድ" የሚለውን ይጫኑ
• Toggle your availability
• መኖርዎን (Availability) ያስተካክሉ
• Accept or decline session requests
• የክፍለ ጊዜ ጥያቄዎችን ይቀበሉ ወይም አይቀበሉ

**Important:**
**አስፈላጊ:**
🆘 If you're in crisis or having suicidal thoughts, please select "Crisis & Substance Support" to be prioritized for support.
🆘 አጣዳፊ ሁኔታ ላይ ከሆኑ ወይም እራስን የማጥፋት ሀሳብ ካሎት፣ ለድጋፍ ቅድሚያ እንዲሰጠዎት እባክዎ "አጣዳፊ እና የሱሰኝነት ድጋፍ" የሚለውን ይምረጡ።

If you are in immediate danger, please seek help offline as well:
በአስቸኳይ አደጋ ውስጥ ከሆኑ፣ እባክዎ በአካልም እርዳታ ይጠይቁ፡
• Go to the nearest clinic, hospital, or health centre
• በአቅራቢያዎ ወደሚገኝ ክሊኒክ፣ ሆስፒታል ወይም ጤና ጣቢያ ይሂዱ
• Reach out to a trusted person (friend, family, fellowship leader, or university staff)
• ለሚያምኑት ሰው (ጓደኛ፣ ቤተሰብ፣ የፌሎውሺፕ መሪ፣ ወይም የዩኒቨርሲቲ ሰራተኛ) ያናግሩ
• Contact local emergency services or campus security in your area
• የአካባቢውን የድንገተኛ አደጋ አገልግሎቶች ወይም የግቢውን ጥበቃ ያግኙ

**Contact Admin:**
**አስተዳዳሪን ያግኙ:**
If you have issues, contact the administrators.
ችግር ካጋጠመዎት አስተዳዳሪዎችን ያግኙ።
Buttons:

"◀️ Back"

"◀️ ተመለስ"

About Text
**About HU Counseling Service** 🙏
**ስለ HU የምክር አገልግሎት** 🙏

A safe, confidential space where students can receive biblical guidance and support from trained peer counselors. All conversations are completely anonymous.
ተማሪዎች ከሰለጠኑ እኩዮች አማካሪዎች መጽሐፍ ቅዱሳዊ ምክር እና ድጋፍ የሚያገኙበት ደህንነቱ የተጠበቀ፣ ምስጢራዊ ቦታ። ሁሉም ውይይቶች ሙሉ በሙሉ ማንነታቸው የማይታወቅ ነው።

**Our Mission:**
**ተልዕኳችን:**
To provide a supportive community where students can seek guidance and find encouragement through faith-centered counseling.
ተማሪዎች መመሪያን የሚሹበት እና በእምነት ላይ የተመሰረተ ምክር አማካኝነት ማበረታቻ የሚያገኙበት ደጋፊ ማህበረሰብ መፍጠር።

**How It Works:**
**እንዴት እንደሚሰራ:**
1. **Request Help** - Select a topic and describe your situation
1. **እርዳታ ይጠይቁ** - ርዕስ ይምረጡ እና ሁኔታዎን ይግለጹ
2. **Get Matched** - We connect you with a trained peer counselor
2. **ይገናኙ** - ከሰለጠነ እኩያ አማካሪ ጋር እናገናኝዎታለን
3. **Chat Anonymously** - Have a private conversation in a safe space
3. **በምስጢር ይወያዩ** - ደህንነቱ በተጠበቀ ቦታ የግል ውይይት ያድርጉ
4. **Get Support** - Receive guidance and encouragement
4. **ድጋፍ ያግኙ** - መመሪያ እና ማበረታቻ ይቀበሉ

**Confidentiality:**
**ምስጢራዊነት:**
🔒 All conversations are completely anonymous
🔒 ሁሉም ውይይቶች ሙሉ በሙሉ ማንነታቸው የማይታወቅ ነው
🔒 No personal information is shared between users
🔒 በተጠቃሚዎች መካከል ምንም አይነት የግል መረጃ አይጋራም።
🔒 Counselors never see your identity
🔒 አማካሪዎች ማንነትዎን በጭራሽ አያዩም።
🔒 Your privacy is our top priority
🔒 የእርስዎ ግላዊነት ቅድሚያ የምንሰጠው ጉዳይ ነው።

**Counselor Training:**
**የአማካሪ ስልጠና:**
All counselors are trained students who have completed our counseling program and are supervised by experienced mentors.
ሁሉም አማካሪዎች የምክር አገልግሎት ፕሮግራማችንን ያጠናቀቁ እና ልምድ ባላቸው አማካሪዎች የሚታገዙ የሰለጠኑ ተማሪዎች ናቸው።

**Need Immediate Help?**
**አስቸኳይ እርዳታ ይፈልጋሉ?**
If you're in crisis or having thoughts of self-harm:
አጣዳፊ ሁኔታ ውስጥ ከሆኑ ወይም እራስን የመጉዳት ሀሳብ ካሎት፡
1. Select "Crisis & Substance Support" when requesting counseling
1. ምክር ሲጠይቁ "አጣዳፊ እና የሱሰኝነት ድጋፍ" የሚለውን ይምረጡ
2. Reach out to a trusted person nearby
2. በአቅራቢያዎ ለሚገኝ ለሚያምኑት ሰው ያናግሩ
3. Contact local emergency services
3. የአካባቢ ድንገተኛ አደጋ አገልግሎቶችን ያግኙ

**Contact:**
**ግንኙነት:**
For technical issues or questions, please contact the administrators.
ለቴክኒካዊ ጉዳዮች ወይም ጥያቄዎች እባክዎ አስተዳዳሪዎችን ያግኙ።
Error Messages
"⚠️ Session error: Topic not found. Please start over with /start"

"⚠️ የክፍለ ጊዜ ስህተት፡ ርዕሱ አልተገኘም። እባክዎ በ /start እንደገና ይጀምሩ"

"⚠️ This session is no longer available."

"⚠️ ይህ ክፍለ ጊዜ ከአሁን በኋላ አይገኝም።"

"⚠️ You don't have an active session."

"⚠️ ምንም ንቁ ክፍለ ጊዜ የለዎትም።"

"⚠️ You don't have admin access."

"⚠️ የአስተዳዳሪ ፈቃድ የለዎትም።"

"⚠️ Session has already ended."

"⚠️ ክፍለ ጊዜው ቀድሞውኑ ተጠናቅቋል።"

"⚠️ You don't have an active session."

"⚠️ ምንም ንቁ ክፍለ ጊዜ የለዎትም።"

Crisis Resources
Default crisis text:

⚠️ **If you are in immediate danger or feel you might harm yourself or someone else, please seek help around you immediately (nearby people, university clinic, health centre, hospital, or campus security).**
⚠️ **አጣዳፊ አደጋ ላይ ከሆኑ ወይም እራስዎን ወይም ሌላ ሰው ሊጎዱ እንደሚችሉ ከተሰማዎት፣ እባክዎ በአካባቢዎ ካሉ አካላት በአስቸኳይ እርዳታ ይጠይቁ (በአቅራቢያ ካሉ ሰዎች፣ የዩኒቨርሲቲ ክሊኒክ፣ ጤና ጣቢያ፣ ሆስፒታል ወይም የግቢው ጥበቃ)።**

**Emergency:** Local emergency services / campus security
**ድንገተኛ አደጋ:** የአካባቢ ድንገተኛ አደጋ አገልግሎቶች / የግቢው ጥበቃ

**Crisis Resources:**
**የአጣዳፊ ጊዜ ግብዓቶች:**
• **Local crisis support:** Contact your university clinic, counseling office, or local health centre
• **የአካባቢ ድጋፍ:** የዩኒቨርሲቲዎን ክሊኒክ፣ የምክር አገልግሎት ቢሮ፣ ወይም የአካባቢ ጤና ጣቢያ ያግኙ
• **Trusted people around you:** Reach out to a close friend, family member, fellowship leader, or university staff
• **በአካባቢዎ ያሉ የሚታመኑ ሰዎች:** ለቅርብ ጓደኛ፣ ለቤተሰብ አባል፣ ለፌሎውሺፕ መሪ፣ ወይም ለዩኒቨርሲቲ ሰራተኛ ያናግሩ
Session Timeout Messages
To user:

⏰ **Session Timeout**
⏰ **የክፍለ ጊዜ ማብቂያ**

Your counseling session has been automatically ended due to {self.timeout_hours} hours of inactivity.
ለ {self.timeout_hours} ሰዓታት ምንም እንቅስቃሴ ባለመኖሩ የምክር አገልግሎት ክፍለ ጊዜዎ በራስ-ሰር ተጠናቅቋል።

If you still need support, feel free to request a new session anytime. 🙏
አሁንም ድጋፍ የሚፈልጉ ከሆነ፣ በማንኛውም ጊዜ አዲስ ክፍለ ጊዜ መጠየቅ ይችላሉ። 🙏
To counselor:

⏰ **Session Timeout**
⏰ **የክፍለ ጊዜ ማብቂያ**

Your counseling session (ID: #{session_id}) has been automatically ended due to inactivity.
የምክር አገልግሎት ክፍለ ጊዜዎ (መታወቂያ: #{session_id}) እንቅስቃሴ ባለመኖሩ በራስ-ሰር ተጠናቅቋል።

No action needed from you.
ከእርስዎ ምንም እርምጃ አይጠበቅም።
Rating System
Rating submission confirmation:

✅ **Thank you for your feedback!**
✅ **ለአስተያየትዎ እናመሰግናለን!**

You rated this session: {'⭐' * rating}
ለዚህ ክፍለ ጊዜ የሰጡት ደረጃ: {'⭐' * rating}

Your feedback helps us improve our counseling service. 🙏
የእርስዎ አስተያየት የምክር አገልግሎታችንን ለማሻሻል ይረዳናል። 🙏
Topic Names and Descriptions
Academic & Career:    - Name: "Academic & Career"

Name: "ትምህርት እና ሥራ (ሙያ)"

   - Icon: "📚"

   - Description: "Academic struggles, exams, university life, career choices, work and finances"

Description: "የትምህርት ፈተናዎች፣ የዩኒቨርሲቲ ህይወት፣ የሙያ ምርጫዎች፣ ሥራ እና ፋይናንስ"

Mental Health & Emotional:    - Name: "Mental Health & Emotional"

Name: "የአእምሮ ጤና እና ስሜት"

   - Icon: "🧠"

   - Description: "Anxiety, depression, stress, grief, trauma, emotional struggles"

Description: "ጭንቀት፣ ድብርት፣ ውጥረት፣ ሀዘን፣ እና ስሜታዊ ፈተናዎች"

Relationships & Social Life:    - Name: "Relationships & Social Life"

Name: "ግንኙነት እና ማህበራዊ ህይወት"

   - Icon: "💬"

   - Description: "Friendships, family, dating, social life and community"

Description: "ጓደኝነት፣ ቤተሰብ፣ የፍቅር ግንኙነት፣ ማህበራዊ ህይወት እና ማህበረሰብ"

Life Skills & Personal Growth:    - Name: "Life Skills & Personal Growth"

Name: "የህይወት ክህሎት እና የግል እድገት"

   - Icon: "🌱"

   - Description: "Identity, purpose, habits, faith walk, life decisions and personal growth"

Description: "ማንነት፣ ዓላማ፣ ልምዶች፣ የእምነት ጉዞ፣ የህይወት ውሳኔዎች እና የግል እድገት"

Crisis & Substance Support:    - Name: "Crisis & Substance Support"

Name: "አጣዳፊ እና የሱሰኝነት ድጋፍ"

   - Icon: "🆘"

   - Description: "Immediate crisis, safety concerns, suicidal thoughts, and substance use struggles"

Description: "አጣዳፊ ቀውስ፣ የደህንነት ስጋቶች፣ እራስን የማጥፋት ሀሳቦች እና የሱሰኝነት ፈተናዎች"

Other Counseling:    - Name: "Other Counseling"

Name: "ሌላ የምክር አገልግሎት"

   - Icon: "💬"

   - Description: "If you're not sure where your situation fits, choose this."

Description: "ሁኔታዎ የት እንደሚመደብ እርግጠኛ ካልሆኑ፣ ይህንን ይምረጡ።"

System Messages
Bot startup message:

🚀 HU Counseling Service Bot is starting...
🚀 የ HU የምክር አገልግሎት ቦት በመጀመር ላይ ነው...
Database connection messages:

✅ Database connected successfully
✅ ዳታቤዝ በተሳካ ሁኔታ ተገናኝቷል

❌ Database connection failed: {e}
❌ የዳታቤዝ ግንኙነት አልተሳካም: {e}
Missing configuration messages:

❌ BOT_TOKEN not found in environment variables!
❌ BOT_TOKEN በ environment variables ውስጥ አልተገኘም!

Please create a .env file with BOT_TOKEN=your_bot_token
እባክዎ BOT_TOKEN=your_bot_token የያዘ .env ፋይል ይፍጠሩ

❌ ADMIN_IDS not found or empty in environment variables!
❌ ADMIN_IDS በ environment variables ውስጥ አልተገኘም ወይም ባዶ ነው!

Please set ADMIN_IDS in .env file (e.g., ADMIN_IDS=123456789)
እባክዎ ADMIN_IDSን በ .env ፋይል ውስጥ ያዘጋጁ (ምሳሌ: ADMIN_IDS=123456789)

Without ADMIN_IDS, the admin panel will NOT work!
ADMIN_IDS ከሌለ የአስተዳዳሪ ፓነል አይሰራም!