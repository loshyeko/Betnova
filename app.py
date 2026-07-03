from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from translations import translations
from database import get_connection, get_match, get_matches,create_user, get_user, get_all_matches, get_markets, save_bet, update_balance, get_balance
from auth import hash_password, verify_password

app = Flask(__name__)

def get_text():

    language = session.get("language", "en")

    return translations.get(language, translations["en"])

@app.context_processor
def inject_translations():
    lang = session.get("language", "en")
    return {
        "t": translations.get(lang, translations["en"])
    }
app.secret_key = "Dean234@devlin123Gee2025"

def get_currency(country):

    currencies = {
        "254": "KSh",
        "243": "FC",
        "256": "UGX",
        "255": "TZS",
        "257": "BIF",
        "250": "RWF"
    }

    return currencies.get(str(country), "USD")

def format_balance(amount):
    return "{:,.2f}".format(float(amount))

@app.route("/")
def home():
    return redirect("/login")

@app.route("/dashboard")
def dashboard():

    phone = session.get("phone")
    country = session.get("country")

    if not phone:
        return redirect("/login")

    user = get_user(phone)

    if not user:
        session.clear()
        return redirect("/login")

    matches = get_matches()

    if country == "254":
        currency = "KSh"
    elif country == "255":
        currency = "TZS"
    elif country == "256":
        currency = "UGX"
    elif country == "243":
        currency = "CDF"
    else:
        currency = "USD"

    return render_template(
        "dashboard.html",
        matches=matches,
        phone=phone,
        country=country,
        balance=format_balance(user[4]),
        currency=currency
    )

@app.route("/match/<int:match_id>")
def match_details(match_id):

    phone = session.get("phone")

    if not phone:
        return redirect("/login")

    match = get_match(match_id)
    markets = get_markets(match_id)

    if not match:
        return "Match not found."

    return render_template(
        "match_details.html",
        match=match,
        markets=markets
    )

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        country = request.form["country"]
        phone = request.form["phone"]
        phone = phone.lstrip("0")
        full_phone = country + phone

        password = request.form["password"]

        user = get_user(full_phone)

        if user and verify_password(password, user[3]):

            session["phone"] = user[2]
            session["country"] = user[0]
            print("SESSION COUNTRY =",
                  session["country"])
            print("USER =", user)
            session["language"] = user[1]

            return redirect("/dashboard")

        return "Invalid phone number or password."

    return render_template("login.html",
                           text=get_text()
    )

@app.route("/set_language/<lang>")
def set_language(lang):

    if lang not in translations:
        lang = "en"

    session["language"] = lang

    return redirect(request.referrer or url_for("dashboard"))

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        country = request.form["country"]
        language = request.form["language"]
        phone = request.form["phone"]
        phone = phone.lstrip("0")
        full_phone = country + phone
        password = request.form["password"]

        hashed_password = hash_password(password)

        success = create_user(
            country,
            language,
            full_phone,
            hashed_password
        )

        if success:
            return redirect("/login")

        return render_template(
            "register.html",
            error="This phone number is already registered."
        )

    return render_template("register.html")
@app.route("/place_bet", methods=["POST"])
def place_bet():

    phone = session.get("phone")

    if not phone:
        return jsonify({
            "success": False,
            "message": "Please login first."
        })

    data = request.get_json()

    stake = float(data["stake"])
    balance = get_balance(phone)

    if stake <= 0:
        return jsonify({
            "success": False,
            "message": "Invalid stake."
        })

    if stake > balance:
        return jsonify({
            "success": False,
            "message": "Insufficient balance."
        })

    save_bet(
        phone=phone,
        match_id=data["match_id"],
        selection=data["selection"],
        odds=data["odds"],
        stake=stake,
        potential_win=data["potential_win"]
    )

    update_balance(phone, stake)

    new_balance = get_balance(phone)

    return jsonify({
        "success": True,
        "message": "Bet placed successfully.",
        "balance": new_balance
    })
 

@app.route("/betslip")
def betslip():

    phone = session.get("phone")

    if not phone:
        return redirect("/login")

    user = get_user(phone)
    currency = get_currency(user[0])

    return render_template(
        "betslip.html",
        currency=currency
    )


@app.route("/account")
def account():

    phone = session.get("phone")

    if not phone:
        return redirect("/login")

    user = get_user(phone)
    currency = get_currency(user[0])

    return render_template(
        "account.html",
        phone=user[2],
        balance=user[4],
        currency=currency
    )

@app.route("/deposit")
def deposit():

    phone = session.get("phone")

    if not phone:
        return redirect("/login")

    user = get_user(phone)
    currency = get_currency(user[0])

    return render_template(
        "deposit.html",
        balance=user[4],
        currency=currency,
        phone=user[2]
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@app.route("/matches")
def matches():

    phone = session.get("phone")

    if not phone:
        return redirect("/login")

    sport = request.args.get("sport")
    league = request.args.get("league")

    matches = get_all_matches()

    if sport:
        matches = [m for m in matches if m[9] == sport]

    if league:
        matches = [m for m in matches if m[1] == league]

    return render_template(
        "matches.html",
        matches=matches
    )

@app.route("/my_bets")
def my_bets():

    phone = session.get("phone")

    if not phone:
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            match_id,
            selection,
            odds,
            stake,
            potential_win,
            status,
            placed_at
        FROM bets
        WHERE phone = %s
        ORDER BY placed_at DESC
    """, (phone,))

    bets = cur.fetchall()

    cur.close()
    conn.close()

    user = get_user(phone)
    currency = get_currency(user[0])

    return render_template(
        "my_bets.html",
        bets=bets,
        currency=currency
    )

@app.route("/live")
def live():

    phone = session.get("phone")

    if not phone:
        return redirect("/login")

    return render_template("live.html")

@app.route("/promotions")
def promotions():

    phone = session.get("phone")

    if not phone:
        return redirect("/login")

    return render_template("promotions.html")

@app.route("/casino")
def casino():

    phone = session.get("phone")

    if not phone:
        return redirect("/login")

    return render_template("casino.html")

@app.route("/aviator")
def aviator():

    phone = session.get("phone")

    if not phone:
        return redirect("/login")

    return render_template("aviator.html")

@app.route("/slots")
def slots():
    return render_template("slots.html")

@app.route("/blackjack")
def blackjack():
    return render_template("blackjack.html")

@app.route("/roulette")
def roulette():
    return render_template("roulette.html")

@app.route("/baccarat")
def baccarat():
    return render_template("baccarat.html")

@app.route("/poker")
def poker():
    return render_template("poker.html")

@app.route("/dice")
def dice():
    return render_template("dice.html")

@app.route("/crash")
def crash():
    return render_template("crash.html")    

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)