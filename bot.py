import os
import random
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")


def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("📧 Email Name", callback_data="email"),
            InlineKeyboardButton("👤 Username", callback_data="username"),
        ],
        [
            InlineKeyboardButton("💼 Business Name", callback_data="business"),
            InlineKeyboardButton("✨ Random Name", callback_data="random"),
        ],
        [
            InlineKeyboardButton("💡 Creative Idea", callback_data="idea"),
        ],
        [
            InlineKeyboardButton("ℹ️ Help", callback_data="help"),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


WELCOME = """🚀 *Welcome to Generation Bot!*

Your smart assistant for creating:

📧 Email names
👤 Usernames
💼 Business names
✨ Random names
💡 Creative ideas

Fast, simple and easy to use.

Choose an option below 👇
"""


def unique(items):
    result = []

    for item in items:
        if item not in result:
            result.append(item)

    return result[:8]


def email_names(text):
    words = text.lower().split()

    if not words:
        words = ["user"]

    first = words[0]
    last = words[-1]
    base = "".join(words)

    results = [
        f"{first}.{last}",
        base,
        f"{first}{random.randint(10, 99)}",
        f"{base}{random.randint(100, 999)}",
        f"official{base}",
        f"the{base}",
        f"{first}.{last}{random.randint(1, 99)}",
        f"{base}.official",
    ]

    return unique(results)


def usernames(text):
    clean = "".join(
        character.lower()
        for character in text
        if character.isalnum() or character == " "
    )

    clean = clean.replace(" ", "")

    if not clean:
        clean = "user"

    suffixes = [
        "hub",
        "x",
        "official",
        "hq",
        "pro",
        "zone",
        "world",
    ]

    results = [
        clean,
        f"{clean}{random.randint(10, 99)}",
        f"the{clean}",
        f"{clean}_{random.randint(10, 999)}",
        f"{clean}{random.choice(suffixes)}",
        f"{random.choice(suffixes)}{clean}",
        f"{clean}_official",
        f"{clean}x",
    ]

    return unique(results)


def business_names(text):
    topic = text.strip().title()

    if not topic:
        topic = "Nova"

    prefixes = [
        "Nova",
        "Prime",
        "Bright",
        "Next",
        "Urban",
        "Swift",
        "Elite",
        "Vertex",
    ]

    suffixes = [
        "Labs",
        "Hub",
        "Works",
        "Studio",
        "Solutions",
        "Group",
        "Ventures",
    ]

    results = [
        f"{topic} {random.choice(suffixes)}",
        f"{random.choice(prefixes)} {topic}",
        f"{topic} Ventures",
        f"{topic} Solutions",
        f"Next {topic}",
        f"{topic} Studio",
        f"{random.choice(prefixes)} {random.choice(suffixes)}",
        f"{topic} Hub",
    ]

    return unique(results)


def random_names():
    first_names = [
        "Alex",
        "Jordan",
        "Taylor",
        "Morgan",
        "Riley",
        "Cameron",
        "Avery",
        "Drew",
    ]

    last_names = [
        "Stone",
        "Carter",
        "Brooks",
        "Hayes",
        "Parker",
        "Reed",
        "Mason",
        "Blake",
    ]

    results = []

    for _ in range(8):
        results.append(
            f"{random.choice(first_names)} "
            f"{random.choice(last_names)}"
        )

    return unique(results)


def creative_ideas(text):
    topic = text.strip()

    if not topic:
        topic = "a new project"

    results = [
        f"Create a simple brand around {topic}.",
        f"Build a social media page focused on {topic}.",
        f"Create a service that makes {topic} easier.",
        f"Start a community for people interested in {topic}.",
        f"Turn {topic} into a useful web or mobile tool.",
        f"Create a challenge or campaign around {topic}.",
        f"Make a beginner-friendly guide about {topic}.",
        f"Create a marketplace related to {topic}.",
    ]

    return unique(results)


def format_results(title, results):
    message = f"{title}\n\n"

    for number, result in enumerate(results, 1):
        message += f"{number}. {result}\n"

    message += "\n🔄 Send another word or topic for more ideas."

    return message


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        WELCOME,
        parse_mode="Markdown",
        reply_markup=main_menu(),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """ℹ️ *How Generation Bot Works*

1️⃣ Choose a generator.
2️⃣ Send a name, word or topic.
3️⃣ Get multiple suggestions instantly.
4️⃣ Send another request whenever you want fresh ideas.

Have fun! 🚀"""

    await update.message.reply_text(
        help_text,
        parse_mode="Markdown",
        reply_markup=main_menu(),
    )


async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    await query.answer()

    option = query.data

    if option == "help":
        await query.edit_message_text(
            "ℹ️ Choose a generator below and send me a name, word or topic.",
            reply_markup=main_menu(),
        )
        return

    prompts = {
        "email": "📧 *Email Name Generator*\n\nSend me a name or words.",
        "username": "👤 *Username Generator*\n\nSend me a name, word or topic.",
        "business": "💼 *Business Name Generator*\n\nSend me a business topic or keyword.",
        "random": "✨ *Random Name Generator*\n\nSend any word or topic.",
        "idea": "💡 *Creative Idea Generator*\n\nSend me a topic, niche or keyword.",
    }

    context.user_data["mode"] = option

    await query.edit_message_text(
        prompts[option],
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⬅️ Back to Menu",
                        callback_data="back",
                    )
                ]
            ]
        ),
    )


async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    mode = context.user_data.get("mode")

    if not mode:
        await update.message.reply_text(
            "Please choose a generator first 👇",
            reply_markup=main_menu(),
        )
        return

    if mode == "email":
        results = email_names(text)
        title = "📧 Email Name Ideas"

    elif mode == "username":
        results = usernames(text)
        title = "👤 Username Ideas"

    elif mode == "business":
        results = business_names(text)
        title = "💼 Business Name Ideas"

    elif mode == "random":
        results = random_names()
        title = "✨ Random Name Ideas"

    else:
        results = creative_ideas(text)
        title = "💡 Creative Ideas"

    await update.message.reply_text(
        format_results(title, results),
        reply_markup=main_menu(),
    )


async def callback_router(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    if query.data == "back":
        await query.answer()

        context.user_data.clear()

        await query.edit_message_text(
            WELCOME,
            parse_mode="Markdown",
            reply_markup=main_menu(),
        )

    else:
        await button_handler(update, context)


def main():
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN environment variable is missing."
        )

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("help", help_command)
    )

    application.add_handler(
        CallbackQueryHandler(callback_router)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler,
        )
    )

    print("🚀 Generation Bot is running...")

    application.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
