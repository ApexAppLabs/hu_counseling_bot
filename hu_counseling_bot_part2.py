"""
HU Counseling Bot - Part 2: Counselor Registration & Admin Functions
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from counseling_database import COUNSELING_TOPICS

# This file contains the continuation of hu_counseling_bot.py
# Import and integrate these functions into the main bot file

# ==================== COUNSELOR REGISTRATION ====================

async def register_counselor_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start counselor registration process"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Check if already a counselor
    from hu_counseling_bot import db
    counselor = db.get_counselor_by_user_id(user_id)
    if counselor:
        status = counselor['status']
        if status == 'pending':
            await query.edit_message_text(
                "⏳ Your counselor application is pending review.\n\n"
                "An admin will review it soon. We'll notify you once it's approved!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("◀️ Back", callback_data='main_menu')
                ]])
            )
            return
        elif status == 'approved':
            await query.edit_message_text(
                "✅ You're already an approved counselor!\n\n"
                "Go to the Counselor Dashboard to manage your sessions.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("👨‍⚕️ Counselor Dashboard", callback_data='counselor_dashboard')
                ]])
            )
            return
    
    text = """
**Become a Counselor** 👨‍⚕️

Thank you for your interest in serving as a peer counselor!

**Requirements:**
✅ Active member of the gospel fellowship
✅ Mature faith and biblical knowledge
✅ Good listening skills
✅ Commitment to confidentiality
✅ Available regularly (at least 3 hours/week)

**What you'll do:**
• Provide biblical guidance and support
• Listen with empathy and compassion
• Maintain strict confidentiality
• Help students navigate challenges

**Next Steps:**
1. Choose your areas of expertise
2. Write a brief bio
3. Submit for admin approval

Ready to start?
"""
    
    keyboard = [[
        InlineKeyboardButton("✅ Yes, Continue", callback_data='counselor_select_spec'),
        InlineKeyboardButton("❌ Cancel", callback_data='main_menu')
    ]]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def counselor_select_specialization(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Let counselor select specializations"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    from hu_counseling_bot import USER_STATE, create_counselor_specialization_keyboard
    
    if user_id not in USER_STATE:
        USER_STATE[user_id] = {}
    
    selected = USER_STATE[user_id].get('specializations', [])
    
    text = """
**Select Your Areas of Expertise** 📚

Choose the topics you feel equipped to counsel on. Select at least 2 areas.

💡 *Tip: Only choose areas where you have personal experience or strong biblical knowledge.*

Click the icons to select/deselect:
"""
    
    keyboard = create_counselor_specialization_keyboard(selected)
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')

async def toggle_specialization(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle a specialization selection"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    spec = query.data.replace('spec_', '')
    
    from hu_counseling_bot import USER_STATE
    if user_id not in USER_STATE:
        USER_STATE[user_id] = {}
    
    if 'specializations' not in USER_STATE[user_id]:
        USER_STATE[user_id]['specializations'] = []
    
    selected = USER_STATE[user_id]['specializations']
    
    if spec == 'done':
        if len(selected) < 2:
            await query.answer("Please select at least 2 areas of expertise.", show_alert=True)
            return
        
        # Move to bio step
        await counselor_enter_bio(query, context)
        return
    
    # Toggle selection
    if spec in selected:
        selected.remove(spec)
    else:
        if len(selected) >= 5:
            await query.answer("You can select up to 5 areas maximum.", show_alert=True)
            return
        selected.append(spec)
    
    USER_STATE[user_id]['specializations'] = selected
    
    # Update keyboard
    from hu_counseling_bot import create_counselor_specialization_keyboard
    keyboard = create_counselor_specialization_keyboard(selected)
    text = f"""
**Select Your Areas of Expertise** 📚

**Selected:** {len(selected)}/5

Choose the topics you feel equipped to counsel on. Select at least 2 areas.

Click the icons to select/deselect:
"""
    
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')

async def counselor_enter_bio(query, context: ContextTypes.DEFAULT_TYPE):
    """Ask counselor to enter bio"""
    user_id = query.from_user.id
    
    from hu_counseling_bot import USER_STATE
    selected = USER_STATE[user_id].get('specializations', [])
    
    # Show selected topics
    topics_text = '\n'.join([f"• {COUNSELING_TOPICS[s]['icon']} {COUNSELING_TOPICS[s]['name']}" 
                             for s in selected])
    
    text = f"""
**Great! Your expertise:** 👍

{topics_text}

**Now, write a brief bio** (2-3 sentences):

Tell us about yourself:
• Your year/major
• Why you want to be a counselor
• Any relevant experience

*Type your bio and send it as a message:*
"""
    
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data='main_menu')]]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    USER_STATE[user_id]['awaiting_bio'] = True

async def handle_counselor_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle counselor bio submission"""
    user_id = update.effective_user.id
    
    from hu_counseling_bot import USER_STATE, db
    
    if user_id not in USER_STATE or not USER_STATE[user_id].get('awaiting_bio'):
        return
    
    bio = update.message.text
    
    if len(bio) < 50:
        await update.message.reply_text(
            "⚠️ Your bio is too short. Please write at least 50 characters (about 2-3 sentences)."
        )
        return
    
    if len(bio) > 500:
        await update.message.reply_text(
            "⚠️ Your bio is too long. Please keep it under 500 characters."
        )
        return
    
    # Save counselor application
    selected = USER_STATE[user_id].get('specializations', [])
    display_name = f"{update.effective_user.first_name or 'Counselor'}"
    
    counselor_id = db.register_counselor(user_id, display_name, bio, selected)
    
    # Clear state
    USER_STATE[user_id] = {}
    
    # Send confirmation
    await update.message.reply_text(
        "✅ **Application Submitted!**\n\n"
        "Thank you for applying to be a counselor. Your application has been sent to the admin team for review.\n\n"
        "We'll notify you once your application is approved. This usually takes a short time.\n\n"
        "**What happens next:**\n"
        "1. Admins review your application\n"
        "2. You may be contacted for a brief interview\n"
        "3. Once approved, you'll receive access to the Counselor Dashboard\n\n"
        "Thank you for your willingness to serve! 🙏",
        parse_mode='Markdown'
    )
    
    # Notify all admins about new application
    from hu_counseling_bot import ADMIN_IDS
    topics_list = ', '.join([COUNSELING_TOPICS[s]['name'] for s in selected[:3]])
    if len(selected) > 3:
        topics_list += f" (+{len(selected)-3} more)"
    
    admin_message = (
        f"🔔 **New Counselor Application**\n\n"
        f"**Applicant:** {display_name}\n"
        f"**User ID:** `{user_id}`\n"
        f"**Specializations:** {topics_list}\n\n"
        f"**Bio:**\n{bio}\n\n"
        f"📋 Go to Admin Panel → Pending Applications to review."
    )
    
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=admin_message,
                parse_mode='Markdown'
            )
        except Exception as e:
            # Admin might have blocked the bot or doesn't exist
            pass

# ==================== COUNSELOR DASHBOARD ====================

async def counselor_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show counselor dashboard"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    from hu_counseling_bot import db
    counselor = db.get_counselor_by_user_id(user_id)
    
    if not counselor or counselor['status'] != 'approved':
        await query.edit_message_text(
            "⚠️ You are not an approved counselor.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ Back", callback_data='main_menu')
            ]])
        )
        return
    
    counselor_id = counselor['counselor_id']
    is_available = counselor['is_available'] == 1
    total_sessions = counselor['total_sessions']
    
    # Calculate rating
    rating_count = counselor['rating_count']
    rating_sum = counselor['rating_sum']
    avg_rating = (rating_sum / rating_count) if rating_count > 0 else 0
    
    # Check for active session
    active_session = db.get_active_session_by_counselor(counselor_id)
    
    status_icon = "🟢" if is_available else "🔴"
    status_text = "Available" if is_available else "Unavailable"
    
    text = f"""
**Counselor Dashboard** 👨‍⚕️

**Status:** {status_icon} {status_text}
**Total Sessions:** {total_sessions}
**Rating:** {'⭐' * int(avg_rating)} ({avg_rating:.1f}/5.0) from {rating_count} ratings

"""
    
    if active_session:
        text += f"\n📱 **Active Session**\nYou currently have an active counseling session."
    else:
        text += "\n💬 No active sessions"
    
    keyboard = []
    
    # Toggle availability
    toggle_text = "🔴 Go Offline" if is_available else "🟢 Go Online"
    keyboard.append([InlineKeyboardButton(toggle_text, callback_data='toggle_availability')])
    
    # My stats
    keyboard.append([InlineKeyboardButton("📊 My Statistics", callback_data='counselor_stats')])
    
    # View active session if exists
    if active_session:
        keyboard.append([InlineKeyboardButton("📱 View Active Session", callback_data='current_session')])
    
    keyboard.append([InlineKeyboardButton("◀️ Back to Menu", callback_data='main_menu')])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def toggle_availability(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle counselor availability"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    from hu_counseling_bot import db
    counselor = db.get_counselor_by_user_id(user_id)
    
    if not counselor:
        return
    
    counselor_id = counselor['counselor_id']
    current_status = counselor['is_available'] == 1
    new_status = not current_status
    
    # Check if has active session
    if current_status and new_status == False:
        active_session = db.get_active_session_by_counselor(counselor_id)
        if active_session:
            await query.answer("You cannot go offline while in an active session!", show_alert=True)
            return
    
    db.set_counselor_availability(counselor_id, new_status)
    
    status_text = "🟢 Online" if new_status else "🔴 Offline"
    await query.answer(f"Status changed to {status_text}")
    
    # Refresh dashboard
    await counselor_dashboard(update, context)

async def counselor_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show counselor statistics"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    from hu_counseling_bot import db
    counselor = db.get_counselor_by_user_id(user_id)
    
    if not counselor:
        return
    
    total = counselor['total_sessions']
    rating_count = counselor['rating_count']
    rating_sum = counselor['rating_sum']
    avg_rating = (rating_sum / rating_count) if rating_count > 0 else 0
    
    specs = counselor['specializations']
    spec_text = '\n'.join([f"• {COUNSELING_TOPICS[s]['icon']} {COUNSELING_TOPICS[s]['name']}" for s in specs])
    
    text = f"""
**Your Counseling Statistics** 📊

**Total Sessions Completed:** {total}
**Average Rating:** {'⭐' * int(avg_rating)} ({avg_rating:.1f}/5.0)
**Number of Ratings:** {rating_count}

**Your Expertise:**
{spec_text}

**Keep up the great work! 🙏**
"""
    
    keyboard = [[InlineKeyboardButton("◀️ Back to Dashboard", callback_data='counselor_dashboard')]]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# ==================== RATING SYSTEM ====================

async def rate_session_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start session rating"""
    query = update.callback_query
    await query.answer()
    
    session_id = int(query.data.replace('rate_session_', ''))
    
    text = """
**Rate Your Session** ⭐

How was your counseling experience?

Please rate from 1 to 5 stars:
"""
    
    keyboard = [
        [InlineKeyboardButton("⭐", callback_data=f'rating_{session_id}_1'),
         InlineKeyboardButton("⭐⭐", callback_data=f'rating_{session_id}_2'),
         InlineKeyboardButton("⭐⭐⭐", callback_data=f'rating_{session_id}_3')],
        [InlineKeyboardButton("⭐⭐⭐⭐", callback_data=f'rating_{session_id}_4'),
         InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data=f'rating_{session_id}_5')],
        [InlineKeyboardButton("⏭️ Skip", callback_data='main_menu')]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def submit_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Submit session rating"""
    query = update.callback_query
    await query.answer()
    
    data_parts = query.data.replace('rating_', '').split('_')
    session_id = int(data_parts[0])
    rating = int(data_parts[1])
    
    from hu_counseling_bot import db
    db.add_session_rating(session_id, rating)
    
    await query.edit_message_text(
        f"✅ **Thank you for your feedback!**\n\n"
        f"You rated this session: {'⭐' * rating}\n\n"
        f"Your feedback helps us improve our counseling service. 🙏",
        parse_mode='Markdown'
    )

# ==================== ADMIN PANEL ====================

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin panel"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    from hu_counseling_bot import db, ADMIN_IDS
    if not db.is_admin(user_id) and user_id not in ADMIN_IDS:
        await query.answer("⚠️ You don't have admin access.", show_alert=True)
        return
    
    stats = db.get_bot_stats()
    
    text = f"""
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
"""
    
    keyboard = [
        [InlineKeyboardButton("📋 Pending Applications", callback_data='admin_pending_counselors')],
        [InlineKeyboardButton("📊 Detailed Statistics", callback_data='admin_detailed_stats')],
        [InlineKeyboardButton("👥 Manage Counselors", callback_data='admin_manage_counselors')],
        [InlineKeyboardButton("🔔 Pending Sessions", callback_data='admin_pending_sessions')],
        [InlineKeyboardButton("◀️ Back", callback_data='main_menu')]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def admin_pending_counselors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show pending counselor applications"""
    query = update.callback_query
    await query.answer()
    
    from hu_counseling_bot import db
    pending = db.get_pending_counselors()
    
    if not pending:
        text = "📋 **No Pending Applications**\n\nThere are currently no counselor applications waiting for review."
        keyboard = [[InlineKeyboardButton("◀️ Back", callback_data='admin_panel')]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        return
    
    text = f"**Pending Counselor Applications** ({len(pending)})\n\n"
    
    for app in pending[:5]:  # Show first 5
        text += f"**Application #{app['counselor_id']}**\n"
        text += f"User: {app.get('first_name', 'Unknown')}\n"
        text += f"Bio: {app['bio'][:100]}...\n\n"
    
    keyboard = []
    for app in pending[:5]:
        keyboard.append([
            InlineKeyboardButton(f"Review #{app['counselor_id']}", 
                               callback_data=f"review_counselor_{app['counselor_id']}")
        ])
    
    keyboard.append([InlineKeyboardButton("◀️ Back", callback_data='admin_panel')])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def review_counselor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Review a specific counselor application"""
    query = update.callback_query
    await query.answer()
    
    counselor_id = int(query.data.replace('review_counselor_', ''))
    
    from hu_counseling_bot import db
    counselor = db.get_counselor(counselor_id)
    
    if not counselor:
        await query.edit_message_text("⚠️ Application not found.")
        return
    
    specs = counselor['specializations']
    spec_text = '\n'.join([f"• {COUNSELING_TOPICS[s]['name']}" for s in specs])
    
    text = f"""
**Counselor Application Review**

**Applicant ID:** {counselor_id}
**Display Name:** {counselor['display_name']}
**Bio:**
{counselor['bio']}

**Specializations:**
{spec_text}

**Decision:**
"""
    
    keyboard = [
        [InlineKeyboardButton("✅ Approve", callback_data=f'approve_counselor_{counselor_id}'),
         InlineKeyboardButton("❌ Reject", callback_data=f'reject_counselor_{counselor_id}')],
        [InlineKeyboardButton("◀️ Back", callback_data='admin_pending_counselors')]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def approve_counselor_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Approve a counselor application"""
    query = update.callback_query
    await query.answer()
    
    counselor_id = int(query.data.replace('approve_counselor_', ''))
    admin_id = query.from_user.id
    
    from hu_counseling_bot import db
    counselor = db.get_counselor(counselor_id)
    
    if not counselor:
        await query.edit_message_text("⚠️ Application not found.")
        return
    
    db.approve_counselor(counselor_id, admin_id)
    
    # Notify the counselor
    await context.bot.send_message(
        chat_id=counselor['user_id'],
        text="🎉 **Congratulations!**\n\n"
             "Your counselor application has been approved!\n\n"
             "You can now start accepting counseling sessions. Go to your Counselor Dashboard to get started.\n\n"
             "Thank you for your willingness to serve! 🙏",
        parse_mode='Markdown'
    )
    
    await query.edit_message_text(
        f"✅ Counselor #{counselor_id} has been approved!\n\n"
        f"They have been notified and can now start accepting sessions.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("◀️ Back", callback_data='admin_pending_counselors')
        ]]),
        parse_mode='Markdown'
    )

async def reject_counselor_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reject a counselor application"""
    query = update.callback_query
    await query.answer()
    
    counselor_id = int(query.data.replace('reject_counselor_', ''))
    
    from hu_counseling_bot import db
    counselor = db.get_counselor(counselor_id)
    
    if not counselor:
        await query.edit_message_text("⚠️ Application not found.")
        return
    
    db.reject_counselor(counselor_id)
    
    # Notify the applicant
    await context.bot.send_message(
        chat_id=counselor['user_id'],
        text="**Application Update**\n\n"
             "Thank you for your interest in becoming a counselor. "
             "Unfortunately, we are unable to approve your application at this time.\n\n"
             "You may reapply in the future. If you have questions, please contact an admin.",
        parse_mode='Markdown'
    )
    
    await query.edit_message_text(
        f"❌ Counselor application #{counselor_id} has been rejected.\n\n"
        f"The applicant has been notified.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("◀️ Back", callback_data='admin_pending_counselors')
        ]]),
        parse_mode='Markdown'
    )

# ==================== ADDITIONAL ADMIN HANDLERS ====================

async def admin_detailed_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed system statistics"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    from hu_counseling_bot import db, ADMIN_IDS
    if not db.is_admin(user_id) and user_id not in ADMIN_IDS:
        await query.answer("⚠️ You don't have admin access.", show_alert=True)
        return
    
    stats = db.get_bot_stats()
    
    # Get topic distribution
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Top topics
    cursor.execute('''
        SELECT topic, COUNT(*) as count 
        FROM counseling_sessions 
        GROUP BY topic 
        ORDER BY count DESC 
        LIMIT 5
    ''')
    top_topics = cursor.fetchall()
    
    # Average rating
    cursor.execute('''
        SELECT AVG(CAST(rating_sum AS FLOAT) / NULLIF(rating_count, 0)) as avg_rating
        FROM counselors 
        WHERE rating_count > 0
    ''')
    avg_rating_row = cursor.fetchone()
    avg_rating = avg_rating_row['avg_rating'] if avg_rating_row['avg_rating'] else 0
    
    conn.close()
    
    topics_text = '\n'.join([f"• {COUNSELING_TOPICS.get(row['topic'], {}).get('name', row['topic'])}: {row['count']}" 
                             for row in top_topics])
    
    text = f"""
**Detailed System Statistics** 📊

**Users & Counselors:**
👥 Total Users: {stats.get('total_users', 0)}
👨‍⚕️ Total Counselors: {stats.get('total_counselors', 0)}
🟢 Active Counselors: {stats.get('active_counselors', 0)}
✅ Approved: {stats.get('total_counselors', 0) - len(db.get_pending_counselors())}
⏳ Pending: {len(db.get_pending_counselors())}

**Sessions:**
📊 Total: {stats.get('total_sessions', 0)}
🔄 Active: {stats.get('active_sessions', 0)}
✅ Completed: {stats.get('completed_sessions', 0)}
⏳ Pending: {stats.get('pending_sessions', 0)}

**Quality Metrics:**
⭐ Average Rating: {avg_rating:.2f}/5.0

**Top 5 Topics:**
{topics_text if topics_text else '• No data yet'}

**System Health:** ✅ Operational
"""
    
    keyboard = [[InlineKeyboardButton("◀️ Back to Admin Panel", callback_data='admin_panel')]]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def admin_manage_counselors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manage all counselors"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    from hu_counseling_bot import db, ADMIN_IDS
    if not db.is_admin(user_id) and user_id not in ADMIN_IDS:
        await query.answer("⚠️ You don't have admin access.", show_alert=True)
        return
    
    # Get all counselors
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT counselor_id, display_name, status, is_available, total_sessions
        FROM counselors 
        ORDER BY status, counselor_id
        LIMIT 10
    ''')
    counselors = cursor.fetchall()
    conn.close()
    
    if not counselors:
        text = "**Counselor Management** 👥\n\nNo counselors in the system yet."
        keyboard = [[InlineKeyboardButton("◀️ Back", callback_data='admin_panel')]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        return
    
    text = "**Counselor Management** 👥\n\n"
    
    for c in counselors[:10]:
        status_emoji = {"approved": "✅", "pending": "⏳", "rejected": "❌"}.get(c['status'], "❓")
        avail_emoji = "🟢" if c['is_available'] else "🔴"
        text += f"{status_emoji} **{c['display_name']}** (ID: {c['counselor_id']})\n"
        text += f"   Status: {c['status'].title()} | {avail_emoji} | Sessions: {c['total_sessions']}\n\n"
    
    keyboard = [
        [InlineKeyboardButton("📋 View Pending Applications", callback_data='admin_pending_counselors')],
        [InlineKeyboardButton("🔄 Refresh List", callback_data='admin_manage_counselors')],
        [InlineKeyboardButton("◀️ Back", callback_data='admin_panel')]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def admin_pending_sessions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View pending counseling sessions"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    from hu_counseling_bot import db, ADMIN_IDS
    if not db.is_admin(user_id) and user_id not in ADMIN_IDS:
        await query.answer("⚠️ You don't have admin access.", show_alert=True)
        return
    
    pending = db.get_pending_sessions(limit=10)
    
    if not pending:
        text = "**Pending Sessions** 🔔\n\nNo pending sessions waiting for counselors."
        keyboard = [[InlineKeyboardButton("◀️ Back", callback_data='admin_panel')]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        return
    
    text = f"**Pending Sessions** 🔔\n\nThere are **{len(pending)}** sessions waiting for counselors:\n\n"
    
    for session in pending[:5]:
        topic_data = COUNSELING_TOPICS.get(session['topic'], {})
        text += f"**Session #{session['session_id']}**\n"
        text += f"Topic: {topic_data.get('icon', '💬')} {topic_data.get('name', session['topic'])}\n"
        text += f"Requested: {session.get('created_at', 'Unknown')}\n"
        text += f"Description: {session.get('description', 'No description')[:50]}...\n\n"
    
    if len(pending) > 5:
        text += f"\n*...and {len(pending) - 5} more sessions*"
    
    text += "\n\n💡 **Note:** These sessions are waiting for available counselors to come online."
    
    keyboard = [
        [InlineKeyboardButton("🔄 Refresh", callback_data='admin_pending_sessions')],
        [InlineKeyboardButton("◀️ Back", callback_data='admin_panel')]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# Export all handler functions
__all__ = [
    'register_counselor_start', 'counselor_select_specialization', 'toggle_specialization',
    'handle_counselor_bio', 'counselor_dashboard', 'toggle_availability', 'counselor_stats',
    'rate_session_start', 'submit_rating', 'admin_panel', 'admin_pending_counselors',
    'review_counselor', 'approve_counselor_handler', 'reject_counselor_handler',
    'admin_detailed_stats', 'admin_manage_counselors', 'admin_pending_sessions'
]
