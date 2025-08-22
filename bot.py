import os, re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.environ["BOT_TOKEN"]
AFFILIATE_TAG = os.environ.get("AFFILIATE_TAG", "dailyfreshd03-21")

AMAZON_DOMAINS = (
    "amazon.in", "www.amazon.in",
    "amazon.com", "www.amazon.com",
    "amazon.ae", "www.amazon.ae",
    "amazon.co.uk", "www.amazon.co.uk",
)

URL_REGEX = re.compile(r"(https?://[^\s]+)")

def convert_amazon_url(u: str) -> str | None:
    """Return affiliate version of an Amazon URL (or None if not convertible)."""
    try:
        p = urlparse(u)
        if p.netloc.lower() not in AMAZON_DOMAINS:
            return None
        q = parse_qs(p.query)
        q["tag"] = [AFFILIATE_TAG]  # set/replace tag
        new_query = urlencode(q, doseq=True)
        new_url = urlunparse((p.scheme, p.netloc, p.path, p.params, new_query, p.fragment))
        return new_url
    except Exception:
        return None

async def handle_any(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    text = (msg.text or msg.caption or "").strip()
    if not text:
        return

    urls = URL_REGEX.findall(text)
    converted = []

    for u in urls:
        # skip amzn.to shorteners (cannot append tag there)
        if "amzn.to" in u:
            continue
        new_u = convert_amazon_url(u)
        if new_u:
            converted.append(new_u)

    if converted:
        reply = "✅ *Converted Link(s):*\n" + "\n".join(converted) + \
                "\n\nℹ️ Tip: amzn.to short links auto-convert nahi hote. Product page link bhejo."
        await msg.reply_text(reply, parse_mode="Markdown")
    else:
        # optional gentle hint
        if any("amzn.to" in u for u in urls):
            await msg.reply_text("ℹ️ amzn.to short links convert nahi hote. Product page link bhejo.")
        # else: keep quiet

if name == "main":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    # messages (DM / groups) + channel posts (when bot is admin)
    app.add_handler(MessageHandler(filters.ALL, handle_any))
    app.run_polling(allowed_updates=None)
