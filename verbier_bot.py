from playwright.sync_api import sync_playwright
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

URL = "https://verbier4vallees.ch/fr/shop-en-ligne/activites/opening-session_activity_410650"


# =============== CONFIG EMAIL ===============
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.environ["SMTP_USER"]        # your Gmail address
SMTP_PASS = os.environ["SMTP_PASS"]
EMAIL_TO   = ["gerry.sergi@gmail.com", "terzuoli11@gmail.com","alicepotter02@gmail.com","francesco.stsup@gmail.com","antonblaise@gmail.com","maxime.barre@epfl.ch","arthur.dattin@gmail.com","noe.nomblot@epfl.ch"]       # destinatario (può essere uguale)
# ============================================


def send_email_available():
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = ", ".join(EMAIL_TO)
    msg["Subject"] = "Verbier tickets: AVAILABLE"
    body = (
    "ALERT \n\n"
    "Verbier tickets are BACK! \n"
    "Stop whatever you’re doing\n"
    "Powder waits for no one ❄️⛷️\n\n"
    f"👉 Get them before they vanish: {URL}\n\n"
    "–––––––––––––––––––––––––––––––––––––––––––\n"
    "🇮🇹 *Versione italiana:*\n"
    " ALLERTA \n\n"
    "I biglietti per Verbier sono TORNATI! \n"
    "Lascia tutto ! \n"
    "La neve non aspetta nessuno ⛷️💨\n\n"
    f"👉 Prendili subito: {URL}\n"
)

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    print("Email inviata.")


def check_once(page):
    # --- pagina principale ---
    page.goto(URL, timeout=60000)
    page.wait_for_load_state("domcontentloaded")

    # cookie
    try:
        for txt in ["Tout accepter", "Accepter tout", "Accepter"]:
            btn = page.locator(f"button:has-text('{txt}')")
            if btn.count() > 0 and btn.first.is_visible():
                btn.first.click()
                break
    except Exception:
        pass

    # bottone
    buy_btn = page.locator(
        "button.js-activity-ticket-config__open.d-md-grid:has-text('Acheter maintenant')"
    )
    if buy_btn.count() == 0:
        buy_btn = page.locator(
            "button.js-activity-ticket-config__open:has-text('Acheter maintenant')"
        )
    if buy_btn.count() == 0:
        print("bottone non trovato")
        return None  # stato sconosciuto

    buy_btn.first.scroll_into_view_if_needed()
    time.sleep(0.5)
    buy_btn.first.click()

    # aspetta modale
    page.wait_for_selector(".ticket-configuration", timeout=15000)
    time.sleep(1)

    # cerca 'Epuisé'
    sold_out_locator = page.locator(".ticket-configuration__availability:has-text('Epuisé')")
    if sold_out_locator.count() > 0:
        # tutto quello che c’è lo stampiamo
        slots = page.locator(".selection__item").all_inner_texts()
        print("esauriti, slot trovati:", [s.strip() for s in slots])
        return False   # esauriti
    else:
        print("non c’è 'Epuisé' nella modale")
        return True    # disponibili


def monitor(interval_seconds=300):
    """Controlla ogni interval_seconds. Quando trova disponibile, manda mail e si ferma."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        while True:
            try:
                status = check_once(page)
            except Exception as e:
                print("❗ errore durante il check:", e)
                status = None

            if status is True:
                # trovato disponibile → email → stop
                send_email_available()
                break

            # altrimenti aspetta e riprova
            time.sleep(interval_seconds)

        browser.close()


if __name__ == "__main__":
    # controlla ogni 5 minuti (300 s).
    monitor(interval_seconds=100)