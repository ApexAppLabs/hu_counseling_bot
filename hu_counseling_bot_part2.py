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

Choose the topics you feel equipped to counsel on. Select 1-2 areas.

💡 *Tip: Only choose areas where you have personal experience or strong biblical knowledge.*

Click the topics to select/deselect:
"""
    
    keyboard = create_counselor_specialization_keyboard(selected)
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')

async def toggle_specialization(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle a specialization selection (handles both registration and editing)"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    spec = query.data.replace('spec_', '')
    
    from hu_counseling_bot import USER_STATE
    if user_id not in USER_STATE:
        USER_STATE[user_id] = {}
    
    # Check if in edit mode
    if USER_STATE[user_id].get('editing') == 'specs':
        # Delegate to edit handler
        await toggle_edit_specialization(update, context)
        return
    
    # Otherwise, handle as registration
    if 'specializations' not in USER_STATE[user_id]:
        USER_STATE[user_id]['specializations'] = []
    
    selected = USER_STATE[user_id]['specializations']
    
    if spec == 'done':
        if len(selected) < 1:
            await query.answer("Please select at least 1 area of expertise.", show_alert=True)
            return
        
        # Move to gender selection step
        await counselor_select_gender(query, context)
        return
    
    # Toggle selection
    if spec in selected:
        selected.remove(spec)
    else:
        if len(selected) >= 2:
            await query.answer("You can select up to 2 areas maximum.", show_alert=True)
            return
        selected.append(spec)
    
    USER_STATE[user_id]['specializations'] = selected
    
    # Update keyboard
    from hu_counseling_bot import create_counselor_specialization_keyboard
    keyboard = create_counselor_specialization_keyboard(selected)
    text = f"""
**Select Your Areas of Expertise** 📚

**Selected:** {len(selected)}/2

Choose the topics you feel equipped to counsel on. Select 1-2 areas.

Click the topics to select/deselect:
"""
    
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')

async def counselor_select_gender(query, context: ContextTypes.DEFAULT_TYPE):
    """Ask counselor to select their gender"""
    user_id = query.from_user.id
    
    from hu_counseling_bot import USER_STATE
    selected = USER_STATE[user_id].get('specializations', [])
    
    # Show selected topics
    topics_text = '\n'.join([f"• {COUNSELING_TOPICS[s]['icon']} {COUNSELING_TOPICS[s]['name']}" 
                             for s in selected])
    
    text = f"""
**Great! Your expertise:** 👍

{topics_text}

**Select Your Gender** 👤

This helps us provide appropriate guidance and matching. Your gender is stored for admin and matching purposes and is not shown directly to users.

**Why we ask:**
• Some topics require gender-specific advice
• Users may have preferences for their counselor
• Helps maintain appropriate boundaries

Choose an option:
"""
    
    keyboard = [
        [InlineKeyboardButton("👨 Male", callback_data='gender_male')],
        [InlineKeyboardButton("👩 Female", callback_data='gender_female')],
        [InlineKeyboardButton("🔒 Prefer not to say (Anonymous)", callback_data='gender_anonymous')],
        [InlineKeyboardButton("◀️ Back", callback_data='counselor_select_spec')]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def gender_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle gender selection"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    gender = query.data.replace('gender_', '')
    
    from hu_counseling_bot import USER_STATE
    if user_id not in USER_STATE:
        USER_STATE[user_id] = {}
    
    USER_STATE[user_id]['gender'] = gender
    
    # Move to display name step
    await counselor_enter_display_name(query, context)

async def counselor_enter_display_name(query, context: ContextTypes.DEFAULT_TYPE):
    """Ask counselor to enter display name"""
    user_id = query.from_user.id
    
    from hu_counseling_bot import USER_STATE
    
    text = """
**Choose a Display Name** 📛

This name will generally be visible to the **Admin** of the bot for management purposes.

Users will typically see "Counselor #ID" to maintain anonymity, though this name may be used for internal identification.

*Type your Display Name (e.g., your real First Name or a Pseudonym):*
"""
    
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data='main_menu')]]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    USER_STATE[user_id]['awaiting_display_name'] = True

async def handle_counselor_display_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle counselor display name submission"""
    user_id = update.effective_user.id
    from hu_counseling_bot import USER_STATE, db
    
    if user_id not in USER_STATE or not USER_STATE[user_id].get('awaiting_display_name'):
        return

    name = update.message.text.strip()
    
    if len(name) < 2:
        await update.message.reply_text("⚠️ Name is too short. Please use at least 2 characters.")
        return
        
    if len(name) > 50:
        await update.message.reply_text("⚠️ Name is too long. Please keep it under 50 characters.")
        return
        
    USER_STATE[user_id]['display_name'] = name
    USER_STATE[user_id]['awaiting_display_name'] = False
    
    # Now ask for bio
    selected = USER_STATE[user_id].get('specializations', [])
    topics_text = '\\n'.join([f"• {COUNSELING_TOPICS[s]['icon']} {COUNSELING_TOPICS[s]['name']}" for s in selected])
    
    text = f"""
**Display Name Set:** {name} ✅

**Your expertise:**
{topics_text}

**Now, write a brief bio** (2-3 sentences):

Tell us about yourself:
• Your year/major
• Why you want to be a counselor
• Any relevant experience

*Type your bio and send it as a message:*
"""
    
    USER_STATE[user_id]['awaiting_bio'] = True
    await update.message.reply_text(text, parse_mode='Markdown')

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
    gender = USER_STATE[user_id].get('gender', 'anonymous')
    display_name = USER_STATE[user_id].get('display_name') or f"{update.effective_user.first_name or 'Counselor'}"
    
    counselor_id = db.register_counselor(user_id, display_name, bio, selected, gender)
    
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
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to notify admin {admin_id} about counselor application: {e}")

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
    
    rating_count = counselor['rating_count']
    rating_sum = counselor['rating_sum']
    avg_rating = (rating_sum / rating_count) if rating_count > 0 else 0
    
    active_sessions = db.get_active_sessions_by_counselor(counselor_id)
    
    status_icon = "🟢" if is_available else "🔴"
    status_text = "Available" if is_available else "Unavailable"
    
    text = f"""
**Counselor Dashboard** 👨‍⚕️

**Status:** {status_icon} {status_text}
**Total Sessions:** {total_sessions}
**Rating:** {'⭐' * int(avg_rating)} ({avg_rating:.1f}/5.0) from {rating_count} ratings

"""
    
    if active_sessions:
        text += f"\n📱 **Active Sessions:** {len(active_sessions)}\nSelect a session below to focus your replies."
    else:
        text += "\n💬 No active sessions"
    
    keyboard = []
    
    toggle_text = "🔴 Go Offline" if is_available else "🟢 Go Online"
    keyboard.append([InlineKeyboardButton(toggle_text, callback_data='toggle_availability')])
    
    keyboard.append([InlineKeyboardButton("📊 My Statistics", callback_data='counselor_stats')])
    keyboard.append([InlineKeyboardButton("✏️ Edit Profile", callback_data='counselor_edit_profile')])
    
    if active_sessions:
        for s in active_sessions[:5]:
            topic_data = COUNSELING_TOPICS.get(s['topic'], {})
            topic_icon = topic_data.get('icon', '💬')
            topic_name = topic_data.get('name', s['topic'])
            status_label = 'Active' if s['status'] == 'active' else 'Waiting'
            button_text = f"{topic_icon} #{s['session_id']} - {topic_name} ({status_label})"
            keyboard.append([
                InlineKeyboardButton(button_text, callback_data=f'switch_session_{s["session_id"]}')
            ])
        keyboard.append([InlineKeyboardButton("📱 Go to Current Session View", callback_data='current_session')])
    
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
    
    # Check if has any pending or active session
    if current_status and new_status is False:
        active_sessions = db.get_active_sessions_by_counselor(counselor_id)
        if active_sessions:
            await query.answer("You cannot go offline while you have a pending or active session!", show_alert=True)
            return
    
    db.set_counselor_availability(counselor_id, new_status)
    
    # If counselor just came online, immediately try to auto-match pending sessions
    if new_status:
        from hu_counseling_bot import matcher
        pending_sessions = db.get_pending_sessions(limit=20)
        for session in pending_sessions:
            session_id = session['session_id']
            matched_counselor_id = matcher.find_best_match(session_id)
            if not matched_counselor_id:
                continue

            db.match_session_with_counselor(session_id, matched_counselor_id)
            counselor_match = db.get_counselor(matched_counselor_id)
            if not counselor_match:
                continue

            topic_data = COUNSELING_TOPICS.get(session['topic'], {})
            desc = session.get('description') or 'No description provided'
            preview = desc[:100] + ('...' if len(desc) > 100 else '')

            # Get user's gender
            user_data = db.get_user(session['user_id'])
            user_gender = user_data.get('gender', 'anonymous') if user_data else 'anonymous'
            gender_display = {
                'male': '👨 Male',
                'female': '👩 Female',
                'anonymous': '🔒 Anonymous'
            }.get(user_gender, '🔒 Anonymous')

            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ Accept Session", callback_data=f'accept_session_{session_id}'),
                InlineKeyboardButton("❌ Decline", callback_data=f'decline_session_{session_id}')
            ]])

            await context.bot.send_message(
                chat_id=counselor_match['user_id'],
                text=(
                    f"**🔔 New Counseling Request**\n\n"
                    f"**Topic:** {topic_data.get('icon', '💬')} {topic_data.get('name', session['topic'])}\n"
                    f"**User Gender:** {gender_display}\n"
                    f"**Description:** {preview}\n\n"
                    f"Would you like to accept this session?"
                ),
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
    
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
        text += f"User: {app.get('first_name') or 'Unknown'}\n"
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
    
    # Gender display
    gender_display = {
        'male': '👨 Male',
        'female': '👩 Female',
        'anonymous': '🔒 Anonymous'
    }.get(counselor.get('gender', 'anonymous'), '🔒 Anonymous')
    
    text = f"""
**Counselor Application Review**

**Applicant ID:** {counselor_id}
**Display Name:** {counselor['display_name']}
**Gender:** {gender_display}
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
    """Show detailed system statistics with REAL data"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    from hu_counseling_bot import db, ADMIN_IDS
    if not db.is_admin(user_id) and user_id not in ADMIN_IDS:
        await query.answer("⚠️ You don't have admin access.", show_alert=True)
        return
    
    # Get REAL statistics directly from database
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Total users
    cursor.execute('SELECT COUNT(*) as count FROM users')
    total_users = cursor.fetchone()['count']
    
    # Total counselors
    cursor.execute('SELECT COUNT(*) as count FROM counselors')
    total_counselors = cursor.fetchone()['count']
    
    # Approved counselors
    cursor.execute("SELECT COUNT(*) as count FROM counselors WHERE status = 'approved'")
    approved_counselors = cursor.fetchone()['count']
    
    # Currently online counselors
    cursor.execute("SELECT COUNT(*) as count FROM counselors WHERE status = 'approved' AND is_available = 1")
    online_counselors = cursor.fetchone()['count']
    
    # Pending counselors
    cursor.execute("SELECT COUNT(*) as count FROM counselors WHERE status = 'pending'")
    pending_counselors = cursor.fetchone()['count']
    
    # Rejected counselors
    cursor.execute("SELECT COUNT(*) as count FROM counselors WHERE status = 'rejected'")
    rejected_counselors = cursor.fetchone()['count']
    
    # Deactivated counselors
    cursor.execute("SELECT COUNT(*) as count FROM counselors WHERE status = 'deactivated'")
    deactivated_counselors = cursor.fetchone()['count']
    
    # Banned counselors
    cursor.execute("SELECT COUNT(*) as count FROM counselors WHERE status = 'banned'")
    banned_counselors = cursor.fetchone()['count']
    
    # Total sessions
    cursor.execute('SELECT COUNT(*) as count FROM counseling_sessions')
    total_sessions = cursor.fetchone()['count']
    
    # Active sessions
    cursor.execute("SELECT COUNT(*) as count FROM counseling_sessions WHERE status = 'active'")
    active_sessions = cursor.fetchone()['count']
    
    # Completed/ended sessions
    cursor.execute("SELECT COUNT(*) as count FROM counseling_sessions WHERE status = 'ended'")
    completed_sessions = cursor.fetchone()['count']
    
    # Pending sessions (waiting for counselor)
    cursor.execute("SELECT COUNT(*) as count FROM counseling_sessions WHERE status = 'requested'")
    pending_sessions = cursor.fetchone()['count']
    
    # Matched sessions (counselor matched but not accepted yet)
    cursor.execute("SELECT COUNT(*) as count FROM counseling_sessions WHERE status = 'matched'")
    matched_sessions = cursor.fetchone()['count']
    
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
        SELECT AVG(CAST(rating_sum AS FLOAT) / NULLIF(rating_count, 0)) as avg_rating,
               SUM(rating_count) as total_ratings
        FROM counselors 
        WHERE rating_count > 0
    ''')
    rating_row = cursor.fetchone()
    avg_rating = rating_row['avg_rating'] if rating_row['avg_rating'] else 0
    total_ratings = rating_row['total_ratings'] if rating_row['total_ratings'] else 0
    
    # Total messages exchanged
    cursor.execute('SELECT COUNT(*) as count FROM session_messages')
    total_messages = cursor.fetchone()['count']
    
    conn.close()
    
    # Format top topics
    topics_text = '\n'.join([
        f"• {COUNSELING_TOPICS.get(row['topic'], {}).get('icon', '💬')} {COUNSELING_TOPICS.get(row['topic'], {}).get('name', row['topic'])}: {row['count']}" 
        for row in top_topics
    ])
    
    # Calculate completion rate
    completion_rate = 0
    if total_sessions > 0:
        completion_rate = (completed_sessions / total_sessions) * 100
    
    text = f"""
**📊 Detailed System Statistics**

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
"""
    
    keyboard = [
        [InlineKeyboardButton("🔄 Refresh", callback_data='admin_detailed_stats')],
        [InlineKeyboardButton("◀️ Back to Admin Panel", callback_data='admin_panel')]
    ]
    
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
    
    text = "**Counselor Management** 👥\n\nClick on a counselor to manage:\n\n"
    
    keyboard = []
    for c in counselors[:10]:
        status_emoji = {
            "approved": "✅", 
            "pending": "⏳", 
            "rejected": "❌", 
            "deactivated": "🔴",
            "banned": "🚫"
        }.get(c['status'], "❓")
        avail_emoji = "🟢" if c['is_available'] else "🔴"
        
        # Create button for each counselor
        button_text = f"{status_emoji} {c['display_name']} (#{c['counselor_id']})"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f'admin_view_counselor_{c["counselor_id"]}')])
    
    keyboard.extend([
        [InlineKeyboardButton("📋 View Pending Applications", callback_data='admin_pending_counselors')],
        [InlineKeyboardButton("🔄 Refresh List", callback_data='admin_manage_counselors')],
        [InlineKeyboardButton("◀️ Back", callback_data='admin_panel')]
    ])
    
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
    
    text = f"**Pending Sessions** 🔔\n\nThere are **{len(pending)}** sessions waiting for counselors.\n\nSelect a session to view details or assign manually:"
    
    keyboard = []
    
    for session in pending:
        topic_data = COUNSELING_TOPICS.get(session['topic'], {})
        topic_name = topic_data.get('name', session['topic'])
        wait_time = "Unknown"
        # simple wait time calc if created_at is string
        if isinstance(session.get('created_at'), str):
            try:
                created_dt = datetime.fromisoformat(session['created_at'])
                delta = datetime.now() - created_dt
                minutes = int(delta.total_seconds() / 60)
                wait_time = f"{minutes}m"
            except:
                pass
                
        button_text = f"#{session['session_id']} {topic_name} (Wait: {wait_time})"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f'admin_view_session_{session["session_id"]}')])
    
    keyboard.extend([
        [InlineKeyboardButton("🔄 Refresh", callback_data='admin_pending_sessions')],
        [InlineKeyboardButton("◀️ Back", callback_data='admin_panel')]
    ])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def admin_view_pending_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View details of a pending session and take action"""
    query = update.callback_query
    await query.answer()
    
    try:
        session_id = int(query.data.replace('admin_view_session_', ''))
    except ValueError:
        return

    from hu_counseling_bot import db, ADMIN_IDS
    session = db.get_session(session_id)
    
    if not session or session['status'] != 'requested':
        await query.edit_message_text(
            "⚠️ This session is no longer pending (it may have been accepted or cancelled).",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data='admin_pending_sessions')]])
        )
        return

    # Get user gender for context
    user_data = db.get_user(session['user_id'])
    user_gender = user_data.get('gender', 'anonymous') if user_data else 'anonymous'
    gender_display = {
        'male': '👨 Male',
        'female': '👩 Female',
        'anonymous': '🔒 Anonymous'
    }.get(user_gender, '🔒 Anonymous')

    topic_data = COUNSELING_TOPICS.get(session['topic'], {})
    
    # Format created_at to be human readable (remove microseconds)
    created_time = session.get('created_at', 'Unknown')
    try:
        if isinstance(created_time, str):
            dt = datetime.fromisoformat(created_time)
            created_time = dt.strftime("%Y-%m-%d %H:%M")
    except:
        pass

    text = f"""
**Pending Session #{session_id}** 📋

**Topic:** {topic_data.get('icon', '💬')} {topic_data.get('name', session['topic'])}
**User Gender:** {gender_display}
**Created:** {created_time}

**Description:**
{session.get('description', 'No description provided')}

**Actions:**
"""
    
    keyboard = []
    
    # Check if admin is also a counselor
    counselor = db.get_counselor_by_user_id(query.from_user.id)
    if counselor and counselor['status'] == 'approved':
        keyboard.append([InlineKeyboardButton("✅ Accept Session Myself", callback_data=f'admin_accept_session_{session_id}')])
    
    # Assign to other counselor option
    keyboard.append([InlineKeyboardButton("👥 Assign to Other Counselor", callback_data=f'admin_assign_start_{session_id}')])
    
    keyboard.append([InlineKeyboardButton("◀️ Back to List", callback_data='admin_pending_sessions')])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def admin_accept_session_as_counselor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin accepts a pending session directly"""
    query = update.callback_query
    await query.answer()
    
    session_id = int(query.data.replace('admin_accept_session_', ''))
    user_id = query.from_user.id
    
    from hu_counseling_bot import db, accept_session
    
    # 1. Get admin's counselor profile
    counselor = db.get_counselor_by_user_id(user_id)
    if not counselor or counselor['status'] != 'approved':
        await query.answer("⚠️ You must be a registered counselor to accept sessions.", show_alert=True)
        return

    # 2. MATCH the session to this counselor first (changing status from requested -> matched)
    # This fixes the issue where accept_session fails because status is not 'matched'
    db.match_session_with_counselor(session_id, counselor['counselor_id'])
    
    # 3. Now verify it worked and proceed to accept
    session = db.get_session(session_id)
    if session and session['status'] == 'matched':
        # Hack query data for the reuse of accept_session
        query.data = f"accept_session_{session_id}"
        await accept_session(update, context)
    else:
        await query.edit_message_text("⚠️ Failed to assign session. It may have been taken by someone else.")

async def admin_assign_session_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of counselors to assign a session to"""
    query = update.callback_query
    await query.answer()
    
    session_id = int(query.data.replace('admin_assign_start_', ''))
    
    from hu_counseling_bot import db
    
    # Get session to check topic
    session = db.get_session(session_id)
    if not session:
        return
    session_topic = session['topic']
    
    # Get all potential counselors with specs
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT counselor_id, display_name, is_available, total_sessions, specializations
        FROM counselors 
        WHERE status = 'approved'
        ORDER BY is_available DESC, total_sessions ASC
        LIMIT 20
    ''')
    counselors = cursor.fetchall()
    conn.close()
    
    if not counselors:
        await query.edit_message_text(
            "⚠️ No approved counselors found to assign to.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data=f'admin_view_session_{session_id}')]])
        )
        return
        
    text = f"**Assign Session #{session_id}**\n\nSelect a counselor to assign this session to:\n⭐ = Specialized in this topic"
    
    keyboard = []
    
    import json
    
    for c in counselors:
        # Parse specs
        specs = []
        try:
            val = c['specializations']
            if val:
                specs = json.loads(val)
        except:
            pass
            
        is_spec = session_topic in specs or 'other' in specs
        spec_mark = "⭐" if session_topic in specs else ""
        
        status = "🟢" if c['is_available'] else "🔴"
        btn_text = f"{status} {c['display_name']} {spec_mark}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f'admin_assign_confirm_{session_id}_{c["counselor_id"]}')])
        
    keyboard.append([InlineKeyboardButton("◀️ Back", callback_data=f'admin_view_session_{session_id}')])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def admin_assign_session_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Perform the assignment of a session to a counselor"""
    query = update.callback_query
    await query.answer()
    
    try:
        _, _, _, session_id_str, counselor_id_str = query.data.split('_')
        session_id = int(session_id_str)
        counselor_id = int(counselor_id_str)
    except:
        return
        
    from hu_counseling_bot import db, COUNSELING_TOPICS
    
    # Check if session is still pending
    session = db.get_session(session_id)
    if not session or session['status'] != 'requested':
        await query.edit_message_text("⚠️ Session is no longer pending.")
        return
        
    # Match in DB
    db.match_session_with_counselor(session_id, counselor_id)
    
    # Notify the counselor
    counselor = db.get_counselor(counselor_id)
    if not counselor:
        await query.edit_message_text("⚠️ Create counselor error.")
        return
        
    topic_data = COUNSELING_TOPICS.get(session['topic'], {})
    desc = session.get('description') or 'No description provided'
    
    # Get user gender
    user_data = db.get_user(session['user_id'])
    user_gender = user_data.get('gender', 'anonymous') if user_data else 'anonymous'
    gender_display = {'male': '👨 Male', 'female': '👩 Female'}.get(user_gender, '🔒 Anonymous')
    
    # Send notification to assigned counselor
    try:
        keyboard = [[
            InlineKeyboardButton("✅ Accept Session", callback_data=f'accept_session_{session_id}'),
            InlineKeyboardButton("❌ Decline", callback_data=f'decline_session_{session_id}')
        ]]
        
        await context.bot.send_message(
            chat_id=counselor['user_id'],
            text=(
                f"**🔔 Session Assigned by Admin**\n\n"
                f"An admin has manually assigned you a session.\n\n"
                f"**Topic:** {topic_data.get('icon', '💬')} {topic_data.get('name', session['topic'])}\n"
                f"**User Gender:** {gender_display}\n"
                f"**Description:** {desc[:100]}...\n\n"
                f"Please accept or decline below."
            ),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        msg = f"✅ **Assigned!**\n\nSession #{session_id} has been assigned to {counselor['display_name']}."
    except Exception as e:
        msg = f"⚠️ Assigned but failed to notify counselor: {e}"
    
    keyboard = [[InlineKeyboardButton("◀️ Back to List", callback_data='admin_pending_sessions')]]
    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# ==================== NEW ADMIN MANAGEMENT HANDLERS ====================

async def admin_view_counselor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View detailed counselor information"""
    query = update.callback_query
    await query.answer()
    
    counselor_id = int(query.data.replace('admin_view_counselor_', ''))
    
    from hu_counseling_bot import db
    counselor = db.get_counselor(counselor_id)
    
    if not counselor:
        await query.edit_message_text("⚠️ Counselor not found.")
        return
    
    # counselor['specializations'] is already a Python list from the database layer.
    # For safety, handle the case where it might still be stored as a JSON string.
    import json
    specs_value = counselor.get('specializations', [])
    if isinstance(specs_value, str):
        try:
            specs_value = json.loads(specs_value) or []
        except Exception:
            specs_value = []
    counselor['specializations'] = specs_value
    
    # Get additional info
    conn = db.get_connection()
    cursor = conn.cursor()
    ph = db.param_placeholder
    
    # Get rating info
    rating_avg = 0
    if counselor['rating_count'] > 0:
        rating_avg = counselor['rating_sum'] / counselor['rating_count']
    
    # Get active session count
    cursor.execute(f'''
        SELECT COUNT(*) as count FROM counseling_sessions 
        WHERE counselor_id = {ph} AND status = 'active'
    ''', (counselor_id,))
    active_sessions = cursor.fetchone()['count']
    
    conn.close()
    
    # Format specializations
    specs = counselor['specializations']
    spec_text = '\n'.join([f"• {COUNSELING_TOPICS[s]['icon']} {COUNSELING_TOPICS[s]['name']}" for s in specs])
    
    # Status display
    status_emoji = {
        "approved": "✅ Approved",
        "pending": "⏳ Pending",
        "rejected": "❌ Rejected",
        "deactivated": "🔴 Deactivated",
        "banned": "🚫 Banned"
    }.get(counselor['status'], "❓ Unknown")
    
    avail_status = "🟢 Online" if counselor['is_available'] else "🔴 Offline"
    
    # Gender display
    gender_display = {
        'male': '👨 Male',
        'female': '👩 Female',
        'anonymous': '🔒 Anonymous'
    }.get(counselor.get('gender', 'anonymous'), '🔒 Anonymous')
    
    text = f"""
**Counselor Details** 📊

**ID:** {counselor_id}
**Display Name:** {counselor['display_name']}
**Gender:** {gender_display}
**Status:** {status_emoji}
**Availability:** {avail_status}

**Statistics:**
📊 Total Sessions: {counselor['total_sessions']}
🔄 Active Now: {active_sessions}
⭐ Rating: {rating_avg:.1f}/5.0 ({counselor['rating_count']} ratings)

**Bio:**
{counselor['bio']}

**Specializations:**
{spec_text}

**Actions:**
"""
    
    # Create action buttons based on status
    keyboard = []
    
    if counselor['status'] == 'approved':
        keyboard.append([InlineKeyboardButton("🔴 Deactivate", callback_data=f'admin_deactivate_{counselor_id}')])
        keyboard.append([InlineKeyboardButton("🗑️ Delete", callback_data=f'admin_delete_{counselor_id}')])
    elif counselor['status'] == 'deactivated':
        keyboard.append([InlineKeyboardButton("🟢 Reactivate", callback_data=f'admin_reactivate_{counselor_id}')])
        keyboard.append([InlineKeyboardButton("🗑️ Delete", callback_data=f'admin_delete_{counselor_id}')])
    elif counselor['status'] == 'pending':
        keyboard.append([InlineKeyboardButton("✅ Approve", callback_data=f'approve_counselor_{counselor_id}')])
        keyboard.append([InlineKeyboardButton("❌ Reject", callback_data=f'reject_counselor_{counselor_id}')])
    elif counselor['status'] == 'banned':
        keyboard.append([InlineKeyboardButton("🗑️ Delete", callback_data=f'admin_delete_{counselor_id}')])
    
    keyboard.append([InlineKeyboardButton("✏️ Edit Info", callback_data=f'admin_edit_{counselor_id}')])
    keyboard.append([InlineKeyboardButton("◀️ Back", callback_data='admin_manage_counselors')])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def admin_deactivate_counselor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Deactivate a counselor temporarily"""
    query = update.callback_query
    await query.answer()
    
    counselor_id = int(query.data.replace('admin_deactivate_', ''))
    admin_id = query.from_user.id
    
    from hu_counseling_bot import db
    counselor = db.get_counselor(counselor_id)
    
    if not counselor:
        await query.edit_message_text("⚠️ Counselor not found.")
        return
    
    db.deactivate_counselor(counselor_id, admin_id)
    
    # Notify counselor
    await context.bot.send_message(
        chat_id=counselor['user_id'],
        text="⚠️ **Account Deactivated**\n\n"
             "Your counselor account has been temporarily deactivated by an administrator.\n\n"
             "You cannot accept new sessions until reactivated. Please contact fellowship leadership for more information.",
        parse_mode='Markdown'
    )
    
    await query.edit_message_text(
        f"🔴 **Counselor Deactivated**\n\n"
        f"Counselor #{counselor_id} ({counselor['display_name']}) has been deactivated.\n\n"
        f"They have been notified and cannot accept new sessions.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("◀️ Back to List", callback_data='admin_manage_counselors')
        ]]),
        parse_mode='Markdown'
    )

async def admin_reactivate_counselor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reactivate a deactivated counselor"""
    query = update.callback_query
    await query.answer()
    
    counselor_id = int(query.data.replace('admin_reactivate_', ''))
    admin_id = query.from_user.id
    
    from hu_counseling_bot import db
    counselor = db.get_counselor(counselor_id)
    
    if not counselor:
        await query.edit_message_text("⚠️ Counselor not found.")
        return
    
    db.reactivate_counselor(counselor_id, admin_id)
    
    # Notify counselor
    await context.bot.send_message(
        chat_id=counselor['user_id'],
        text="✅ **Account Reactivated**\n\n"
             "Your counselor account has been reactivated!\n\n"
             "You can now toggle your availability and start accepting sessions again. 🙏",
        parse_mode='Markdown'
    )
    
    await query.edit_message_text(
        f"✅ **Counselor Reactivated**\n\n"
        f"Counselor #{counselor_id} ({counselor['display_name']}) has been reactivated.\n\n"
        f"They can now accept sessions again.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("◀️ Back to List", callback_data='admin_manage_counselors')
        ]]),
        parse_mode='Markdown'
    )

async def admin_delete_counselor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete a counselor account completely"""
    query = update.callback_query
    await query.answer()
    
    counselor_id = int(query.data.replace('admin_delete_', ''))
    admin_id = query.from_user.id
    
    from hu_counseling_bot import db
    counselor = db.get_counselor(counselor_id)
    
    if not counselor:
        await query.edit_message_text("⚠️ Counselor not found.")
        return
    
    ok = db.delete_counselor(counselor_id, admin_id)
    if not ok:
        await query.answer("Cannot delete: counselor has active or matched sessions.", show_alert=True)
        return

    try:
        await context.bot.send_message(
            chat_id=counselor['user_id'],
            text="🗑️ **Account Deleted**\n\nYour counselor account has been removed by an admin.",
            parse_mode='Markdown'
        )
    except Exception:
        pass

    await query.edit_message_text(
        f"🗑️ **Counselor Deleted**\n\n"
        f"Counselor #{counselor_id} ({counselor['display_name']}) has been removed from the system.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("◀️ Back to List", callback_data='admin_manage_counselors')
        ]]),
        parse_mode='Markdown'
    )

async def admin_edit_counselor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Edit counselor information - shows edit options"""
    query = update.callback_query
    await query.answer()
    
    counselor_id = int(query.data.replace('admin_edit_', ''))
    
    from hu_counseling_bot import db
    counselor = db.get_counselor(counselor_id)
    
    if not counselor:
        await query.edit_message_text("⚠️ Counselor not found.")
        return
    
    text = f"""
**Edit Counselor Info** ✏️

**Counselor:** {counselor['display_name']} (#{counselor_id})

**Current Information:**
• Display Name: {counselor['display_name']}
• Status: {counselor['status']}
• Total Sessions: {counselor['total_sessions']}

**Note:** To edit counselor information, contact the counselor directly and ask them to update their profile, or use the database admin tools.

**Future Feature:** Direct editing UI will be added soon.
"""
    
    keyboard = [
        [InlineKeyboardButton("📱 Message Counselor", url=f"tg://user?id={counselor['user_id']}")],
        [InlineKeyboardButton("◀️ Back", callback_data=f'admin_view_counselor_{counselor_id}')]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# ==================== COUNSELOR EDIT PROFILE ====================

async def counselor_edit_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show counselor profile edit menu"""
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
    
    specs = counselor['specializations']
    spec_text = '\n'.join([f"• {COUNSELING_TOPICS[s]['icon']} {COUNSELING_TOPICS[s]['name']}" for s in specs])
    
    gender_display = {
        'male': '👨 Male',
        'female': '👩 Female',
        'anonymous': '🔒 Anonymous'
    }.get(counselor.get('gender', 'anonymous'), '🔒 Anonymous')
    
    text = f"""
**Edit Your Profile** ✏️

**Current Information:**

**Display Name:** {counselor['display_name']}
**Gender:** {gender_display}

**Bio:**
{counselor['bio']}

**Specializations:**
{spec_text}

**What would you like to edit?**
"""
    
    keyboard = [
        [InlineKeyboardButton("✏️ Edit Display Name", callback_data='edit_counselor_name')],
        [InlineKeyboardButton("📝 Edit Bio", callback_data='edit_counselor_bio')],
        [InlineKeyboardButton("📚 Edit Specializations", callback_data='edit_counselor_specs')],
        [InlineKeyboardButton("👤 Edit Gender", callback_data='edit_counselor_gender')],
        [InlineKeyboardButton("◀️ Back to Dashboard", callback_data='counselor_dashboard')]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def edit_counselor_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start editing counselor display name"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    text = """
**Edit Display Name** ✏️

Please type your new display name and send it as a message.

This name is visible to the **Admin**. Users will essentially see "Counselor #ID" to maintain your anonymity.

*Type your new display name:*
"""
    
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data='counselor_edit_profile')]]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    from hu_counseling_bot import USER_STATE
    if user_id not in USER_STATE:
        USER_STATE[user_id] = {}
    USER_STATE[user_id]['editing'] = 'name'

async def edit_counselor_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start editing counselor bio"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    from hu_counseling_bot import db
    counselor = db.get_counselor_by_user_id(user_id)
    
    text = f"""
**Edit Bio** 📝

**Current Bio:**
{counselor['bio']}

Please type your new bio (2-3 sentences, 50-500 characters) and send it as a message.

Tell us about:
• Your year/major
• Why you want to be a counselor
• Any relevant experience

*Type your new bio:*
"""
    
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data='counselor_edit_profile')]]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    from hu_counseling_bot import USER_STATE
    if user_id not in USER_STATE:
        USER_STATE[user_id] = {}
    USER_STATE[user_id]['editing'] = 'bio'

async def edit_counselor_specs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start editing counselor specializations"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    from hu_counseling_bot import db, USER_STATE, create_counselor_specialization_keyboard
    counselor = db.get_counselor_by_user_id(user_id)
    
    if user_id not in USER_STATE:
        USER_STATE[user_id] = {}
    
    # Initialize with current specializations
    USER_STATE[user_id]['editing'] = 'specs'
    USER_STATE[user_id]['specializations'] = counselor['specializations'].copy()
    
    selected = USER_STATE[user_id]['specializations']
    
    text = f"""
**Edit Specializations** 📚

**Currently Selected:** {len(selected)}/2

Choose the topics you feel equipped to counsel on. Select 1-2 areas.

💡 *Tip: Only choose areas where you have personal experience or strong biblical knowledge.*

Click the topics to select/deselect:
"""
    
    keyboard = create_counselor_specialization_keyboard(selected)
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')

async def edit_counselor_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start editing counselor gender"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    from hu_counseling_bot import db
    counselor = db.get_counselor_by_user_id(user_id)
    
    current_gender = counselor.get('gender', 'anonymous')
    gender_display = {
        'male': '👨 Male',
        'female': '👩 Female',
        'anonymous': '🔒 Anonymous'
    }.get(current_gender, '🔒 Anonymous')
    
    text = f"""
**Edit Gender** 👤

**Current:** {gender_display}

Select your new gender preference:

**Why we ask:**
• Some topics require gender-specific advice
• Users may have preferences for their counselor
• Helps maintain appropriate boundaries

Choose an option:
"""
    
    keyboard = [
        [InlineKeyboardButton("👨 Male", callback_data='edit_gender_male')],
        [InlineKeyboardButton("👩 Female", callback_data='edit_gender_female')],
        [InlineKeyboardButton("🔒 Prefer not to say (Anonymous)", callback_data='edit_gender_anonymous')],
        [InlineKeyboardButton("◀️ Back", callback_data='counselor_edit_profile')]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def handle_counselor_edit_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle counselor profile edit text inputs"""
    user_id = update.effective_user.id
    
    from hu_counseling_bot import USER_STATE, db
    
    if user_id not in USER_STATE or 'editing' not in USER_STATE[user_id]:
        return
    
    editing = USER_STATE[user_id].get('editing')
    
    if editing == 'name':
        new_name = update.message.text.strip()
        
        if len(new_name) < 2:
            await update.message.reply_text("⚠️ Display name is too short. Please use at least 2 characters.")
            return
        
        if len(new_name) > 50:
            await update.message.reply_text("⚠️ Display name is too long. Please keep it under 50 characters.")
            return
        
        counselor = db.get_counselor_by_user_id(user_id)
        db.update_counselor_info(counselor['counselor_id'], display_name=new_name)
        
        USER_STATE[user_id] = {}
        
        await update.message.reply_text(
            f"✅ **Display Name Updated!**\n\n"
            f"Your new display name is: **{new_name}**\n\n"
            f"This will be shown to users when they rate their session.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ Back to Profile", callback_data='counselor_edit_profile')
            ]])
        )
    
    elif editing == 'bio':
        new_bio = update.message.text.strip()
        
        if len(new_bio) < 50:
            await update.message.reply_text(
                "⚠️ Your bio is too short. Please write at least 50 characters (about 2-3 sentences)."
            )
            return
        
        if len(new_bio) > 500:
            await update.message.reply_text(
                "⚠️ Your bio is too long. Please keep it under 500 characters."
            )
            return
        
        counselor = db.get_counselor_by_user_id(user_id)
        db.update_counselor_info(counselor['counselor_id'], bio=new_bio)
        
        USER_STATE[user_id] = {}
        
        await update.message.reply_text(
            f"✅ **Bio Updated!**\n\n"
            f"Your new bio:\n{new_bio}\n\n"
            f"This will help admins and the matching system understand your expertise.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ Back to Profile", callback_data='counselor_edit_profile')
            ]])
        )

async def toggle_edit_specialization(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle a specialization when editing"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    spec = query.data.replace('spec_', '')
    
    from hu_counseling_bot import USER_STATE, db, create_counselor_specialization_keyboard
    
    if user_id not in USER_STATE or USER_STATE[user_id].get('editing') != 'specs':
        # Not in edit mode, use the regular toggle for registration
        return
    
    if 'specializations' not in USER_STATE[user_id]:
        USER_STATE[user_id]['specializations'] = []
    
    selected = USER_STATE[user_id]['specializations']
    
    if spec == 'done':
        if len(selected) < 1:
            await query.answer("Please select at least 1 area of expertise.", show_alert=True)
            return
        
        # Save the updated specializations
        counselor = db.get_counselor_by_user_id(user_id)
        db.update_counselor_info(counselor['counselor_id'], specializations=selected)
        
        specs_text = '\n'.join([f"• {COUNSELING_TOPICS[s]['icon']} {COUNSELING_TOPICS[s]['name']}" for s in selected])
        
        USER_STATE[user_id] = {}
        
        await query.edit_message_text(
            f"✅ **Specializations Updated!**\n\n"
            f"Your new areas of expertise:\n{specs_text}\n\n"
            f"You'll now receive requests matching these topics.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ Back to Profile", callback_data='counselor_edit_profile')
            ]])
        )
        return
    
    # Toggle selection
    if spec in selected:
        selected.remove(spec)
    else:
        if len(selected) >= 2:
            await query.answer("You can select up to 2 areas maximum.", show_alert=True)
            return
        selected.append(spec)
    
    USER_STATE[user_id]['specializations'] = selected
    
    # Update keyboard
    keyboard = create_counselor_specialization_keyboard(selected)
    text = f"""
**Edit Specializations** 📚

**Selected:** {len(selected)}/2

Choose the topics you feel equipped to counsel on. Select 1-2 areas.

Click the topics to select/deselect:
"""
    
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')

async def edit_gender_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle gender update"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    new_gender = query.data.replace('edit_gender_', '')
    
    from hu_counseling_bot import db
    counselor = db.get_counselor_by_user_id(user_id)
    
    # Update gender in database using the unified method
    db.update_counselor_info(counselor['counselor_id'], gender=new_gender)
    
    gender_display = {
        'male': '👨 Male',
        'female': '👩 Female',
        'anonymous': '🔒 Anonymous'
    }.get(new_gender, '🔒 Anonymous')
    
    await query.edit_message_text(
        f"✅ **Gender Updated!**\n\n"
        f"Your gender is now set to: {gender_display}\n\n"
        f"This helps with appropriate matching and guidance.",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("◀️ Back to Profile", callback_data='counselor_edit_profile')
        ]])
    )


# Export all handler functions
__all__ = [
    'register_counselor_start', 'counselor_select_specialization', 'toggle_specialization',
    'gender_selected', 'handle_counselor_bio', 'counselor_dashboard', 'toggle_availability', 'counselor_stats',
    'handle_counselor_display_name',
    'rate_session_start', 'submit_rating', 'admin_panel', 'admin_pending_counselors',
    'review_counselor', 'approve_counselor_handler', 'reject_counselor_handler',
    'admin_detailed_stats', 'admin_manage_counselors', 'admin_pending_sessions',
    'admin_view_counselor', 'admin_deactivate_counselor', 'admin_reactivate_counselor',
    'admin_delete_counselor', 'admin_edit_counselor',
    'counselor_edit_profile', 'edit_counselor_name', 'edit_counselor_bio', 'edit_counselor_specs',
    'edit_counselor_gender', 'handle_counselor_edit_message', 'toggle_edit_specialization',
    'edit_gender_selected',
    'edit_gender_selected',
    'admin_view_pending_session', 'admin_accept_session_as_counselor',
    'admin_assign_session_start', 'admin_assign_session_confirm'
]
