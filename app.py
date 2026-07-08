import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]

    # Get user's current cash
    cash_row = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    cash = cash_row[0]["cash"]

    # Get total shares grouped by symbol
    holdings = db.execute(
        "SELECT symbol, SUM(shares) as total_shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING total_shares > 0",
        user_id
    )

    portfolio = []
    stocks_total_value = 0

    for holding in holdings:
        stock_info = lookup(holding["symbol"])
        if stock_info:
            current_price = stock_info["price"]
            total_value = holding["total_shares"] * current_price
            stocks_total_value += total_value
            portfolio.append({
                "symbol": holding["symbol"],
                "name": stock_info["name"],
                "shares": holding["total_shares"],
                "price": current_price,
                "total": total_value
            })

    grand_total = cash + stocks_total_value

    return render_template("index.html", portfolio=portfolio, cash=cash, grand_total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares_input = request.form.get("shares")

        if not symbol:
            return apology("must provide symbol", 400)

        stock = lookup(symbol)
        if not stock:
            return apology("invalid symbol", 400)

        if not shares_input:
            return apology("must provide number of shares", 400)

        # Validate that shares is a positive integer
        try:
            shares = int(shares_input)
            if shares <= 0:
                raise ValueError
        except ValueError:
            return apology("shares must be a positive integer", 400)

        user_id = session["user_id"]
        cash_row = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_cash = cash_row[0]["cash"]

        total_cost = stock["price"] * shares

        if user_cash < total_cost:
            return apology("can't afford", 400)

        # Update cash and record transaction
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", total_cost, user_id)
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
            user_id, stock["symbol"], shares, stock["price"]
        )

        flash("Bought!")
        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    transactions = db.execute(
        "SELECT symbol, shares, price, timestamp FROM transactions WHERE user_id = ? ORDER BY timestamp DESC",
        user_id
    )
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        session["user_id"] = rows[0]["id"]
        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide symbol", 400)

        stock = lookup(symbol)
        if not stock:
            return apology("invalid symbol", 400)

        return render_template("quoted.html", stock=stock)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("must provide username", 400)
        if not password:
            return apology("must provide password", 400)
        if not confirmation:
            return apology("must confirm password", 400)
        if password != confirmation:
            return apology("passwords do not match", 400)

        # Hash password and insert into DB safely
        hash_value = generate_password_hash(password)
        try:
            user_id = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_value)
        except ValueError:
            return apology("username already exists", 400)

        session["user_id"] = user_id
        flash("Registered!")
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]

    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares_input = request.form.get("shares")

        if not symbol:
            return apology("must provide symbol", 400)
        if not shares_input:
            return apology("must provide shares", 400)

        try:
            shares = int(shares_input)
            if shares <= 0:
                raise ValueError
        except ValueError:
            return apology("shares must be a positive integer", 400)

        # Check if user owns enough shares
        user_shares = db.execute(
            "SELECT SUM(shares) as total_shares FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol",
            user_id, symbol
        )

        if not user_shares or user_shares[0]["total_shares"] < shares:
            return apology("not enough shares", 400)

        stock = lookup(symbol)
        total_gain = stock["price"] * shares

        # Update cash and record transaction as negative shares
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", total_gain, user_id)
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
            user_id, symbol, -shares, stock["price"]
        )

        flash("Sold!")
        return redirect("/")
    else:
        # Get all symbols the user currently owns to populate dropdown
        stocks = db.execute(
            "SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0",
            user_id
        )
        return render_template("sell.html", stocks=stocks)


@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    """Personal Touch: Allow users to add cash to their account"""
    if request.method == "POST":
        amount_input = request.form.get("amount")

        try:
            amount = float(amount_input)
            if amount <= 0:
                raise ValueError
        except ValueError:
            return apology("must enter a valid positive amount", 400)

        user_id = session["user_id"]
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", amount, user_id)

        flash("Cash Added!")
        return redirect("/")
    else:
        return render_template("add_cash.html")
