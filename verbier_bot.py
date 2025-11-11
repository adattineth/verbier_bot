from playwright.sync_api import sync_playwright
import time
import smtp    if sold_out_locator.count() > 0:
        # print everything we find
        slots = page.locator(".selection__item").all_inner_texts()
        print("⏱️ Sold out, slots found:", [s.strip() for s in slots])
        return False   # sold out
    else:
        print("✅ No 'Epuisé' in the modal")
        return True    # availablem email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

URL = "https://verbier4vallees.ch/fr/shop-en-ligne/activites/opening-session_activity_410650"

# =============== EMAIL CONFIG ===============
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "terzuoli11@gmail.com"         # <-- put your email here
SMTP_PASS = "dljx zirk myip fbbk".replace(" ", "")     # <-- put your app password here
EMAIL_TO   = ["gerry.sergi@gmail.com", "terzuoli11@gmail.com"]       # recipient (can be the same)
# ============================================


def send_email_available():
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = ", ".join(EMAIL_TO)
    msg["Subject"] = "Verbier tickets: AVAILABLE"
    body = (
        "It seems that tickets are no longer marked as 'Épuisé'.\n"
        f"Check here: {URL}"
    )
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    print("📧 Email sent.")


def check_once(page):
    # --- main page ---
    page.goto(URL, timeout=60000)
    page.wait_for_load_state("domcontentloaded")

    # cookies
    try:
        for txt in ["Tout accepter", "Accepter tout", "Accepter"]:
            btn = page.locator(f"button:has-text('{txt}')")
            if btn.count() > 0 and btn.first.is_visible():
                btn.first.click()
                break
    except Exception:
        pass

    # button
    buy_btn = page.locator(
        "button.js-activity-ticket-config__open.d-md-grid:has-text('Acheter maintenant')"
    )
    if buy_btn.count() == 0:
        buy_btn = page.locator(
            "button.js-activity-ticket-config__open:has-text('Acheter maintenant')"
        )
    if buy_btn.count() == 0:
        print("⚠️ Button not found")
        return None  # unknown status

    buy_btn.first.scroll_into_view_if_needed()
    time.sleep(0.5)
    buy_btn.first.click()

    # wait for modal
    page.wait_for_selector(".ticket-configuration", timeout=15000)
    time.sleep(1)

    # look for 'Epuisé'
    sold_out_locator = page.locator(".ticket-configuration__availability:has-text('Epuisé')")
    if sold_out_locator.count() > 0:
        # tutto quello che c’è lo stampiamo
        slots = page.locator(".selection__item").all_inner_texts()
        print("⏱️ esauriti, slot trovati:", [s.strip() for s in slots])
        return False   # esauriti
    else:
        print("✅ non c’è 'Epuisé' nella modale")
        return True    # disponibili


def monitor(interval_seconds=300):
    """Check every interval_seconds. When available tickets are found, send email and stop."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        while True:
            try:
                status = check_once(page)
            except Exception as e:
                print("❗ Error during check:", e)
                status = None

            if status is True:
                # found available → email → stop
                send_email_available()
                break

            # otherwise wait and retry
            time.sleep(interval_seconds)

        browser.close()


if __name__ == "__main__":
    # check every 100 seconds
    monitor(interval_seconds=100)
