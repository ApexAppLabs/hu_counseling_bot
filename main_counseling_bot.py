"""
Main entry point for HU Counseling Service Bot
Combines all modules and starts the bot
"""

import logging
import asyncio
import os
from telegram import BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# Import production-ready modules
from logging_config import setup_logging
from session_timeout import SessionTimeoutManager
from backup_database import backup_database

# Import bot modules
from hu_counseling_bot import (
    start, help_command, about_command,
    request_counseling, topic_selected, user_gender_selected, handle_description, skip_description,
    accept_session, decline_session, handle_session_message,
    end_session_handler, confirm_end_session,
    session_info_handler, current_session_handler, transfer_session_handler, confirm_transfer_handler,
    BOT_TOKEN, db, matcher, create_main_menu_keyboard, create_session_control_keyboard,
    ADMIN_IDS
)

from hu_counseling_bot_part2 import (
    register_counselor_start, counselor_select_specialization, toggle_specialization,
    gender_selected, handle_counselor_bio, counselor_dashboard, toggle_availability, counselor_stats,
    rate_session_start, submit_rating, admin_panel, admin_pending_counselors,
    review_counselor, approve_counselor_handler, reject_counselor_handler,
    admin_detailed_stats, admin_manage_counselors, admin_pending_sessions,
    admin_view_counselor, admin_deactivate_counselor, admin_reactivate_counselor,
    admin_ban_counselor, admin_edit_counselor
)

# Setup comprehensive logging with file rotation
setup_logging(log_level=logging.INFO)
logger = logging.getLogger(__name__)

async def main_menu_handler(update, context):
    """Handle main menu callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Check counselor status
    counselor = db.get_counselor_by_user_id(user_id)
    is_counselor = counselor and counselor['status'] == 'approved'
    
    # Check admin status
    is_admin = db.is_admin(user_id) or user_id in ADMIN_IDS
    
    text = """
**HU Counseling Service** 🙏

Anonymous counseling for students in the gospel fellowship.

What would you like to do?
"""
    
    keyboard = create_main_menu_keyboard(is_counselor, is_admin)
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')

async def menu_command(update, context):
    """Handle /menu command - shows main menu"""
    user_id = update.effective_user.id
    
    # Check counselor status
    counselor = db.get_counselor_by_user_id(user_id)
    is_counselor = counselor and counselor['status'] == 'approved'
    
    # Check admin status
    is_admin = db.is_admin(user_id) or user_id in ADMIN_IDS
    
    text = """
**HU Counseling Service** 🙏

Anonymous counseling for students in the gospel fellowship.

What would you like to do?
"""
    
    keyboard = create_main_menu_keyboard(is_counselor, is_admin)
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')

async def cancel_end_handler(update, context):
    """Cancel end session"""
    query = update.callback_query
    await query.answer("Continuing session")
    
    user_id = query.from_user.id
    
    # Check if user or counselor
    is_counselor = False
    counselor = db.get_counselor_by_user_id(user_id)
    if counselor and counselor.get('status') == 'approved':
        is_counselor = True
    
    await query.edit_message_text(
        "✅ **Session Continues**\n\nType your message below to continue the conversation:",
        reply_markup=create_session_control_keyboard(is_user=not is_counselor),
        parse_mode='Markdown'
    )

async def post_init(application):
    """Post initialization - Set up bot commands menu and background tasks"""
    bot_commands = [
        BotCommand("start", "🏠 Start the bot / Main menu"),
        BotCommand("menu", "📋 Show main menu"),
        BotCommand("help", "❓ Get help and information"),
        BotCommand("about", "ℹ️ About HU Counseling Service")
    ]
    await application.bot.set_my_commands(bot_commands)
    logger.info("✅ Bot commands menu configured")
    
    # Create initial database backup
    try:
        backup_database(db.db_path)
        logger.info("✅ Initial database backup created")
    except Exception as e:
        logger.warning(f"Initial backup failed: {e}")
    
    # Start session timeout manager
    timeout_manager = SessionTimeoutManager(
        db=db,
        bot_context=application,
        timeout_hours=24
    )
    application.bot_data['timeout_manager'] = timeout_manager
    asyncio.create_task(timeout_manager.start())
    logger.info("✅ Session timeout manager started")
    
    # Start scheduled tasks manager
    from scheduled_tasks import ScheduledTasksManager
    scheduled_tasks_manager = ScheduledTasksManager(db)
    application.bot_data['scheduled_tasks_manager'] = scheduled_tasks_manager
    asyncio.create_task(scheduled_tasks_manager.start())
    logger.info("✅ Scheduled tasks manager started")
    
    # Start health ping service (only in Render environment)
    import os
    if os.getenv("RENDER") == "true":  # Render sets this automatically
        from health_ping import HealthPingService
        health_ping_service = HealthPingService(ping_interval_minutes=int(os.getenv("HEALTH_PING_INTERVAL", "10")))
        application.bot_data['health_ping_service'] = health_ping_service
        asyncio.create_task(health_ping_service.start())
        logger.info("✅ Health ping service started")

async def post_shutdown(application):
    """Post shutdown - Clean up background tasks"""
    logger.info("Shutting down background services...")
    
    # Stop health ping service
    if 'health_ping_service' in application.bot_data:
        await application.bot_data['health_ping_service'].stop()
    
    # Stop scheduled tasks manager
    if 'scheduled_tasks_manager' in application.bot_data:
        await application.bot_data['scheduled_tasks_manager'].stop()
    
    # Stop session timeout manager
    if 'timeout_manager' in application.bot_data:
        await application.bot_data['timeout_manager'].stop()
    
    logger.info("All background services stopped")

def main():
    """Start the bot"""
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found in environment variables!")
        logger.error("Please create a .env file with BOT_TOKEN=your_bot_token")
        return
    
    # Import ADMIN_IDS from hu_counseling_bot to validate
    from hu_counseling_bot import ADMIN_IDS
    if not ADMIN_IDS:
        logger.error("❌ ADMIN_IDS not found or empty in environment variables!")
        logger.error("Please set ADMIN_IDS in .env file (e.g., ADMIN_IDS=123456789)")
        logger.error("Without ADMIN_IDS, the admin panel will NOT work!")
        return
    
    logger.info(f"✅ Admin IDs configured: {ADMIN_IDS}")
    
    # Build application
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).post_shutdown(post_shutdown).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    
    # Callback query handlers
    app.add_handler(CallbackQueryHandler(main_menu_handler, pattern='^main_menu$'))
    app.add_handler(CallbackQueryHandler(help_command, pattern='^help$'))
    app.add_handler(CallbackQueryHandler(about_command, pattern='^about$'))
    
    # Counseling request flow
    app.add_handler(CallbackQueryHandler(request_counseling, pattern='^request_counseling$'))
    app.add_handler(CallbackQueryHandler(topic_selected, pattern='^topic_'))
    app.add_handler(CallbackQueryHandler(user_gender_selected, pattern='^user_gender_'))
    app.add_handler(CallbackQueryHandler(skip_description, pattern='^skip_description$'))
    
    # Session management
    app.add_handler(CallbackQueryHandler(accept_session, pattern='^accept_session_'))
    app.add_handler(CallbackQueryHandler(decline_session, pattern='^decline_session_'))
    app.add_handler(CallbackQueryHandler(end_session_handler, pattern='^end_session$'))
    app.add_handler(CallbackQueryHandler(confirm_end_session, pattern='^confirm_end_'))
    app.add_handler(CallbackQueryHandler(cancel_end_handler, pattern='^cancel_end$'))
    app.add_handler(CallbackQueryHandler(session_info_handler, pattern='^session_info$'))
    app.add_handler(CallbackQueryHandler(current_session_handler, pattern='^current_session$'))
    app.add_handler(CallbackQueryHandler(transfer_session_handler, pattern='^transfer_session$'))
    app.add_handler(CallbackQueryHandler(confirm_transfer_handler, pattern='^confirm_transfer_'))
    
    # Counselor registration
    app.add_handler(CallbackQueryHandler(register_counselor_start, pattern='^register_counselor$'))
    app.add_handler(CallbackQueryHandler(counselor_select_specialization, pattern='^counselor_select_spec$'))
    app.add_handler(CallbackQueryHandler(toggle_specialization, pattern='^spec_'))
    app.add_handler(CallbackQueryHandler(gender_selected, pattern='^gender_'))
    
    # Counselor dashboard
    app.add_handler(CallbackQueryHandler(counselor_dashboard, pattern='^counselor_dashboard$'))
    app.add_handler(CallbackQueryHandler(toggle_availability, pattern='^toggle_availability$'))
    app.add_handler(CallbackQueryHandler(counselor_stats, pattern='^counselor_stats$'))
    
    # Rating system
    app.add_handler(CallbackQueryHandler(rate_session_start, pattern='^rate_session_'))
    app.add_handler(CallbackQueryHandler(submit_rating, pattern='^rating_'))
    
    # Admin panel
    app.add_handler(CallbackQueryHandler(admin_panel, pattern='^admin_panel$'))
    app.add_handler(CallbackQueryHandler(admin_pending_counselors, pattern='^admin_pending_counselors$'))
    app.add_handler(CallbackQueryHandler(review_counselor, pattern='^review_counselor_'))
    app.add_handler(CallbackQueryHandler(approve_counselor_handler, pattern='^approve_counselor_'))
    app.add_handler(CallbackQueryHandler(reject_counselor_handler, pattern='^reject_counselor_'))
    app.add_handler(CallbackQueryHandler(admin_detailed_stats, pattern='^admin_detailed_stats$'))
    app.add_handler(CallbackQueryHandler(admin_manage_counselors, pattern='^admin_manage_counselors$'))
    app.add_handler(CallbackQueryHandler(admin_pending_sessions, pattern='^admin_pending_sessions$'))
    
    # Admin counselor management
    app.add_handler(CallbackQueryHandler(admin_view_counselor, pattern='^admin_view_counselor_'))
    app.add_handler(CallbackQueryHandler(admin_deactivate_counselor, pattern='^admin_deactivate_'))
    app.add_handler(CallbackQueryHandler(admin_reactivate_counselor, pattern='^admin_reactivate_'))
    app.add_handler(CallbackQueryHandler(admin_ban_counselor, pattern='^admin_ban_'))
    app.add_handler(CallbackQueryHandler(admin_edit_counselor, pattern='^admin_edit_'))
    
    # Message handlers (for descriptions and session messages)
    async def text_message_handler(update, context):
        """Route text messages to appropriate handlers"""
        user_id = update.effective_user.id
        
        # Import USER_STATE
        from hu_counseling_bot import USER_STATE
        
        # Check if awaiting bio
        if user_id in USER_STATE and USER_STATE[user_id].get('awaiting_bio'):
            await handle_counselor_bio(update, context)
            return
        
        # Check if awaiting description
        if user_id in USER_STATE and USER_STATE[user_id].get('awaiting_description'):
            await handle_description(update, context)
            return
        
        # Otherwise, treat as session message
        await handle_session_message(update, context)
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))
    
    # Start bot
    logger.info("🚀 HU Counseling Service Bot is starting...")
    logger.info(f"📊 Database: {db.db_path}")

    use_webhook = os.getenv("USE_WEBHOOK", "false").lower() == "true"

    if use_webhook:
        # Webhook configuration for public deployment (e.g., Render)
        base_url = os.getenv("WEBHOOK_BASE_URL")
        port = int(os.getenv("PORT", "5000"))
        url_path = os.getenv("WEBHOOK_PATH", BOT_TOKEN)

        if not base_url:
            logger.error("❌ WEBHOOK_BASE_URL not set but USE_WEBHOOK=true. Falling back to polling.")
            use_webhook = False
        else:
            base_url = base_url.rstrip("/")
            webhook_url = f"{base_url}/{url_path}"

            logger.info("🌐 Starting in WEBHOOK mode")
            logger.info(f"🔗 Webhook URL: {webhook_url}")
            logger.info(f"🔌 Listening on 0.0.0.0:{port}, url_path='{url_path}'")

            app.run_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=url_path,
                webhook_url=webhook_url,
            )
            return

    # Default: polling mode (for local development or when webhook not configured)
    logger.info("📡 Starting in POLLING mode")
    logger.info("✅ Ready to serve!")

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    app.run_polling(stop_signals=None)

# Add a new function that can be called without starting the bot immediately
def initialize_bot():
    """Initialize bot without starting it - for use with web service wrapper"""
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found in environment variables!")
        logger.error("Please create a .env file with BOT_TOKEN=your_bot_token")
        return None
    
    # Import ADMIN_IDS from hu_counseling_bot to validate
    from hu_counseling_bot import ADMIN_IDS
    if not ADMIN_IDS:
        logger.error("❌ ADMIN_IDS not found or empty in environment variables!")
        logger.error("Please set ADMIN_IDS in .env file (e.g., ADMIN_IDS=123456789)")
        logger.error("Without ADMIN_IDS, the admin panel will NOT work!")
        return None
    
    logger.info(f"✅ Admin IDs configured: {ADMIN_IDS}")
    
    # Build application
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    
    # NOTE: Handlers are NOT added here to avoid duplication
    # The render_web_service imports and runs the full bot which includes handlers
    
    logger.info("Bot initialized successfully (handlers managed by main application)")
    return app

if __name__ == '__main__':
    main()
