"""
Dategram Telegram Bot
Daily event updates with images.
Deployable to Railway via GitHub.
"""

import os
import logging
from datetime import time as dt_time, datetime, timezone

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from events import get_upcoming_events, get_events_on, get_next_event
from image_generator import generate_event_card

# ---------- Logging ----------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# ---------- /start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    name = user.first_name or "friend"

    text = (
        f"📅 *Welcome to Dategram, {name}!*\n\n"
        "Your personal event companion — I'll automatically update you "
        "about upcoming events and exactly when they take place.\n\n"
        "*What I do:*\n"
        "• 📆 Daily event updates with visuals\n"
        "• ⏰ Countdown to each event\n"
        "• 🔔 Reminders before the big day\n"
        "• 📋 A clear view of what's coming\n\n"
        "*Tap a button below or use /events to begin.*"
    )

    keyboard = [
        [InlineKeyboardButton("📋 Upcoming Events", callback_data="list_events")],
        [
            InlineKeyboardButton("⏭️ Next Event", callback_data="next_event"),
            InlineKeyboardButton("📅 Today", callback_data="today"),
        ],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)


# ---------- /events ----------
async def events_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    upcoming = get_upcoming_events(limit=8)
    if not upcoming:
        await update.message.reply_text(
            "📭 No upcoming events scheduled right now.\nCheck back soon!",
            parse_mode="Markdown",
        )
        return

    lines = ["📋 *Upcoming Events*\n"]
    for ev in upcoming:
        days = ev["days_left"]
        when = "TODAY" if days == 0 else ("Tomorrow" if days == 1 else f"in {days} days")
        lines.append(f"{ev['emoji']} *{ev['name']}*\n   📆 {ev['date']} · {when}")

    lines.append("\n_Use the buttons below for details._")
    keyboard = [
        [InlineKeyboardButton("⏭️ Next Event", callback_data="next_event")],
        [InlineKeyboardButton("📅 Today", callback_data="today")],
    ]
    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ---------- /today ----------
async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    events_today = get_events_on(0)
    if not events_today:
        await update.message.reply_text(
            "📅 *No events today.*\n\nUse /events to see what's coming up.",
            parse_mode="Markdown",
        )
        return
    for ev in events_today:
        img = generate_event_card(ev)
        caption = (
            f"{ev['emoji']} *{ev['name']}*\n"
            f"📆 {ev['date']} · {ev['time']}\n\n"
            f"{ev['description']}"
        )
        await update.message.reply_photo(photo=img, caption=caption, parse_mode="Markdown")


# ---------- /next ----------
async def next_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ev = get_next_event()
    if not ev:
        await update.message.reply_text("📭 No upcoming events right now.")
        return
    img = generate_event_card(ev)
    caption = (
        f"{ev['emoji']} *{ev['name']}*\n"
        f"📆 {ev['date']} · {ev['time']}\n"
        f"⏳ {ev['days_left']} day(s) left\n\n"
        f"{ev['description']}"
    )
    await update.message.reply_photo(photo=img, caption=caption, parse_mode="Markdown")


# ---------- /about ----------
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "ℹ️ *About Dategram*\n\n"
        "*Your personal event companion.*\n\n"
        "Dategram keeps you updated about upcoming events and when "
        "they're set to take place — automatically, with visuals.\n\n"
        "*Features:*\n"
        "• 📆 Automatic daily event updates\n"
        "• ⏰ Live countdowns\n"
        "• 🖼️ Custom event graphics\n"
        "• 🔔 Timely reminders\n\n"
        "*Bot:* @Dategram001bot\n"
        "*Version:* 1.0.0\n\n"
        "_Stay ahead. Never miss a date._"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# ---------- /help ----------
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "🆘 *Dategram Help*\n\n"
        "*Commands:*\n"
        "/start — Welcome and main menu\n"
        "/events — Browse upcoming events\n"
        "/today — See today's events\n"
        "/next — Jump to the next event\n"
        "/about — Learn about Dategram\n"
        "/help — Show this message\n\n"
        "*Daily Updates:*\n"
        "You'll receive an automatic event update every morning. "
        "Just keep the chat active.\n\n"
        "_Tip: Tap the buttons for quick navigation._"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# ---------- Button callbacks ----------
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "list_events":
        upcoming = get_upcoming_events(limit=8)
        if not upcoming:
            await query.edit_message_text("📭 No upcoming events right now.")
            return
        lines = ["📋 *Upcoming Events*\n"]
        for ev in upcoming:
            days = ev["days_left"]
            when = "TODAY" if days == 0 else ("Tomorrow" if days == 1 else f"in {days} days")
            lines.append(f"{ev['emoji']} *{ev['name']}*\n   📆 {ev['date']} · {when}")
        keyboard = [
            [InlineKeyboardButton("⏭️ Next Event", callback_data="next_event")],
            [InlineKeyboardButton("📅 Today", callback_data="today")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_menu")],
        ]
        await query.edit_message_text(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif data == "next_event":
        ev = get_next_event()
        if not ev:
            await query.edit_message_text("📭 No upcoming events right now.")
            return
        img = generate_event_card(ev)
        caption = (
            f"{ev['emoji']} *{ev['name']}*\n"
            f"📆 {ev['date']} · {ev['time']}\n"
            f"⏳ {ev['days_left']} day(s) left\n\n"
            f"{ev['description']}"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_menu")]]
        await query.message.reply_photo(
            photo=img,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        await query.message.delete()

    elif data == "today":
        events_today = get_events_on(0)
        if not events_today:
            await query.edit_message_text(
                "📅 *No events today.*\n\nUse /events to see what's coming up.",
                parse_mode="Markdown",
            )
            return
        ev = events_today[0]
        img = generate_event_card(ev)
        caption = (
            f"{ev['emoji']} *{ev['name']}*\n"
            f"📆 {ev['date']} · {ev['time']}\n\n"
            f"{ev['description']}"
        )
        await query.message.reply_photo(photo=img, caption=caption, parse_mode="Markdown")
        await query.message.delete()

    elif data == "about":
        text = (
            "ℹ️ *About Dategram*\n\n"
            "*Your personal event companion.*\n\n"
            "Automatic updates about upcoming events with visuals.\n\n"
            "*Bot:* @Dategram001bot\n"
            "*Version:* 1.0.0"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_menu")]]
        await query.edit_message_text(
            text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "back_menu":
        text = (
            "📅 *Dategram Main Menu*\n\n"
            "Choose an option below:"
        )
        keyboard = [
            [InlineKeyboardButton("📋 Upcoming Events", callback_data="list_events")],
            [
                InlineKeyboardButton("⏭️ Next Event", callback_data="next_event"),
                InlineKeyboardButton("📅 Today", callback_data="today"),
            ],
            [InlineKeyboardButton("ℹ️ About", callback_data="about")],
        ]
        await query.edit_message_text(
            text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
        )


# ---------- Unknown command ----------
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "❓ Unknown command. Try /help to see what I can do."
    )


# ---------- Daily broadcast job ----------
async def daily_event_update(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Runs every day at the scheduled hour.
    Sends the next upcoming event to all subscribers.
    """
    subscribers = context.bot_data.get("subscribers", set())
    if not subscribers:
        logger.info("No subscribers yet — skipping daily update.")
        return

    ev = get_next_event()
    if not ev:
        return

    days = ev["days_left"]
    if days == 0:
        when = "🎉 *HAPPENING TODAY!*"
    elif days == 1:
        when = "⏰ *TOMORROW!*"
    else:
        when = f"⏳ *{days} days to go*"

    caption = (
        f"📅 *Daily Event Update*\n\n"
        f"{ev['emoji']} *{ev['name']}*\n"
        f"📆 {ev['date']} · {ev['time']}\n"
        f"{when}\n\n"
        f"{ev['description']}\n\n"
        f"_Stay ahead. Never miss a date._"
    )

    img = generate_event_card(ev)

    for chat_id in list(subscribers):
        try:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=img,
                caption=caption,
                parse_mode="Markdown",
            )
            img.seek(0)  # reset buffer for reuse
        except Exception as e:
            logger.warning(f"Failed to send to {chat_id}: {e}")
            subscribers.discard(chat_id)


# ---------- Track subscribers on /start ----------
async def track_subscriber(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Called via a handler group before /start; adds user to subscribers."""
    subs = context.bot_data.setdefault("subscribers", set())
    subs.add(update.effective_chat.id)


# ---------- Post init ----------
async def post_init(application: Application) -> None:
    # Register commands
    await application.bot.set_my_commands([
        BotCommand("start", "Start Dategram"),
        BotCommand("events", "Browse upcoming events"),
        BotCommand("today", "See today's events"),
        BotCommand("next", "Show the next upcoming event"),
        BotCommand("about", "About Dategram"),
        BotCommand("help", "Show help"),
    ])

    # Schedule daily update at 09:00 UTC
    job_queue = application.job_queue
    job_queue.run_daily(
        daily_event_update,
        time=dt_time(hour=9, minute=0, tzinfo=timezone.utc),
        name="daily_event_update",
    )
    logger.info("Daily update scheduled at 09:00 UTC")


# ---------- Main ----------
def main() -> None:
    if not BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required.")

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Subscriber tracking (runs before /start handler)
    app.add_handler(MessageHandler(filters.ALL, track_subscriber), group=-1)

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("events", events_command))
    app.add_handler(CommandHandler("today", today_command))
    app.add_handler(CommandHandler("next", next_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("help", help_command))

    # Buttons
    app.add_handler(CallbackQueryHandler(button_callback))

    # Unknown commands
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    logger.info("Starting Dategram bot…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
