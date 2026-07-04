from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from translations import translations
from database import get_connection, get_match, get_matches,create_user, get_user, get_all_matches, get_markets, save_bet, update_balance, get_balance, save_deposit, deposit_exists
from auth import hash_password, verify_password
from werkzeug.security import check_password_hash
import requests
import uuid

PESAPAL_CONSUMER_KEY = "mBtHTkpEO3JtHyDJr33oi+jLaHK5ZTvH"
PESAPAL_CONSUMER_SECRET = "0tjx3NbCqQAOFBpyXEPC/+5BOhY="
PESAPAL_IPN_ID = "983a6f54-b3ba-4965-8392-da61843d4435"

PESAPAL_BASE_URL = "https://pay.pesapal.com/v3"

def get_pesapal_token():
    url = f"{PESAPAL_BASE_URL}/api/Auth/RequestToken"

    payload = {
        "consumer_key": PESAPAL_CONSUMER_KEY,
        "consumer_secret": PESAPAL_CONSUMER_SECRET
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()

    return response.json()["token"]

app = Flask(__name__)

@app.route("/pesapal/list-ipns")
def list_ipns():
    token = get_pesapal_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(
        "https://pay.pesapal.com/v3/api/URLSetup/GetIpnList",
        headers=headers
    )

    return response.text

def get_balance(phone):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT balance FROM users WHERE phone = %s",
        (phone,)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row:
        return float(row[0])

    return 0.0

def update_balance(phone, new_balance):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE users
        SET balance = %s
        WHERE phone = %s
        """,
        (new_balance, phone)
    )

    conn.commit()
    cur.close()
    conn.close()

def save_deposit(phone, merchant_reference, order_tracking_id, amount, payment_status):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO deposits (
            phone,
            merchant_reference,
            order_tracking_id,
            amount,
            payment_status
        )
        VALUES (%s, %s, %s, %s, %s)
    """, (
        phone,
        merchant_reference,
        order_tracking_id,
        amount,
        payment_status
    ))

    conn.commit()
    cur.close()
    conn.close()        

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
    print(matches)

    if country == "254":
        currency = "KSh"
    elif country == "255":
        currency = "TZS"
    elif country == "256":
        currency = "UGX"
    elif country == "243":
        currency = "FC"
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

@app.route("/deposit/confirm")
def deposit_confirm():

    phone = session.get("phone")

    if not phone:
        return redirect("/login")

    try:
        amount = float(request.args.get("amount"))
    except (TypeError, ValueError):
        return "Invalid amount", 400

    if amount <= 0:
        return "Invalid amount", 400

    token = get_pesapal_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    merchant_reference = phone

    payload = {
        "id": merchant_reference,
        "currency": "KES",
        "amount": amount,
        "description": "BetNova Wallet Deposit",
        "callback_url": "https://http://www.betnova.lol/pesapal/callback",
        "notification_id": PESAPAL_IPN_ID,
        "billing_address": {
            "phone_number": phone
        }
    }   

    response = requests.post(
        "https://pay.pesapal.com/v3/api/Transactions/SubmitOrderRequest",
        json=payload,
        headers=headers
    )

    data = response.json()

    return redirect(data["redirect_url"])

@app.route("/pesapal/callback")
def pesapal_callback():

    order_tracking_id = request.args.get("OrderTrackingId")

    token = get_pesapal_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(
        f"https://pay.pesapal.com/v3/api/Transactions/GetTransactionStatus?orderTrackingId={order_tracking_id}",
        headers=headers
    )

    data = response.json()

    if data["payment_status_description"] == "Completed":
        amount = float(data["amount"])
        phone = session["phone"]

        balance = get_balance(phone)
        update_balance(phone, balance + amount)

    return redirect("/account")

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


@app.route("/pesapal/ipn",
methods=["GET", "POST"])
def pesapal_ipn():

    order_tracking_id = (
        request.args.get("OrderTrackingId")
        or request.form.get("OrderTrackingId")
    )

    merchant_reference = (
        request.args.get("OrderMerchantReference")
        or request.form.get("OrderMerchantReference")
    )

    if not order_tracking_id:
        return jsonify({
            "status": "error",
            "message": "Missing OrderTrackingId"
        }), 400

    token = get_pesapal_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(
        f"{PESAPAL_BASE_URL}/api/Transactions/GetTransactionStatus?orderTrackingId={order_tracking_id}",
        headers=headers
    )

    payment = response.json()

    if payment.get("payment_status_description") != "Completed":
        return jsonify({
            "status": "pending"
        }), 200

    # Prevent duplicate wallet credit
    if deposit_exists(order_tracking_id):
        return jsonify({
            "status": "success",
            "message": "Deposit already processed."
        }), 200

    phone = merchant_reference
    amount = float(payment["amount"])

    current_balance = get_balance(phone)

    update_balance(phone, current_balance + amount)

    save_deposit(
        phone=phone,
        merchant_reference=merchant_reference,
        order_tracking_id=order_tracking_id,
        amount=amount,
        payment_status="Completed"
    )

    return jsonify({
        "status": "success",
        "message": "Wallet credited successfully."
    }), 200

@app.route("/admin/login", 
methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT username, password_hash, role, is_active
            FROM admins
            WHERE username = %s
        """, (username,))

        admin = cur.fetchone()

        cur.close()
        conn.close()

        if admin and admin[3]:
            if check_password_hash(admin[1], password):
                session["admin"] = True
                session["admin_username"] = admin[0]
                session["admin_role"] = admin[2]
                return redirect("/admin/dashboard")

        return render_template(
            "admin_login.html",
            error="Invalid username or password"
        )

    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():

    if not session.get("admin"):
        return redirect("/admin/login")

    conn = get_connection()
    cur = conn.cursor()

    # Total users
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    # Total completed deposits
    cur.execute("""
        SELECT COALESCE(SUM(amount),0)
        FROM deposits
        WHERE payment_status='completed'
    """)
    total_deposits = cur.fetchone()[0]

    # Total withdrawals
    cur.execute("""
        SELECT COALESCE(SUM(amount),0)
        FROM withdrawals
        WHERE status='Approved'
    """)
    total_withdrawals = cur.fetchone()[0]

    profit = total_deposits - total_withdrawals

    cur.execute("""
        SELECT
            phone,
            amount,
            payment_status,
            deposited_at
        FROM deposits
        ORDER BY deposited_at DESC
        LIMIT 10
    """)

    rows = cur.fetchall()

    deposits = []

    for row in rows:
        deposits.append({
            "phone": row[0],
            "amount": row[1],
            "status": row[2],
            "date": row[3]
        })

    cur.close()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_deposits=total_deposits,
        total_withdrawals=total_withdrawals,
        profit=profit,
        deposits=deposits
    )

@app.route("/admin/matches/add", 
methods=["GET", "POST"])
def add_match():

    if not session.get("admin"):
        return redirect("/admin/login")

    if request.method == "POST":

        sport = request.form["sport"]
        league = request.form["league"]
        home_team = request.form["home_team"]
        away_team = request.form["away_team"]
        kickoff = request.form["match_time"]

        home_odds = request.form["home_odds"]
        draw_odds = request.form["draw_odds"]
        away_odds = request.form["away_odds"]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO matches
            (sport, league, home_team, away_team, kickoff,
             home_odds, draw_odds, away_odds)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            sport,
            league,
            home_team,
            away_team,
            kickoff,
            home_odds,
            draw_odds,
            away_odds
        ))

        conn.commit()
        cur.close()
        conn.close()

        return redirect("/admin/dashboard")

    return render_template("add_match.html")

@app.route("/admin/matches")
def admin_matches():

    if not session.get("admin"):
        return redirect("/admin/login")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id,
               sport,
               league,
               home_team,
               away_team,
               kickoff,
               status
        FROM matches
        ORDER BY kickoff ASC
    """)

    matches = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "admin_matches.html",
        matches=matches
    )

@app.route("/admin/matches/edit/<int:match_id>", 
methods=["GET", "POST"])
def edit_match(match_id):
    if not session.get("admin"):
        return redirect("/admin/login")

    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        sport = request.form["sport"]
        league = request.form["league"]
        home_team = request.form["home_team"]
        away_team = request.form["away_team"]
        kickoff = request.form["kickoff"]
        home_odds = request.form["home_odds"]
        draw_odds = request.form["draw_odds"]
        away_odds = request.form["away_odds"]
        status = request.form["status"]

        cur.execute("""
            UPDATE matches
            SET sport=%s,
                league=%s,
                home_team=%s,
                away_team=%s,
                kickoff=%s,
                home_odds=%s,
                draw_odds=%s,
                away_odds=%s,
                status=%s
            WHERE id=%s
        """, (
            sport,
            league,
            home_team,
            away_team,
            kickoff,
            home_odds,
            draw_odds,
            away_odds,
            status,
            match_id
        ))

        conn.commit()
        cur.close()
        conn.close()

        return redirect("/admin/matches")

    cur.execute("""
        SELECT id,
               sport,
               league,
               home_team,
               away_team,
               kickoff,
               home_odds,
               draw_odds,
               away_odds,
               status
        FROM matches
        WHERE id=%s
    """, (match_id,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return "Match not found", 404

    match = {
        "id": row[0],
        "sport": row[1],
        "league": row[2],
        "home_team": row[3],
        "away_team": row[4],
        "kickoff": row[5],
        "home_odds": row[6],
        "draw_odds": row[7],
        "away_odds": row[8],
        "status": row[9],
    }

    return render_template("edit_match.html", match=match)

@app.route("/admin/matches/delete/<int:match_id>")
def delete_match(match_id):
    if not session.get("admin"):
        return redirect("/admin/login")

    conn = get_connection()
    cur = conn.cursor()

    # Delete all markets belonging to the match first
    cur.execute("DELETE FROM markets WHERE match_id = %s", (match_id,))

    # Delete the match
    cur.execute("DELETE FROM matches WHERE id = %s", (match_id,))

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/admin/matches")

if __name__== "__main__":
    app.run(host="127.0.0.1", 
port=5000)
