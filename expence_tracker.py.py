import turtle
import json
import random
from datetime import datetime

DATA_FILE = "expense_tracker_data.json"

PANEL = "#16213E"
ROW = "#1D2B50"
WHITE = "#F8FAFC"
MUTED = "#CBD5E1"
GREEN = "#4ADE80"
RED = "#FB7185"
BLUE = "#38BDF8"
YELLOW = "#FACC15"
GOLD = "#F59E0B"
PURPLE = "#C4B5FD"
DARK = "#0B1120"

transactions = []
buttons = []
message = "Welcome! Select an option below."

def load_data():
    global transactions
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        transactions = data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        transactions = []


def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(transactions, f, indent=4)
        return True
    except OSError:
        return False


def get_totals():
    income = sum(t["amount"] for t in transactions if t["type"] == "Income")
    expenses = sum(t["amount"] for t in transactions if t["type"] == "Expense")
    return income, expenses, income - expenses

screen = turtle.Screen()
screen.setup(width=900, height=650)
screen.title("Expense Tracker Pro")
screen.bgcolor("#1A1240")
screen.tracer(0)

bg = turtle.Turtle()
bg.hideturtle()
bg.speed(0)
bg.penup()

pen = turtle.Turtle()
pen.hideturtle()
pen.speed(0)
pen.penup()


def rectangle(t, x, y, w, h, color):
    t.penup()
    t.goto(x, y)
    t.setheading(0)
    t.color(color)
    t.pendown()
    t.begin_fill()
    for _ in range(2):
        t.forward(w)
        t.left(90)
        t.forward(h)
        t.left(90)
    t.end_fill()
    t.penup()


def write_text(x, y, text, size=12, color=WHITE, align="left", style="normal"):
    pen.goto(x, y)
    pen.color(color)
    pen.write(str(text), align=align, font=("Arial", size, style))


def blend(c1, c2, t):
    """Colour between two hex colours (t = 0 to 1)."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def draw_ring(cx, cy, radius, color):
    bg.goto(cx, cy - radius)
    bg.setheading(0)
    bg.pensize(2)
    bg.color(color)
    bg.pendown()
    bg.circle(radius)
    bg.penup()


def draw_logo(x, y):
    """Gold coin inside a glowing blue ring, with a rising-bars badge."""
    bg.goto(x, y)
    bg.dot(78, "#14304F")
    bg.dot(70, BLUE)
    bg.dot(62, DARK)
    bg.dot(50, GOLD)
    bg.dot(42, YELLOW)
    bg.dot(34, GOLD)
    bg.goto(x, y - 9)
    bg.color(DARK)
    bg.write("Rs", align="center", font=("Arial", 15, "bold"))
    for i, h in enumerate((6, 10, 15)):
        rectangle(bg, x - 12 + i * 9, y - 30, 6, h, GREEN)


def draw_background():
    bands = 70
    for i in range(bands):
        color = blend("#0B1120", "#33196B", i / (bands - 1))
        rectangle(bg, -480, 345 - (i + 1) * 10, 960, 11, color)
    for cx, cy, base, glow in [(430, -240, 170, "#5B21B6"),
                               (-430, -250, 140, "#0369A1"),
                               (440, 150, 100, "#0E7490"),
                               (-440, 60, 80, "#7C3AED")]:
        for k in range(7):
            bg.goto(cx, cy)
            bg.dot(base * 2 - k * base / 3.6, blend("#150F33", glow, (k + 1) / 7))
    for r in (90, 140, 190, 240):
        draw_ring(-450, 330, r, "#2D2B6B")
        draw_ring(450, -330, r, "#2A2F6B")

    random.seed(11)
    for _ in range(90):
        bg.goto(random.randint(-470, 470), random.randint(-335, 335))
        bg.dot(random.choice((2, 2, 3, 4)), random.choice(("#475A8F", "#6D7FB8", "#8B5CF6")))

    heights = [20, 32, 26, 46, 38, 60, 50, 74, 64, 90, 78, 104, 90]
    for i, h in enumerate(heights):
        rectangle(bg, -470 + i * 74, -335, 44, h, "#1C2A52")
        rectangle(bg, -470 + i * 74, -335 + h, 44, 3, "#3B5A9A")

    rectangle(bg, -480, 232, 960, 113, "#0F172A")
    rectangle(bg, -480, 229, 960, 3, BLUE)
    rectangle(bg, -480, 227, 960, 2, PURPLE)
    draw_logo(-385, 282)


def draw_heading(title, subtitle):
    write_text(0, 272, title, 26, WHITE, "center", "bold")
    write_text(0, 245, subtitle, 12, MUTED, "center")
    write_text(425, 276, datetime.now().strftime("%a, %d %b %Y"), 11, WHITE, "right", "bold")
    write_text(425, 254, "Offline | Secure local storage", 9, BLUE, "right")

def draw_button(x, y, w, h, label, color, action):
    rectangle(pen, x, y, w, h, color)
    write_text(x + w / 2, y + h / 2 - 6, label, 11, DARK, "center", "bold")
    buttons.append((x, y, x + w, y + h, action))


def handle_click(x, y):
    for x1, y1, x2, y2, action in buttons[:]:
        if x1 <= x <= x2 and y1 <= y <= y2:
            action()
            return

def short(text, limit):
    return text if len(text) <= limit else text[:limit - 3] + "..."

def draw_insights(income, expenses):
    """Right-hand panel with quick statistics and progress bars."""
    rectangle(pen, 80, -240, 355, 275, PANEL)
    write_text(95, 8, "QUICK INSIGHTS", 14, PURPLE, style="bold")

    spent = [t["amount"] for t in transactions if t["type"] == "Expense"]
    rows = [
        ("Total transactions", len(transactions)),
        ("Income entries", len(transactions) - len(spent)),
        ("Expense entries", len(spent)),
        ("Average expense", f"Rs. {sum(spent) / len(spent):,.2f}" if spent else "Rs. 0.00"),
        ("Largest expense", f"Rs. {max(spent):,.2f}" if spent else "Rs. 0.00"),
    ]
    for i, (label, value) in enumerate(rows):
        y = -22 - i * 28
        write_text(95, y, label, 10, MUTED)
        write_text(420, y, value, 11, WHITE, "right", "bold")

    saved = max(0, min(100, (income - expenses) / income * 100)) if income else 0
    used = max(0, min(100, expenses / income * 100)) if income else 0

    for label, pct, color, y in (("Savings rate", saved, GREEN, -160),
                                 ("Spent of income", used, RED, -204)):
        write_text(95, y, label, 10, MUTED)
        write_text(420, y, f"{pct:.0f}%", 11, color, "right", "bold")
        rectangle(pen, 95, y - 20, 325, 12, "#334155")
        if pct > 0:
            rectangle(pen, 95, y - 20, 325 * pct / 100, 12, color)


def refresh():
    buttons.clear()
    pen.clear()
    income, expenses, balance = get_totals()

    draw_heading("EXPENSE TRACKER", "Personal Finance Management System")

    cards = [(-395, "TOTAL INCOME", income, GREEN),
             (-122, "TOTAL EXPENSES", expenses, RED),
             (151, "BALANCE", balance, GREEN if balance >= 0 else RED)]
    for x, title, amount, color in cards:
        rectangle(pen, x, 125, 245, 90, PANEL)
        rectangle(pen, x, 125, 245, 4, color)
        write_text(x + 122, 185, title, 11, MUTED, "center")
        write_text(x + 122, 151, f"Rs. {amount:,.2f}", 18, color, "center", "bold")

    draw_button(-370, 55, 160, 43, "ADD INCOME", GREEN, lambda: add_transaction("Income"))
    draw_button(-175, 55, 160, 43, "ADD EXPENSE", RED, lambda: add_transaction("Expense"))
    draw_button(20, 55, 160, 43, "VIEW HISTORY", BLUE, view_history)
    draw_button(215, 55, 160, 43, "UNDO LAST", YELLOW, undo_last)

    rectangle(pen, -435, -240, 495, 275, PANEL)
    write_text(-420, 8, "RECENT TRANSACTIONS", 14, PURPLE, style="bold")

    if not transactions:
        write_text(-420, -30, "No records yet. Add your first transaction!", 11, MUTED)
    else:
        for i, item in enumerate(transactions[-7:][::-1]):
            y = -22 - i * 31
            is_income = item["type"] == "Income"
            sign = "+" if is_income else "-"
            write_text(-420, y, f'{item["date"]} | {item["type"]} | {short(item["description"], 18)}', 10, WHITE)
            write_text(45, y, f'{sign} Rs. {item["amount"]:,.2f}', 10, GREEN if is_income else RED, "right")

    draw_insights(income, expenses)
    rectangle(pen, -435, -285, 870, 32, PANEL)
    write_text(-420, -275, message, 10, MUTED)
    screen.update()

def get_amount():
    while True:
        answer = screen.textinput("Enter Amount", "Enter amount in rupees:")
        if answer is None:
            return None
        try:
            amount = float(answer.strip())
            if not 0 < amount < float("inf"):
                raise ValueError
            return round(amount, 2)
        except ValueError:
            screen.textinput("Invalid Amount",
                             "Enter a valid positive number, e.g. 250 or 99.50.")


def get_description():
    answer = screen.textinput("Transaction Description",
                              "Enter description, e.g. Food, Salary, Bus fare:")
    return None if answer is None else answer.strip() or "General"


def add_transaction(kind):
    global message

    amount = get_amount()
    description = get_description() if amount is not None else None
    if amount is None or description is None:
        message = "Transaction cancelled."
        refresh()
        return

    transactions.append({
        "type": kind,
        "amount": amount,
        "description": description,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })

    if save_data():
        message = f"{kind} of Rs. {amount:,.2f} saved successfully."
    else:
        transactions.pop()
        message = "Could not save data. Check folder permissions."
    refresh()

def view_history():
    buttons.clear()
    pen.clear()

    draw_heading("TRANSACTION HISTORY", "Latest transactions appear first")

    rectangle(pen, -435, -225, 870, 430, PANEL)
    for x, label, align in ((-415, "DATE", "left"), (-250, "TYPE", "left"),
                            (-150, "DESCRIPTION", "left"), (415, "AMOUNT", "right")):
        write_text(x, 180, label, 10, PURPLE, align, "bold")

    if not transactions:
        write_text(0, 0, "No transactions recorded yet.", 14, WHITE, "center")
    else:
        for i, item in enumerate(transactions[-12:][::-1]):
            y = 148 - i * 30
            is_income = item["type"] == "Income"
            if i % 2 == 0:
                rectangle(pen, -425, y - 7, 850, 27, ROW)
            write_text(-415, y, item["date"], 11, WHITE)
            write_text(-250, y, item["type"], 11, GREEN if is_income else RED, style="bold")
            write_text(-150, y, short(item["description"], 38), 11, WHITE)
            write_text(415, y, f'{"+" if is_income else "-"} Rs. {item["amount"]:,.2f}',
                       11, GREEN if is_income else RED, "right", "bold")

        if len(transactions) > 12:
            write_text(0, -218, f"Showing 12 of {len(transactions)} records.",
                       10, MUTED, "center")

    draw_button(-90, -290, 180, 42, "BACK TO DASHBOARD", BLUE, refresh)
    screen.update()

def undo_last():
    global message

    if not transactions:
        message = "There are no transactions to undo."
        refresh()
        return

    last = transactions[-1]
    answer = screen.textinput(
        "Confirm Undo",
        f'Remove latest {last["type"]} of Rs. {last["amount"]:,.2f}? '
        'Type YES to confirm:')

    if answer is None or answer.strip().upper() != "YES":
        message = "Undo cancelled."
        refresh()
        return

    removed = transactions.pop()
    if save_data():
        message = f'Removed {removed["type"]} of Rs. {removed["amount"]:,.2f}.'
    else:
        transactions.append(removed)
        message = "Could not save changes; transaction restored."
    refresh()

draw_background()
load_data()
refresh()
screen.onclick(handle_click)
screen.mainloop()
