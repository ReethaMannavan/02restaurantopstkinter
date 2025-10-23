import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
import os
import math

DB_FILE = "restaurant.db"
GST_RATE = 0.05

# ------------------- DATABASE -------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_no TEXT,
            total REAL,
            status TEXT,
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            item_name TEXT,
            qty INTEGER,
            price REAL,
            FOREIGN KEY(order_id) REFERENCES orders(id)
        )
    """)
    conn.commit()
    conn.close()

# ------------------- MENU -------------------
MENU = {
    "Starters": [
        ("Paneer Tikka", 180),
        ("Veg Manchurian", 150),
        ("Gobi 65", 160),
        ("Chicken 65", 190),
        ("Spring Rolls", 130),
        ("French Fries", 120),
        ("Tandoori Chicken", 250)
    ],
    "Main Course": [
        ("Butter Naan", 35),
        ("Garlic Naan", 40),
        ("Paneer Butter Masala", 230),
        ("Chicken Curry", 260),
        ("Dal Tadka", 180),
        ("Veg Pulao", 160),
        ("Chicken Biryani", 280),
        ("Veg Fried Rice", 170)
    ],
    "Desserts": [
        ("Gulab Jamun", 90),
        ("Ice Cream", 100),
        ("Rasmalai", 110),
        ("Brownie", 140),
        ("Carrot Halwa", 120),
        ("Falooda", 150)
    ],
    "Beverages": [
        ("Masala Tea", 40),
        ("Cold Coffee", 110),
        ("Lassi", 90),
        ("Fresh Lime Soda", 80),
        ("Buttermilk", 60),
        ("Filter Coffee", 50)
    ]
}

# ------------------- UTILITIES -------------------
def number_to_words(n):
    """Converts number to Indian-style words (simple version)."""
    from num2words import num2words
    return num2words(n, lang='en_IN').title() + " Only"

def generate_bill(order_id, table_no, items, subtotal, gst, total):
    folder = "bills"
    os.makedirs(folder, exist_ok=True)
    filename = f"{folder}/Bill_{table_no}_{order_id}.pdf"

    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Header
    c.setFillColor(colors.darkblue)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height-60, "REETHA'S RESTAURANT")
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.black)
    c.drawCentredString(width/2, height-80, "No. 21, MG Road, Chennai - 600001 | Ph: +91 98765 43210")

    # Bill Info
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height-110, f"Table No: {table_no}")
    c.drawString(400, height-110, f"Order ID: {order_id}")
    c.setFont("Helvetica", 11)
    c.drawString(50, height-125, f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")

    # Table header
    y = height - 160
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.darkblue)
    c.rect(45, y-20, 510, 25, fill=1)
    c.setFillColor(colors.white)
    c.drawString(55, y-12, "Item")
    c.drawString(320, y-12, "Qty")
    c.drawString(380, y-12, "Rate")
    c.drawString(470, y-12, "Total")
    c.setFillColor(colors.black)

    # Table rows
    y -= 30
    c.setFont("Helvetica", 11)
    for item_name, qty, price in items:
        if y < 100:
            c.showPage()
            y = height - 100
        total_price = qty * price
        c.drawString(55, y, item_name)
        c.drawRightString(355, y, str(qty))
        c.drawRightString(445, y, f"₹{price:.2f}")
        c.drawRightString(545, y, f"₹{total_price:.2f}")
        y -= 20

    # Summary box
    c.line(45, y-5, 550, y-5)
    y -= 25
    c.setFont("Helvetica-Bold", 12)
    c.drawString(380, y, "Subtotal:")
    c.drawRightString(545, y, f"₹{subtotal:.2f}")
    y -= 20
    c.drawString(380, y, f"GST (5%):")
    c.drawRightString(545, y, f"₹{gst:.2f}")
    y -= 20
    c.setFont("Helvetica-Bold", 13)
    c.drawString(380, y, "Grand Total:")
    c.drawRightString(545, y, f"₹{total:.2f}")

    # Amount in words
    y -= 30
    c.setFont("Helvetica-Oblique", 11)
    c.drawString(50, y, f"Amount in Words: {number_to_words(math.floor(total))}")

    # Footer
    y -= 60
    c.line(45, y, 550, y)
    y -= 30
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width/2, y, "Thank You! Visit Again 🙏")
    c.save()

    messagebox.showinfo("Bill Generated", f"Bill saved as {filename}")

# ------------------- MAIN APP -------------------
class RestaurantPOS(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Restaurant POS System - Light Elegant")
        self.geometry("1050x700")
        self.configure(bg="#f8f9fa")

        # Theme
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background="#f8f9fa", padding=10)
        style.configure("TNotebook.Tab", font=("Segoe UI", 11, "bold"), padding=[10, 6])
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#0078D7", foreground="white")
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)
        style.map("TNotebook.Tab", background=[("selected", "#0078D7")], foreground=[("selected", "white")])

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.create_order_tab()
        self.create_kitchen_tab()
        self.create_cashier_tab()
        self.refresh_kitchen()
        self.refresh_cashier()

    # ----------------- ORDER TAB -----------------
    def create_order_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🧾 Order Entry")

        ttk.Label(frame, text="Select Table:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.table_var = tk.StringVar(value="T1")
        tables = [f"T{i}" for i in range(1, 11)]
        ttk.Combobox(frame, textvariable=self.table_var, values=tables, width=10).grid(row=0, column=1, padx=5, pady=10)

        ttk.Label(frame, text="Category:", font=("Segoe UI", 11, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.menu_category = tk.StringVar(value=list(MENU.keys())[0])
        ttk.Combobox(frame, textvariable=self.menu_category, values=list(MENU.keys()), width=20).grid(row=1, column=1)
        ttk.Button(frame, text="Show Items", command=self.show_menu_items).grid(row=1, column=2, padx=10)

        self.item_listbox = tk.Listbox(frame, width=40, height=14, font=("Segoe UI", 10))
        self.item_listbox.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.show_menu_items()

        ttk.Label(frame, text="Quantity:", font=("Segoe UI", 10)).grid(row=3, column=0, padx=10, sticky="e")
        self.qty_var = tk.IntVar(value=1)
        tk.Entry(frame, textvariable=self.qty_var, width=5).grid(row=3, column=1, sticky="w")
        ttk.Button(frame, text="Add to Order", command=self.add_to_order).grid(row=3, column=2, padx=10)

        columns = ("Item", "Qty", "Price", "Total")
        self.order_tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.order_tree.heading(col, text=col)
            self.order_tree.column(col, width=120)
        self.order_tree.grid(row=4, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        ttk.Button(frame, text="Save Order", command=self.save_order).grid(row=5, column=0, padx=10, pady=10)
        ttk.Button(frame, text="Clear", command=self.clear_order).grid(row=5, column=1, padx=10)
        self.total_var = tk.StringVar(value="Total: ₹0.00")
        ttk.Label(frame, textvariable=self.total_var, font=("Segoe UI", 13, "bold"), foreground="#0078D7").grid(row=5, column=2, sticky="e")

        frame.columnconfigure(3, weight=1)
        frame.rowconfigure(4, weight=1)
        self.current_order = []

    def show_menu_items(self):
        self.item_listbox.delete(0, tk.END)
        category = self.menu_category.get()
        for name, price in MENU.get(category, []):
            self.item_listbox.insert(tk.END, f"{name} - ₹{price}")

    def add_to_order(self):
        selection = self.item_listbox.curselection()
        if not selection:
            messagebox.showwarning("No item", "Please select an item.")
            return
        item_text = self.item_listbox.get(selection[0])
        name, price = item_text.split(" - ₹")
        price = float(price)
        qty = self.qty_var.get()
        if qty <= 0:
            messagebox.showerror("Invalid qty", "Quantity must be greater than 0.")
            return
        self.current_order.append((name, qty, price))
        self.refresh_order_tree()

    def refresh_order_tree(self):
        for i in self.order_tree.get_children():
            self.order_tree.delete(i)
        subtotal = 0
        for name, qty, price in self.current_order:
            total = qty * price
            subtotal += total
            self.order_tree.insert("", tk.END, values=(name, qty, f"₹{price:.2f}", f"₹{total:.2f}"))
        gst = subtotal * GST_RATE
        grand_total = subtotal + gst
        self.total_var.set(f"Total (incl. GST): ₹{grand_total:.2f}")

    def clear_order(self):
        self.current_order = []
        self.refresh_order_tree()

    def save_order(self):
        if not self.current_order:
            messagebox.showwarning("Empty", "Add at least one item.")
            return
        table_no = self.table_var.get()
        subtotal = sum(qty * price for _, qty, price in self.current_order)
        gst = subtotal * GST_RATE
        total = subtotal + gst

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO orders (table_no, total, status, created_at) VALUES (?, ?, ?, ?)",
                  (table_no, total, "Pending", datetime.now().isoformat()))
        order_id = c.lastrowid
        for name, qty, price in self.current_order:
            c.execute("INSERT INTO order_items (order_id, item_name, qty, price) VALUES (?, ?, ?, ?)",
                      (order_id, name, qty, price))
        conn.commit()
        conn.close()

        messagebox.showinfo("Saved", f"Order #{order_id} saved for {table_no}")
        self.clear_order()
        self.refresh_kitchen()

    # ----------------- KITCHEN TAB -----------------
    def create_kitchen_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="👨‍🍳 Kitchen")

        columns = ("Order ID", "Table", "Total", "Status")
        self.kitchen_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.kitchen_tree.heading(col, text=col)
        self.kitchen_tree.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Button(frame, text="Mark as Prepared", command=self.mark_prepared).pack(pady=5)

    def refresh_kitchen(self):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, table_no, total, status FROM orders WHERE status='Pending'")
        rows = c.fetchall()
        conn.close()
        for i in self.kitchen_tree.get_children():
            self.kitchen_tree.delete(i)
        for row in rows:
            self.kitchen_tree.insert("", tk.END, values=row)

    def mark_prepared(self):
        selection = self.kitchen_tree.selection()
        if not selection:
            messagebox.showwarning("Select", "Select an order.")
            return
        order_id = self.kitchen_tree.item(selection[0])["values"][0]
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE orders SET status='Prepared' WHERE id=?", (order_id,))
        conn.commit()
        conn.close()
        self.refresh_kitchen()
        self.refresh_cashier()

    # ----------------- CASHIER TAB -----------------
    def create_cashier_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="💰 Cashier")

        columns = ("Order ID", "Table", "Total", "Status")
        self.cashier_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.cashier_tree.heading(col, text=col)
        self.cashier_tree.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Button(frame, text="Print Bill & Close", command=self.print_bill).pack(pady=5)

    def refresh_cashier(self):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, table_no, total, status FROM orders WHERE status='Prepared'")
        rows = c.fetchall()
        conn.close()
        for i in self.cashier_tree.get_children():
            self.cashier_tree.delete(i)
        for row in rows:
            self.cashier_tree.insert("", tk.END, values=row)

    def print_bill(self):
        selection = self.cashier_tree.selection()
        if not selection:
            messagebox.showwarning("Select", "Select an order to print.")
            return
        order_id = self.cashier_tree.item(selection[0])["values"][0]

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT table_no, total FROM orders WHERE id=?", (order_id,))
        order = c.fetchone()
        c.execute("SELECT item_name, qty, price FROM order_items WHERE order_id=?", (order_id,))
        items = c.fetchall()
        conn.close()

        table_no, total = order
        subtotal = sum(qty * price for _, qty, price in items)
        gst = subtotal * GST_RATE
        generate_bill(order_id, table_no, items, subtotal, gst, total)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE orders SET status='Paid' WHERE id=?", (order_id,))
        conn.commit()
        conn.close()

        self.refresh_cashier()

# ------------------- MAIN -------------------
if __name__ == "__main__":
    try:
        from num2words import num2words
    except ImportError:
        os.system("pip install num2words")
        from num2words import num2words

    init_db()
    app = RestaurantPOS()
    app.mainloop()
