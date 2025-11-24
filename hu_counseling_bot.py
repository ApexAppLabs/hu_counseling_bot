"""
HU Counseling Service Bot
Anonymous counseling platform for student gospel fellowship
Version: 3.0
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    filters, ContextTypes, CallbackQueryHandler
)
import logging
import os
from dotenv import load_dotenv
from counseling_database import CounselingDatabase, COUNSELING_TOPICS
from matching_system import CounselingMatcher

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS_STR = os.getenv('ADMIN_IDS', '')
ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(',') if id.strip()] if ADMIN_IDS_STR else []

# Initialize database and matcher
db = CounselingDatabase()
matcher = CounselingMatcher(db)

# User states
USER_STATE = {}

# ==================== KEYBOARD HELPERS ====================

def create_main_menu_keyboard(is_counselor: bool = False, is_admin: bool = False):
    """Create main menu keyboard"""
    keyboard = [
        [InlineKeyboardButton("🆘 Request Counseling", callback_data='request_counseling')],
        [InlineKeyboardButton("ℹ️ About Us", callback_data='about'),
         InlineKeyboardButton("❓ Help", callback_data='help')]
    ]
    
    if is_counselor:
        keyboard.insert(1, [InlineKeyboardButton("👨‍⚕️ Counselor Dashboard", callback_data='counselor_dashboard')])
    else:
        keyboard.insert(1, [InlineKeyboardButton("📝 Become a Counselor", callback_data='register_counselor')])
    
    if is_admin:
        keyboard.append([InlineKeyboardButton("🛡️ Admin Panel", callback_data='admin_panel')])
    
    return InlineKeyboardMarkup(keyboard)

def create_topic_keyboard():
    """Create topic selection keyboard"""
    keyboard = []
    
    # Sort topics by priority (crisis first)
    sorted_topics = sorted(
        COUNSELING_TOPICS.items(),
        key=lambda x: (0 if x[1].get('priority') else 1, x[0])
    )
    
    # Add topics in rows of 2
    for i in range(0, len(sorted_topics), 2):
        row = []
        for j in range(i, min(i + 2, len(sorted_topics))):
            topic_key, topic_data = sorted_topics[j]
            icon = topic_data['icon']
            name = topic_data['name']
            row.append(InlineKeyboardButton(f"{icon} {name}", callback_data=f'topic_{topic_key}'))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data='main_menu')])
    return InlineKeyboardMarkup(keyboard)

def create_counselor_specialization_keyboard(selected: list = None):
    """Create specialization selection keyboard for counselors"""
    if selected is None:
        selected = []
    
    keyboard = []
    
    for i in range(0, len(COUNSELING_TOPICS), 2):
        row = []
        topics_list = list(COUNSELING_TOPICS.items())
        for j in range(i, min(i + 2, len(topics_list))):
            topic_key, topic_data = topics_list[j]
            icon = topic_data['icon']
            name = topic_data['name'].split('&')[0].strip()  # Shorten name
            
            # Add checkmark if selected
            display = f"✅ {icon} {name}" if topic_key in selected else f"{icon} {name}"
            row.append(InlineKeyboardButton(display, callback_data=f'spec_{topic_key}'))
        keyboard.append(row)
    
    if selected:
        keyboard.append([InlineKeyboardButton(f"✔️ Done ({len(selected)} selected)", callback_data='spec_done')])
    
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data='main_menu')])
    return InlineKeyboardMarkup(keyboard)

def create_session_control_keyboard(is_user: bool = True):
    """Create session control keyboard"""
    keyboard = [
        [InlineKeyboardButton("❌ End Session", callback_data='end_session')],
        [InlineKeyboardButton("📋 Session Info", callback_data='session_info')]
    ]
    
    if not is_user:
        # Counselor has additional options
        keyboard.insert(1, [InlineKeyboardButton("🔄 Transfer Session", callback_data='transfer_session')])
    
    return InlineKeyboardMarkup(keyboard)

# ==================== START & BASIC COMMANDS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    if not user:
        return
    
    # Add user to database
    db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Check if user is banned
    if db.is_user_banned(user.id):
        await update.message.reply_text("⚠️ You have been banned from using this service.")
        return
    
    # Check if user is counselor
    counselor = db.get_counselor_by_user_id(user.id)
    is_counselor = counselor and counselor['status'] == 'approved'
    
    # Check if user is admin
    is_admin = db.is_admin(user.id) or user.id in ADMIN_IDS
    
    # Clear any previous state
    USER_STATE[user.id] = {}
    
    welcome_text = f"""
**Welcome to HU Counseling Service! 🙏**

A safe, anonymous space for students in the gospel fellowship to receive guidance and support.

**What we offer:**
• 🤝 Anonymous 1-on-1 counseling sessions
• 🔒 Complete privacy and confidentiality
• 👥 Trained peer counselors from our fellowship
• 💬 Real-time chat support

**All conversations are private and anonymous.**
Neither party will see personal information about the other.

Choose an option below to get started:
"""
    
    keyboard = create_main_menu_keyboard(is_counselor, is_admin)
    await update.message.reply_text(welcome_text, reply_markup=keyboard, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command and help button"""
    help_text = """
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
🆘 If you're in crisis or having suicidal thoughts, please select "Crisis & Emergency" to be prioritized for support.
If you are in immediate danger, please seek help offline as well:
• Go to the nearest clinic, hospital, or health centre
• Reach out to a trusted person (friend, family, fellowship leader, or university staff)
• Contact local emergency services or campus security in your area

**Contact Admin:**
If you have issues, contact the administrators.
"""
    
    keyboard = [[InlineKeyboardButton("◀️ Back", callback_data='main_menu')]]
    
    # Check if called from callback query (button) or message (command)
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(help_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        await update.message.reply_text(help_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command and about button"""
    about_text = """
**About HU Counseling Service** 🙏

We are a student-led counseling initiative within the gospel fellowship, dedicated to providing confidential support to fellow students.

**Our Mission:**
To create a safe, anonymous space where students can:
• Share their struggles without judgment
• Receive biblical guidance and support
• Connect with caring peers who understand
• Find hope and healing through faith

**Our Values:**
✝️ **Faith-Centered** - Grounded in Christian principles
🤝 **Confidential** - Your privacy is sacred
💝 **Compassionate** - Led by love and empathy
👥 **Peer-to-Peer** - Students helping students

**How We Work:**
All counselors are fellow students who have been trained and approved by our leadership team. Sessions are completely anonymous—neither party sees personal information about the other.

**Our Topics:**
We cover spiritual growth, mental health, relationships, academics, identity, addiction, grief, and more. Whatever you're going through, we're here to listen.

*"Carry each other's burdens, and in this way you will fulfill the law of Christ." - Galatians 6:2*
"""
    
    keyboard = [[InlineKeyboardButton("◀️ Back", callback_data='main_menu')]]
    
    # Check if called from callback query (button) or message (command)
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(about_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        await update.message.reply_text(about_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# ==================== COUNSELING REQUEST FLOW ====================

async def request_counseling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start counseling request flow"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Check if user already has a pending or active session
    active_session = db.get_active_session_by_user(user_id)
    if active_session:
        await query.edit_message_text(
            "⚠️ You already have a pending or active counseling request.\n\n"
            "Please complete or end your current session before requesting a new one.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📱 Go to Current Session", callback_data='current_session')
            ]])
        )
        return
    
    text = """
**Request Counseling** 🆘

Please select the topic that best describes what you'd like to talk about:

💡 *Choose the category that fits best. Your counselor will be matched based on their expertise.*

🔒 *Remember: Everything is completely anonymous and confidential.*
"""
    
    keyboard = create_topic_keyboard()
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')

async def topic_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle topic selection"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    topic = query.data.replace('topic_', '')
    
    # Store topic in user state
    USER_STATE[user_id] = {'topic': topic}
    
    topic_data = COUNSELING_TOPICS.get(topic, {})
    topic_name = topic_data.get('name', topic)
    topic_icon = topic_data.get('icon', '💬')
    
    # Show gender selection first
    await user_gender_selection(query, context, topic, topic_name, topic_icon)

async def user_gender_selection(query, context, topic, topic_name, topic_icon):
    """Ask user to select their gender"""
    user_id = query.from_user.id
    
    text = f"""
**Topic Selected:** {topic_icon} **{topic_name}**

**Select Your Gender** 👤

This helps us match you with an appropriate counselor and ensures they can provide relevant guidance.

**Your privacy:**
• Your gender is only shared with your matched counselor
• Choose "Anonymous" if you prefer not to specify
• All conversations remain confidential

Choose an option:
"""
    
    keyboard = [
        [InlineKeyboardButton("👨 Male", callback_data=f'user_gender_male')],
        [InlineKeyboardButton("👩 Female", callback_data=f'user_gender_female')],
        [InlineKeyboardButton("🔒 Prefer not to say (Anonymous)", callback_data=f'user_gender_anonymous')],
        [InlineKeyboardButton("◀️ Back", callback_data='request_counseling')]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def user_gender_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user gender selection"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    gender = query.data.replace('user_gender_', '')
    
    # Save gender to database
    db.update_user_gender(user_id, gender)
    
    # Store in state
    if user_id not in USER_STATE:
        USER_STATE[user_id] = {}
    USER_STATE[user_id]['gender'] = gender
    
    # Get topic from state - it should have been set in topic_selected
    topic = USER_STATE[user_id].get('topic')
    if not topic:
        await query.edit_message_text("⚠️ Session error: Topic not found. Please start over with /start")
        return
    topic_data = COUNSELING_TOPICS.get(topic, {})
    topic_name = topic_data.get('name', topic)
    topic_icon = topic_data.get('icon', '💬')
    
    # For crisis, create session immediately
    if topic == 'crisis':
        text = f"""
**🆘 CRISIS SUPPORT REQUESTED**

You've selected: {topic_icon} **{topic_name}**

⚠️ **If you are in immediate danger or feel you might harm yourself or someone else, please seek help around you immediately.**

You can:
• Go to the nearest clinic, hospital, or health centre
• Reach out to a trusted person (friend, family, fellowship leader, or university staff)
• Contact local emergency services or campus security in your area

We're connecting you with a counselor right now. If you'd like, you can briefly describe your situation while we find someone:

*Type your message or click "Skip" to connect immediately.*
"""
        
        keyboard = [[
            InlineKeyboardButton("⏭️ Skip - Connect Now", callback_data='skip_description')
        ]]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        USER_STATE[user_id]['awaiting_description'] = True
        return
    
    # For other topics, ask for optional description
    text = f"""
**Topic Selected:** {topic_icon} **{topic_name}**

{topic_data.get('description', '')}

Would you like to briefly describe your situation? This helps us match you with the right counselor.

*Type your message or click "Skip" to proceed.*
"""
    
    keyboard = [[
        InlineKeyboardButton("⏭️ Skip", callback_data='skip_description'),
        InlineKeyboardButton("❌ Cancel", callback_data='main_menu')
    ]]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    USER_STATE[user_id]['awaiting_description'] = True

async def handle_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user's description message"""
    user_id = update.effective_user.id
    
    if user_id not in USER_STATE or not USER_STATE[user_id].get('awaiting_description'):
        return
    
    description = update.message.text
    USER_STATE[user_id]['description'] = description
    USER_STATE[user_id]['awaiting_description'] = False
    
    # Create the session
    await create_counseling_session(update, context, user_id)

async def skip_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Skip description and create session"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    USER_STATE[user_id]['awaiting_description'] = False
    
    await create_counseling_session_from_callback(query, context, user_id)

async def create_counseling_session(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Create a counseling session request"""
    state = USER_STATE.get(user_id, {})
    topic = state.get('topic')
    description = state.get('description')
    
    if not topic:
        await update.message.reply_text("⚠️ Please start over by requesting counseling.")
        return
    
    # Create session in database
    session_id = db.create_session_request(user_id, topic, description)
    
    # Try to match with a counselor
    counselor_id = matcher.find_best_match(session_id)
    
    if counselor_id:
        db.match_session_with_counselor(session_id, counselor_id)
        
        # Notify counselor
        counselor = db.get_counselor(counselor_id)
        counselor_user_id = counselor['user_id']
        
        topic_data = COUNSELING_TOPICS.get(topic, {})
        
        # Notify user
        await update.message.reply_text(
            f"✅ **Match Found!**\n\n"
            f"We've matched you with a counselor specialized in **{topic_data.get('name', topic)}**.\n\n"
            f"Waiting for the counselor to accept...\n\n"
            f"🔒 Remember: Everything is anonymous and confidential.",
            parse_mode='Markdown'
        )
        
        # Notify counselor
        desc_preview = description[:100] + "..." if description and len(description) > 100 else (description or "No description provided")
        
        # Get user's gender
        user_data = db.get_user(user_id)
        user_gender = user_data.get('gender', 'anonymous') if user_data else 'anonymous'
        gender_display = {
            'male': '👨 Male',
            'female': '👩 Female',
            'anonymous': '🔒 Anonymous'
        }.get(user_gender, '🔒 Anonymous')
        
        keyboard = [[
            InlineKeyboardButton("✅ Accept Session", callback_data=f'accept_session_{session_id}'),
            InlineKeyboardButton("❌ Decline", callback_data=f'decline_session_{session_id}')
        ]]
        
        await context.bot.send_message(
            chat_id=counselor_user_id,
            text=f"**🔔 New Counseling Request**\n\n"
                 f"**Topic:** {topic_data['icon']} {topic_data['name']}\n"
                 f"**User Gender:** {gender_display}\n"
                 f"**Description:** {desc_preview}\n\n"
                 f"Would you like to accept this session?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        # No counselor available
        await update.message.reply_text(
            "⏳ **Request Submitted**\n\n"
            "There are currently no available counselors for your topic.\n\n"
            "You've been added to the queue. We'll notify you as soon as a counselor becomes available.\n\n"
            "📱 You can check your request status anytime from the main menu.",
            parse_mode='Markdown',
            reply_markup=create_main_menu_keyboard()
        )
    
    # Clear state
    USER_STATE[user_id] = {}

async def create_counseling_session_from_callback(query, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Create session from callback (for skip button)"""
    state = USER_STATE.get(user_id, {})
    topic = state.get('topic')
    description = state.get('description')

    # Validate topic before creating session
    if not topic:
        await query.edit_message_text("⚠️ Please start over by requesting counseling.")
        USER_STATE[user_id] = {}
        return

    # Create session in database
    session_id = db.create_session_request(user_id, topic, description)
    
    # Try to match with a counselor
    counselor_id = matcher.find_best_match(session_id)
    
    if counselor_id:
        db.match_session_with_counselor(session_id, counselor_id)
        
        counselor = db.get_counselor(counselor_id)
        counselor_user_id = counselor['user_id']
        
        topic_data = COUNSELING_TOPICS.get(topic, {})
        
        await query.edit_message_text(
            f"✅ **Match Found!**\n\n"
            f"We've matched you with a counselor specialized in **{topic_data.get('name', topic)}**.\n\n"
            f"Waiting for the counselor to accept...",
            parse_mode='Markdown'
        )
        
        # Notify counselor
        desc_preview = description[:100] + "..." if description and len(description) > 100 else (description or "No description provided")
        
        # Get user's gender
        user_data = db.get_user(user_id)
        user_gender = user_data.get('gender', 'anonymous') if user_data else 'anonymous'
        gender_display = {
            'male': '👨 Male',
            'female': '👩 Female',
            'anonymous': '🔒 Anonymous'
        }.get(user_gender, '🔒 Anonymous')
        
        keyboard = [[
            InlineKeyboardButton("✅ Accept Session", callback_data=f'accept_session_{session_id}'),
            InlineKeyboardButton("❌ Decline", callback_data=f'decline_session_{session_id}')
        ]]
        
        await context.bot.send_message(
            chat_id=counselor_user_id,
            text=f"**🔔 New Counseling Request**\n\n"
                 f"**Topic:** {topic_data['icon']} {topic_data['name']}\n"
                 f"**User Gender:** {gender_display}\n"
                 f"**Description:** {desc_preview}\n\n"
                 f"Would you like to accept this session?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text(
            "⏳ **Request Submitted**\n\n"
            "There are currently no available counselors for your topic.\n\n"
            "You've been added to the queue. We'll notify you as soon as a counselor becomes available.",
            parse_mode='Markdown'
        )
    
    USER_STATE[user_id] = {}

# ==================== SESSION MANAGEMENT ====================

async def accept_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Counselor accepts a session"""
    query = update.callback_query
    await query.answer()
    
    session_id = int(query.data.replace('accept_session_', ''))
    counselor_user_id = query.from_user.id
    
    session = db.get_session(session_id)
    if not session or session['status'] != 'matched':
        await query.edit_message_text("⚠️ This session is no longer available.")
        return
    
    # Start the session
    db.start_session(session_id)
    
    # Notify both parties
    user_id = session['user_id']
    topic_data = COUNSELING_TOPICS.get(session['topic'], {})
    
    # Notify user
    await context.bot.send_message(
        chat_id=user_id,
        text=f"✅ **Session Started!**\n\n"
             f"Your counselor has joined. You can now begin your conversation.\n\n"
             f"**Topic:** {topic_data['icon']} {topic_data['name']}\n\n"
             f"🔒 Remember: Everything is anonymous and confidential.\n\n"
             f"*Type your message below to start.*",
        reply_markup=create_session_control_keyboard(is_user=True),
        parse_mode='Markdown'
    )
    
    # Notify counselor
    desc = session.get('description', 'No description provided')
    
    # Get user's gender
    user_data = db.get_user(user_id)
    user_gender = user_data.get('gender', 'anonymous') if user_data else 'anonymous'
    gender_display = {
        'male': '👨 Male',
        'female': '👩 Female',
        'anonymous': '🔒 Anonymous'
    }.get(user_gender, '🔒 Anonymous')
    
    await query.edit_message_text(
        f"✅ **Session Started!**\n\n"
        f"**Topic:** {topic_data['icon']} {topic_data['name']}\n"
        f"**User Gender:** {gender_display}\n"
        f"**User's Description:** {desc}\n\n"
        f"*The user can now send messages. Wait for their first message.*",
        reply_markup=create_session_control_keyboard(is_user=False),
        parse_mode='Markdown'
    )

async def decline_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Counselor declines a session"""
    query = update.callback_query
    await query.answer()
    
    session_id = int(query.data.replace('decline_session_', ''))
    
    session = db.get_session(session_id)
    if not session:
        await query.edit_message_text("⚠️ This session is no longer available.")
        return
    
    # Reset session to requested state and try to find another counselor
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE counseling_sessions SET status = ?, counselor_id = NULL WHERE session_id = ?',
                  ('requested', session_id))
    conn.commit()
    conn.close()
    
    await query.edit_message_text("You've declined this session. Looking for another counselor...")
    
    # Try to find another match
    new_counselor_id = matcher.find_best_match(session_id)
    if new_counselor_id:
        db.match_session_with_counselor(session_id, new_counselor_id)
        # Notify new counselor (similar to above)

async def handle_session_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages during an active session"""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    logger.info(f"📨 Message received from user_id: {user_id}, text: {message_text[:50] if message_text else 'None'}...")
    
    if not message_text:
        logger.warning(f"Empty message from user {user_id}, ignoring")
        return
    
    # IMPORTANT: Check counselor FIRST before user
    # This prevents counselors from matching as users in their own sessions
    logger.info(f"🔍 Checking if user {user_id} is a counselor...")
    counselor = db.get_counselor_by_user_id(user_id)
    
    if counselor and counselor.get('status') == 'approved':
        logger.info(f"✅ User {user_id} IS counselor {counselor['counselor_id']}, status: approved")
        session = db.get_active_session_by_counselor(counselor['counselor_id'])
        
        if session:
            status = session.get('status')
            logger.info(f"✅ Counselor {counselor['counselor_id']} has current session {session['session_id']} (status={status})")

            # Only allow messaging in active sessions
            if status != 'active':
                await update.message.reply_text(
                    "⚠️ This session has not started yet.\n\n"
                    "Please accept the session from the request message before sending messages to the user.",
                    parse_mode='Markdown'
                )
                return

            # Counselor is sending a message in an active session
            session_id = session['session_id']
            client_user_id = session['user_id']
            
            logger.info(f"📤 Preparing to send counselor message to user {client_user_id}")
            
            # Save message
            db.add_message(session_id, 'counselor', user_id, message_text)
            logger.info(f"💾 Message saved to database")
            
            # Forward to user with anonymous display name
            try:
                await context.bot.send_message(
                    chat_id=client_user_id,
                    text=f"Counselor #{counselor['counselor_id']}\n\n{message_text}",
                    parse_mode='Markdown'
                )
                logger.info(f"✅ SUCCESS! Counselor {counselor['counselor_id']} message sent to user {client_user_id}")
            except Exception as e:
                logger.error(f"❌ ERROR sending counselor message: {e}")
                import traceback
                logger.error(traceback.format_exc())
            return
    
    # Now check if user is in an active session (as a regular user, not counselor)
    session = db.get_active_session_by_user(user_id)
    if session:
        status = session.get('status')
        session_id = session['session_id']

        # If session is not yet active (requested or matched), block messaging
        if status != 'active':
            logger.info(f"⏳ User {user_id} tried to send message in non-active session {session_id} (status={status})")
            await update.message.reply_text(
                "⏳ Your counseling request has been sent.\n\n"
                "Please wait until a counselor accepts your request before sending messages.",
                parse_mode='Markdown'
            )
            return

        # User is sending a message in an active session
        logger.info(f"✅ User {user_id} is in active session {session_id}")
        counselor = db.get_counselor(session['counselor_id'])
        counselor_user_id = counselor['user_id']
        
        # Save message
        db.add_message(session_id, 'user', user_id, message_text)
        
        # Forward to counselor with anonymous display name
        try:
            await context.bot.send_message(
                chat_id=counselor_user_id,
                text=f"User #{user_id % 10000}\n\n{message_text}",
                parse_mode='Markdown'
            )
            logger.info(f"✅ User {user_id} sent message to counselor {counselor_user_id}")
        except Exception as e:
            logger.error(f"❌ Error sending user message: {e}")
        return
    
    # No active session found as either user or counselor
    if counselor:
        logger.warning(f"❌ Counselor {counselor['counselor_id']} has NO active session")
    else:
        logger.warning(f"❌ User {user_id} is NOT a counselor and has no active session as user")
    return

async def end_session_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle end session request - works for requested, matched, or active sessions"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Find ANY session (requested, matched, or active)
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Check as user
    cursor.execute('''
        SELECT * FROM counseling_sessions 
        WHERE user_id = ? AND status IN ('requested', 'matched', 'active')
        ORDER BY created_at DESC LIMIT 1
    ''', (user_id,))
    session = cursor.fetchone()
    
    is_counselor = False
    if not session:
        # Check if counselor
        counselor = db.get_counselor_by_user_id(user_id)
        if counselor:
            cursor.execute('''
                SELECT * FROM counseling_sessions 
                WHERE counselor_id = ? AND status IN ('matched', 'active')
                ORDER BY created_at DESC LIMIT 1
            ''', (counselor['counselor_id'],))
            session = cursor.fetchone()
            is_counselor = True
    
    conn.close()
    
    if not session:
        await query.edit_message_text("⚠️ You don't have an active session.")
        return
    
    session = dict(session)
    session_id = session['session_id']
    status = session['status']
    
    # Different messages based on status
    if status == 'requested':
        message = "**Cancel your counseling request?**\n\nYou're still waiting for a counselor. Do you want to cancel?"
    elif status == 'matched':
        message = "**Cancel this session?**\n\nA counselor has been matched but hasn't accepted yet. Cancel the request?"
    else:
        message = "**Are you sure you want to end this session?**\n\nThe conversation will be closed for both parties."
    
    # Confirm end session
    keyboard = [[
        InlineKeyboardButton("✅ Yes, End/Cancel", callback_data=f'confirm_end_{session_id}'),
        InlineKeyboardButton("❌ No, Continue", callback_data='cancel_end')
    ]]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def confirm_end_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and end/cancel the session - handles all statuses"""
    query = update.callback_query
    await query.answer()
    
    session_id = int(query.data.replace('confirm_end_', ''))
    session = db.get_session(session_id)
    
    if not session or session['status'] in ('completed', 'cancelled'):
        await query.edit_message_text("⚠️ This session has already ended.")
        return
    
    status = session['status']
    user_id = session['user_id']
    
    # Handle based on status
    if status == 'requested':
        # Just waiting for matching - simply cancel
        db.end_session(session_id, 'user_cancelled')
        
        await query.edit_message_text(
            "✅ **Request Cancelled**\n\n"
            "Your counseling request has been cancelled.\n\n"
            "Feel free to request counseling again anytime you need support. 🙏",
            reply_markup=create_main_menu_keyboard(is_counselor=False),
            parse_mode='Markdown'
        )
        logger.info(f"User {user_id} cancelled requested session {session_id}")
        
    elif status == 'matched':
        # Counselor matched but hasn't accepted - cancel and notify counselor
        db.end_session(session_id, 'user_cancelled')
        
        counselor = db.get_counselor(session['counselor_id'])
        counselor_user_id = counselor['user_id']
        
        # Notify counselor
        try:
            await context.bot.send_message(
                chat_id=counselor_user_id,
                text="⚠️ **Session Cancelled**\n\n"
                     "The user has cancelled their counseling request before you could accept.\n\n"
                     "No action needed from you.",
                reply_markup=create_main_menu_keyboard(is_counselor=True),
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error notifying counselor of cancellation: {e}")
        
        await query.edit_message_text(
            "✅ **Request Cancelled**\n\n"
            "Your counseling request has been cancelled.\n\n"
            "Feel free to request counseling again anytime. 🙏",
            reply_markup=create_main_menu_keyboard(is_counselor=False),
            parse_mode='Markdown'
        )
        logger.info(f"User {user_id} cancelled matched session {session_id}")
        
    else:  # status == 'active'
        # Active session - end normally with rating
        db.end_session(session_id, 'user_ended')
        
        counselor = db.get_counselor(session['counselor_id'])
        counselor_user_id = counselor['user_id']
        
        # Notify user with rating option
        await context.bot.send_message(
            chat_id=user_id,
            text="**Session Ended**\n\n"
                 "Thank you for using HU Counseling Service.\n\n"
                 "**Would you like to rate this session?**",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⭐ Rate Session", callback_data=f'rate_session_{session_id}'),
                InlineKeyboardButton("⏭️ Skip", callback_data='main_menu')
            ]]),
            parse_mode='Markdown'
        )
        
        # Notify counselor
        await context.bot.send_message(
            chat_id=counselor_user_id,
            text="**Session Ended**\n\n"
                 "The user has ended the session. Great work! 🙏",
            reply_markup=create_main_menu_keyboard(is_counselor=True),
            parse_mode='Markdown'
        )
        
        await query.edit_message_text("✅ Session ended successfully.")
        logger.info(f"User {user_id} ended active session {session_id}")

# ==================== ADDITIONAL SESSION HANDLERS ====================

async def session_info_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current session information"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Find active session
    session = db.get_active_session_by_user(user_id)
    is_counselor = False
    
    if not session:
        # Check if counselor
        counselor = db.get_counselor_by_user_id(user_id)
        if counselor:
            session = db.get_active_session_by_counselor(counselor['counselor_id'])
            is_counselor = True
    
    if not session:
        await query.answer("⚠️ You don't have an active session.", show_alert=True)
        return
    
    topic_data = COUNSELING_TOPICS.get(session['topic'], {})
    started_at = session.get('started_at', 'Unknown')
    
    # Get message count
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM session_messages WHERE session_id = ?', (session['session_id'],))
    message_count = cursor.fetchone()['count']
    conn.close()
    
    text = f"""
**Session Information** 📋

**Topic:** {topic_data['icon']} {topic_data['name']}
**Session ID:** #{session['session_id']}
**Started:** {started_at}
**Messages Exchanged:** {message_count}
**Status:** Active ✅

🔒 **Privacy Reminder:**
Both parties remain completely anonymous. No personal information is shared.

*Type your message below to continue the conversation.*
"""
    
    keyboard = [[InlineKeyboardButton("◀️ Back", callback_data='main_menu')]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def current_session_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Navigate to current active session"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Find active session
    session = db.get_active_session_by_user(user_id)
    is_counselor = False
    
    if not session:
        # Check if counselor
        counselor = db.get_counselor_by_user_id(user_id)
        if counselor:
            session = db.get_active_session_by_counselor(counselor['counselor_id'])
            is_counselor = True
    
    if not session:
        await query.edit_message_text(
            "⚠️ **No Active Session**\n\nYou don't have any active counseling sessions at the moment.",
            reply_markup=create_main_menu_keyboard(is_counselor),
            parse_mode='Markdown'
        )
        return
    
    topic_data = COUNSELING_TOPICS.get(session['topic'], {})
    
    text = f"""
**Your Active Session** 💬

**Topic:** {topic_data['icon']} {topic_data['name']}
**Session ID:** #{session['session_id']}

You are currently in an active counseling session. Type your message below to continue the conversation.

🔒 Remember: Everything is anonymous and confidential.
"""
    
    keyboard = create_session_control_keyboard(is_user=not is_counselor)
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')

async def transfer_session_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Transfer session to another counselor (counselor only)"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Check if user is a counselor
    counselor = db.get_counselor_by_user_id(user_id)
    if not counselor or counselor['status'] != 'approved':
        await query.answer("⚠️ Only counselors can transfer sessions.", show_alert=True)
        return
    
    # Get active session
    session = db.get_active_session_by_counselor(counselor['counselor_id'])
    if not session:
        await query.answer("⚠️ You don't have an active session to transfer.", show_alert=True)
        return
    
    text = """
**Transfer Session** 🔄

⚠️ **Transfer Feature**

This feature allows you to transfer the current session to another available counselor.

**Note:** This is a sensitive action. Only transfer if:
• You're unable to continue the session
• Another counselor is better suited for the topic
• An emergency prevents you from continuing

The user will be notified that a new counselor is joining.

**Are you sure you want to transfer this session?**
"""
    
    keyboard = [
        [InlineKeyboardButton("✅ Yes, Transfer Session", callback_data=f'confirm_transfer_{session["session_id"]}')],
        [InlineKeyboardButton("❌ Cancel", callback_data='counselor_dashboard')]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def confirm_transfer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm session transfer"""
    query = update.callback_query
    await query.answer()
    
    session_id = int(query.data.replace('confirm_transfer_', ''))
    session = db.get_session(session_id)
    
    if not session or session['status'] != 'active':
        await query.answer("⚠️ Session is no longer active.", show_alert=True)
        return
    
    # Reset session to requested and find new match
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE counseling_sessions SET status = ?, counselor_id = NULL WHERE session_id = ?',
                  ('requested', session_id))
    conn.commit()
    conn.close()
    
    # Try to find a new counselor
    new_counselor_id = matcher.find_best_match(session_id)
    
    if new_counselor_id:
        db.match_session_with_counselor(session_id, new_counselor_id)
        
        # Notify user
        await context.bot.send_message(
            chat_id=session['user_id'],
            text="🔄 **Counselor Change**\n\n"
                 "Your session is being transferred to another counselor who may be better suited to help.\n\n"
                 "Waiting for the new counselor to accept...",
            parse_mode='Markdown'
        )
        
        # Notify new counselor (similar to normal matching)
        counselor = db.get_counselor(new_counselor_id)
        topic_data = COUNSELING_TOPICS.get(session['topic'], {})
        
        keyboard = [[
            InlineKeyboardButton("✅ Accept Session", callback_data=f'accept_session_{session_id}'),
            InlineKeyboardButton("❌ Decline", callback_data=f'decline_session_{session_id}')
        ]]
        
        await context.bot.send_message(
            chat_id=counselor['user_id'],
            text=f"**🔔 Transferred Session Request**\n\n"
                 f"**Topic:** {topic_data['icon']} {topic_data['name']}\n"
                 f"**Description:** {session.get('description', 'No description')}\n\n"
                 f"*This session was transferred from another counselor.*\n\n"
                 f"Would you like to accept this session?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
        await query.edit_message_text(
            "✅ **Session Transferred**\n\n"
            "The session has been transferred to another counselor. Thank you for your service! 🙏",
            reply_markup=create_main_menu_keyboard(is_counselor=True),
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text(
            "⚠️ **No Available Counselors**\n\n"
            "Unable to find another counselor at this time. Please try ending the session and letting the user request again later.",
            reply_markup=create_main_menu_keyboard(is_counselor=True),
            parse_mode='Markdown'
        )

# ==================== (Continuing in next part due to length limit) ====================
