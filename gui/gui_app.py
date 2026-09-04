import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

# Ensure root project directory is in python module search path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from finance import FinanceManager, Income, Expense
from auth import UserManager

RUPEE = "Rs."


class FinanceGUIApp(tk.Tk):
    """Tkinter Desktop Dashboard GUI for Personal Finance Management System."""

    def __init__(self):
        super().__init__()
        self.title("Personal Finance Desktop Dashboard")
        self.geometry("1150x720")
        self.minsize(950, 620)
        self.configure(bg="#f4f7f6")

        self.auth_manager = UserManager()
        self.current_user = "default"
        self.user_info = {"full_name": "Guest User", "email": "guest@local"}
        self.manager = FinanceManager(username=self.current_user)

        self.setup_styles()
        self.build_ui()
        self.refresh()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Color palette
        self.style.configure("Main.TFrame", background="#f4f7f6")
        self.style.configure("Header.TFrame", background="#2b5876")
        self.style.configure("Header.TLabel", background="#2b5876", foreground="#ffffff", font=("Segoe UI", 15, "bold"))
        self.style.configure("SubHeader.TLabel", background="#2b5876", foreground="#dce4ec", font=("Segoe UI", 10))

        self.style.configure("Card.TFrame", background="#ffffff", relief="flat")
        self.style.configure("CardTitle.TLabel", background="#ffffff", foreground="#657089", font=("Segoe UI", 10, "bold"))
        self.style.configure("CardValue.TLabel", background="#ffffff", foreground="#2b5876", font=("Segoe UI", 16, "bold"))

        self.style.configure("Panel.TFrame", background="#ffffff", relief="flat")
        self.style.configure("PanelTitle.TLabel", background="#ffffff", foreground="#2b5876", font=("Segoe UI", 12, "bold"))

        self.style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=5)
        self.style.configure("Accent.TButton", font=("Segoe UI", 9, "bold"), background="#2b5876", foreground="#ffffff", padding=6)
        self.style.configure("Header.TButton", font=("Segoe UI", 9, "bold"), background="#4e73df", foreground="#ffffff", padding=4)

    def build_ui(self):
        # Top Header Banner
        header = ttk.Frame(self, style="Header.TFrame", padding=12)
        header.pack(fill="x")

        # Left Header Title
        title_frame = ttk.Frame(header, style="Header.TFrame")
        title_frame.pack(side="left")
        ttk.Label(title_frame, text="💼 Personal Finance Manager", style="Header.TLabel").pack(anchor="w")

        # Right Header Account Details
        user_frame = ttk.Frame(header, style="Header.TFrame")
        user_frame.pack(side="right")

        self.user_status_label = ttk.Label(user_frame, text="", style="SubHeader.TLabel")
        self.user_status_label.pack(side="left", padx=10)

        switch_btn = ttk.Button(user_frame, text="👤 Switch / Log In Account", command=self.open_account_dialog)
        switch_btn.pack(side="right", padx=5)

        # Main layout container
        main_container = ttk.Frame(self, style="Main.TFrame", padding=15)
        main_container.pack(fill="both", expand=True)

        # Summary Metrics Row
        cards_frame = ttk.Frame(main_container, style="Main.TFrame")
        cards_frame.pack(fill="x", pady=(0, 15))

        self.card_values = {}
        metrics = [
            ("income", "Total Income", "#18805f"),
            ("expense", "Total Expenses", "#c04c4c"),
            ("savings", "Net Savings", "#2b5876"),
            ("budget", "Monthly Budget", "#4f7d5b"),
        ]

        for idx, (key, title, color) in enumerate(metrics):
            card = ttk.Frame(cards_frame, style="Card.TFrame", padding=15)
            card.grid(row=0, column=idx, padx=6, sticky="ew")
            cards_frame.columnconfigure(idx, weight=1)

            ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w")
            lbl = ttk.Label(card, text=f"{RUPEE}0.00", style="CardValue.TLabel", foreground=color)
            lbl.pack(anchor="w", pady=(5, 0))
            self.card_values[key] = lbl

        # Content Split Layout (Left: Input Form, Right: Data Table)
        body = ttk.Frame(main_container, style="Main.TFrame")
        body.pack(fill="both", expand=True)

        # Left Panel - Form
        form_panel = ttk.Frame(body, style="Panel.TFrame", padding=15, width=320)
        form_panel.pack(side="left", fill="y", padx=(0, 10))
        form_panel.pack_propagate(False)

        ttk.Label(form_panel, text="Add Transaction", style="PanelTitle.TLabel").pack(anchor="w", pady=(0, 10))

        ttk.Label(form_panel, text="Transaction Type", background="#ffffff").pack(anchor="w", pady=(5, 2))
        self.kind_var = tk.StringVar(value="Income")
        type_cb = ttk.Combobox(form_panel, textvariable=self.kind_var, values=["Income", "Expense"], state="readonly")
        type_cb.pack(fill="x", pady=(0, 8))

        ttk.Label(form_panel, text="Amount (Rs.)", background="#ffffff").pack(anchor="w", pady=(5, 2))
        self.amount_var = tk.StringVar()
        ttk.Entry(form_panel, textvariable=self.amount_var).pack(fill="x", pady=(0, 8))

        ttk.Label(form_panel, text="Category", background="#ffffff").pack(anchor="w", pady=(5, 2))
        self.category_var = tk.StringVar()
        ttk.Entry(form_panel, textvariable=self.category_var).pack(fill="x", pady=(0, 8))

        ttk.Label(form_panel, text="Source / Payment Method", background="#ffffff").pack(anchor="w", pady=(5, 2))
        self.detail_var = tk.StringVar()
        ttk.Entry(form_panel, textvariable=self.detail_var).pack(fill="x", pady=(0, 8))

        ttk.Label(form_panel, text="Description", background="#ffffff").pack(anchor="w", pady=(5, 2))
        self.desc_var = tk.StringVar()
        ttk.Entry(form_panel, textvariable=self.desc_var).pack(fill="x", pady=(0, 15))

        ttk.Button(form_panel, text="➕ Add Entry", style="Accent.TButton", command=self.add_transaction).pack(fill="x", pady=4)
        ttk.Button(form_panel, text="🔄 Refresh Table", command=self.refresh).pack(fill="x", pady=4)

        # Right Panel - Table
        table_panel = ttk.Frame(body, style="Panel.TFrame", padding=15)
        table_panel.pack(side="right", fill="both", expand=True)

        toolbar = ttk.Frame(table_panel, style="Panel.TFrame")
        toolbar.pack(fill="x", pady=(0, 10))

        ttk.Label(toolbar, text="Transaction Records", style="PanelTitle.TLabel").pack(side="left")
        ttk.Button(toolbar, text="🗑️ Delete Selected", command=self.delete_selected).pack(side="right", padx=(5, 0))

        self.table_status = ttk.Label(toolbar, text="", background="#ffffff", foreground="#657089")
        self.table_status.pack(side="right", padx=10)

        # Treeview Table
        cols = ("type", "amount", "category", "detail", "description", "date")
        self.tree = ttk.Treeview(table_panel, columns=cols, show="headings", selectmode="extended")

        headings = [
            ("type", "Type", 90),
            ("amount", "Amount", 110),
            ("category", "Category", 130),
            ("detail", "Source / Payment", 150),
            ("description", "Description", 180),
            ("date", "Date", 110),
        ]

        for cid, title, width in headings:
            self.tree.heading(cid, text=title)
            self.tree.column(cid, width=width, anchor="w")

        self.tree.tag_configure("income", foreground="#18805f")
        self.tree.tag_configure("expense", foreground="#c04c4c")

        scroll = ttk.Scrollbar(table_panel, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def open_account_dialog(self):
        """Open a dialog window to log in, sign up, or switch accounts."""
        dialog = tk.Toplevel(self)
        dialog.title("Account Management")
        dialog.geometry("450x450")
        dialog.resizable(False, False)
        dialog.configure(bg="#ffffff")
        dialog.transient(self)
        dialog.grab_set()

        # Configure dialog background style
        self.style.configure("Dialog.TFrame", background="#ffffff")
        self.style.configure("Dialog.TNotebook", background="#ffffff")

        container = ttk.Frame(dialog, style="Dialog.TFrame", padding=15)
        container.pack(fill="both", expand=True)

        notebook = ttk.Notebook(container, style="Dialog.TNotebook")
        notebook.pack(fill="both", expand=True)

        # Tab 1: Log In
        login_tab = ttk.Frame(notebook, style="Dialog.TFrame", padding=15)
        notebook.add(login_tab, text="🔑 Log In")

        ttk.Label(login_tab, text="Username", font=("Segoe UI", 9, "bold"), background="#ffffff").pack(anchor="w", pady=(5, 2))
        login_user_var = tk.StringVar()
        ttk.Entry(login_tab, textvariable=login_user_var).pack(fill="x", pady=(0, 8))

        ttk.Label(login_tab, text="Password", font=("Segoe UI", 9, "bold"), background="#ffffff").pack(anchor="w", pady=(5, 2))
        login_pass_var = tk.StringVar()
        ttk.Entry(login_tab, textvariable=login_pass_var, show="*").pack(fill="x", pady=(0, 15))

        def handle_login():
            user = login_user_var.get().strip()
            pwd = login_pass_var.get().strip()
            ok, msg, info = self.auth_manager.login(user, pwd)
            if ok:
                self.current_user = user
                self.user_info = info
                self.manager = FinanceManager(username=self.current_user)
                self.refresh()
                dialog.destroy()
                messagebox.showinfo("Logged In", f"Welcome back, {info.get('full_name') or user}!")
            else:
                messagebox.showerror("Login Error", msg)

        ttk.Button(login_tab, text="Log In", style="Accent.TButton", command=handle_login).pack(fill="x", pady=5)

        # Quick Switch Option
        existing_users = list(self.auth_manager.users.keys())
        if existing_users:
            ttk.Separator(login_tab, orient="horizontal").pack(fill="x", pady=10)
            ttk.Label(login_tab, text="Quick Select Registered Account:", font=("Segoe UI", 9, "bold"), background="#ffffff").pack(anchor="w", pady=(0, 4))
            selected_user_var = tk.StringVar(value=existing_users[0])
            user_cb = ttk.Combobox(login_tab, textvariable=selected_user_var, values=existing_users, state="readonly")
            user_cb.pack(fill="x", pady=(0, 8))

            def handle_quick_switch():
                user = selected_user_var.get()
                info = self.auth_manager.users.get(user, {})
                self.current_user = user
                self.user_info = info
                self.manager = FinanceManager(username=self.current_user)
                self.refresh()
                dialog.destroy()

            ttk.Button(login_tab, text="Switch to Account", command=handle_quick_switch).pack(fill="x")

        # Tab 2: Sign Up
        signup_tab = ttk.Frame(notebook, style="Dialog.TFrame", padding=15)
        notebook.add(signup_tab, text="📝 Sign Up")

        ttk.Label(signup_tab, text="Username", font=("Segoe UI", 9, "bold"), background="#ffffff").pack(anchor="w", pady=(2, 1))
        su_user = tk.StringVar()
        ttk.Entry(signup_tab, textvariable=su_user).pack(fill="x", pady=(0, 4))

        ttk.Label(signup_tab, text="Full Name", font=("Segoe UI", 9, "bold"), background="#ffffff").pack(anchor="w", pady=(2, 1))
        su_name = tk.StringVar()
        ttk.Entry(signup_tab, textvariable=su_name).pack(fill="x", pady=(0, 4))

        ttk.Label(signup_tab, text="Email", font=("Segoe UI", 9, "bold"), background="#ffffff").pack(anchor="w", pady=(2, 1))
        su_email = tk.StringVar()
        ttk.Entry(signup_tab, textvariable=su_email).pack(fill="x", pady=(0, 4))

        ttk.Label(signup_tab, text="Password", font=("Segoe UI", 9, "bold"), background="#ffffff").pack(anchor="w", pady=(2, 1))
        su_pass = tk.StringVar()
        ttk.Entry(signup_tab, textvariable=su_pass, show="*").pack(fill="x", pady=(0, 10))

        def handle_signup():
            u = su_user.get().strip()
            n = su_name.get().strip()
            e = su_email.get().strip()
            p = su_pass.get().strip()

            ok, msg = self.auth_manager.signup(u, p, n, e)
            if ok:
                messagebox.showinfo("Sign Up Success", msg)
                login_user_var.set(u)
                notebook.select(0)
            else:
                messagebox.showerror("Sign Up Error", msg)

        ttk.Button(signup_tab, text="Create Account", style="Accent.TButton", command=handle_signup).pack(fill="x", pady=5)

    def add_transaction(self):
        try:
            val_str = self.amount_var.get().strip()
            if not val_str:
                messagebox.showerror("Error", "Please enter an amount.")
                return
            amount = float(val_str)
            if amount <= 0:
                messagebox.showerror("Error", "Amount must be greater than 0.")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric amount.")
            return

        category = self.category_var.get().strip() or "General"
        detail = self.detail_var.get().strip() or "N/A"
        desc = self.desc_var.get().strip() or "N/A"
        kind = self.kind_var.get()

        if kind == "Income":
            self.manager.income.append(Income(amount, category, desc, detail))
        else:
            self.manager.expenses.append(Expense(amount, category, desc, detail))

        # Clear form fields
        self.amount_var.set("")
        self.category_var.set("")
        self.detail_var.set("")
        self.desc_var.set("")

        self.refresh()
        messagebox.showinfo("Success", f"{kind} transaction added successfully.")

    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Notice", "Please select transaction(s) to delete from the table.")
            return

        if not messagebox.askyesno("Confirm", f"Delete {len(selected_items)} selected record(s)?"):
            return

        for item in selected_items:
            vals = self.tree.item(item, "values")
            if not vals:
                continue
            kind = vals[0]
            amt_str = vals[1].replace(RUPEE, "").replace(",", "").strip()
            cat = vals[2]

            try:
                amt = float(amt_str)
                if kind == "Income":
                    self.manager.income = [i for i in self.manager.income if not (i.amount == amt and i.category == cat)]
                else:
                    self.manager.expenses = [e for e in self.manager.expenses if not (e.amount == amt and e.category == cat)]
            except ValueError:
                pass

        self.refresh()

    def refresh(self):
        # Update User Header Info
        display_name = self.user_info.get("full_name") or self.current_user
        email = self.user_info.get("email") or "N/A"
        self.user_status_label.configure(text=f"👤 {display_name} (@{self.current_user})  |  📧 {email}")

        inc_total = sum(i.amount for i in self.manager.income)
        exp_total = sum(e.amount for e in self.manager.expenses)
        savings = inc_total - exp_total
        budget = self.manager.budget or 0

        self.card_values["income"].configure(text=f"{RUPEE}{inc_total:,.2f}")
        self.card_values["expense"].configure(text=f"{RUPEE}{exp_total:,.2f}")
        self.card_values["savings"].configure(text=f"{RUPEE}{savings:,.2f}")
        self.card_values["budget"].configure(text=f"{RUPEE}{budget:,.2f}")

        # Clear treeview items
        for item in self.tree.get_children():
            self.tree.delete(item)

        count = 0
        for item in self.manager.income:
            self.tree.insert("", "end", values=("Income", f"{RUPEE}{item.amount:,.2f}", item.category, item.source, item.description, getattr(item, "date", "-")), tags=("income",))
            count += 1

        for item in self.manager.expenses:
            self.tree.insert("", "end", values=("Expense", f"{RUPEE}{item.amount:,.2f}", item.category, item.payment, item.description, getattr(item, "date", "-")), tags=("expense",))
            count += 1

        self.table_status.configure(text=f"Total Records: {count}")


if __name__ == "__main__":
    app = FinanceGUIApp()
    app.mainloop()
