import tkinter as tk
from tkinter import messagebox, ttk

from finance import Expense, FinanceManager, Income


RUPEE = "\u20b9"


class FinanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Finance Dashboard")
        self.geometry("1040x680")
        self.minsize(860, 560)
        self.configure(bg="#f4f7fb")
        self.manager = FinanceManager()
        self.person_name = tk.StringVar()
        self.person_age = tk.StringVar()
        self.credit_card_status = tk.StringVar(value="Add age to check credit-card status")
        self.credit_remainder = tk.StringVar(value="")
        self._build_style()
        self._build_ui()
        self.refresh()

    def _build_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("App.TFrame", background="#f4f7fb")
        style.configure("Panel.TFrame", background="#ffffff")
        style.configure("Title.TLabel", background="#f4f7fb", foreground="#172033", font=("Segoe UI", 25, "bold"))
        style.configure("Subtitle.TLabel", background="#f4f7fb", foreground="#657089", font=("Segoe UI", 10))
        style.configure("CardTitle.TLabel", background="#ffffff", foreground="#657089", font=("Segoe UI", 9, "bold"))
        style.configure("CardValue.TLabel", background="#ffffff", foreground="#172033", font=("Segoe UI", 20, "bold"))
        style.configure("TLabel", background="#ffffff", foreground="#25304a", font=("Segoe UI", 10))
        style.configure("TButton", padding=(12, 8), font=("Segoe UI", 10, "bold"))
        style.configure("Accent.TButton", background="#3164d8", foreground="#ffffff")
        style.map("Accent.TButton", background=[("active", "#244da9")])
        style.configure("Treeview", rowheight=32, font=("Segoe UI", 10), background="#ffffff", fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e9eef8" if True else "#fff")
        style.configure("TLabelframe", background="#ffffff")
        style.configure("TLabelframe.Label", background="#ffffff", foreground="#172033", font=("Segoe UI", 11, "bold"))

    def _build_ui(self):
        root = ttk.Frame(self, style="App.TFrame", padding=28)
        root.pack(fill="both", expand=True)
        header = ttk.Frame(root, style="App.TFrame")
        header.pack(fill="x", pady=(0, 22))
        ttk.Label(header, text="Personal Finance", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="A clear view of your income, spending, and savings.", style="Subtitle.TLabel").pack(anchor="w", pady=(4, 0))

        profile = ttk.LabelFrame(root, text="Person profile", padding=12)
        profile.pack(fill="x", pady=(0, 18))
        ttk.Label(profile, text="Name").pack(side="left")
        ttk.Entry(profile, textvariable=self.person_name, width=24).pack(side="left", padx=(6, 18))
        ttk.Label(profile, text="Age").pack(side="left")
        ttk.Entry(profile, textvariable=self.person_age, width=8).pack(side="left", padx=(6, 12))
        ttk.Button(profile, text="Save profile", command=self.save_profile).pack(side="left")
        ttk.Label(profile, textvariable=self.credit_card_status, foreground="#3164d8", font=("Segoe UI", 10, "bold")).pack(side="right", padx=8)
        ttk.Label(profile, textvariable=self.credit_remainder, foreground="#18805f", font=("Segoe UI", 10, "bold")).pack(side="right", padx=8)

        cards = ttk.Frame(root, style="App.TFrame")
        cards.pack(fill="x", pady=(0, 22))
        self.card_values = {}
        for key, label, color in (("income", "TOTAL INCOME", "#18805f"), ("expense", "TOTAL EXPENSE", "#c04c4c"), ("savings", "MONTHLY SAVINGS", "#3164d8"), ("budget", "BUDGET", "#9b6b16")):
            panel = ttk.Frame(cards, style="Panel.TFrame", padding=18)
            panel.pack(side="left", fill="x", expand=True, padx=(0, 12))
            ttk.Label(panel, text=label, style="CardTitle.TLabel").pack(anchor="w")
            value = ttk.Label(panel, text=f"{RUPEE}0.00", style="CardValue.TLabel", foreground=color)
            value.pack(anchor="w", pady=(8, 0))
            self.card_values[key] = value
        cards.winfo_children()[-1].pack_configure(padx=0)

        body = ttk.Frame(root, style="App.TFrame")
        body.pack(fill="both", expand=True)
        form = ttk.LabelFrame(body, text="Add transaction", padding=16)
        form.pack(side="left", fill="y", padx=(0, 18))
        self.kind = tk.StringVar(value="Expense")
        self.amount = tk.StringVar()
        self.category = tk.StringVar()
        self.description = tk.StringVar()
        self.detail = tk.StringVar()
        ttk.Label(form, text="Type").pack(anchor="w")
        ttk.Combobox(form, textvariable=self.kind, values=("Income", "Expense"), state="readonly", width=23).pack(fill="x", pady=(4, 12))
        for label, variable in (("Amount", self.amount), ("Category", self.category), ("Description", self.description), ("Source / payment", self.detail)):
            ttk.Label(form, text=label).pack(anchor="w")
            ttk.Entry(form, textvariable=variable, width=26).pack(fill="x", pady=(4, 12))
        ttk.Button(form, text="Add transaction", style="Accent.TButton", command=self.add_transaction).pack(fill="x", pady=(4, 8))
        ttk.Button(form, text="Clear fields", command=self.clear_form).pack(fill="x")
        ttk.Separator(form).pack(fill="x", pady=18)
        ttk.Button(form, text="Refresh data", command=self.refresh).pack(fill="x")

        table_panel = ttk.Frame(body, style="Panel.TFrame", padding=16)
        table_panel.pack(side="left", fill="both", expand=True)
        toolbar = ttk.Frame(table_panel, style="Panel.TFrame")
        toolbar.pack(fill="x", pady=(0, 10))
        ttk.Label(toolbar, text="Transaction history", font=("Segoe UI", 13, "bold")).pack(side="left")
        ttk.Button(toolbar, text="Delete selected", command=self.delete_selected).pack(side="right", padx=(8, 0))
        ttk.Button(toolbar, text="Clear history", command=self.clear_history).pack(side="right")
        self.status = ttk.Label(toolbar, text="", foreground="#657089")
        self.status.pack(side="right", padx=12)
        self.row_items = {}
        columns = ("selected", "type", "amount", "category", "description", "detail")
        self.table = ttk.Treeview(table_panel, columns=columns, show="headings")
        for column, heading, width in (("selected", "", 42), ("type", "Type", 90), ("amount", "Amount", 100), ("category", "Category", 120), ("description", "Description", 180), ("detail", "Source / payment", 150)):
            self.table.heading(column, text=heading)
            self.table.column(column, width=width, anchor="center" if column == "selected" else "w", stretch=column != "selected")
        self.table.tag_configure("income", foreground="#18805f")
        self.table.tag_configure("expense_low", foreground="#4f7d5b")
        self.table.tag_configure("expense_moderate", foreground="#b47722")
        self.table.tag_configure("expense_high", foreground="#c04c4c")
        self.table.bind("<Button-1>", self.toggle_checkbox)
        legend = ttk.Frame(table_panel, style="Panel.TFrame")
        legend.pack(fill="x", pady=(10, 0))
        ttk.Label(legend, text="Expense level:", foreground="#657089").pack(side="left")
        for label, color in (("Low", "#4f7d5b"), ("Moderate", "#b47722"), ("High", "#c04c4c")):
            ttk.Label(legend, text=f"  {label}", foreground=color, font=("Segoe UI", 9, "bold")).pack(side="left")
        scroll = ttk.Scrollbar(table_panel, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        self.table.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def save_profile(self):
        name = self.person_name.get().strip()
        if not name:
            messagebox.showerror("Missing name", "Enter the person's name.")
            return
        try:
            age = int(self.person_age.get().strip())
            if not 0 <= age <= 120:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid age", "Enter an age between 0 and 120.")
            return
        if age > 25:
            self.credit_card_status.set(f"{name}: Credit card available")
        else:
            self.credit_card_status.set(f"{name}: Credit card not available yet")
        self.update_credit_remainder(age)

    def update_credit_remainder(self, age=None):
        if age is None:
            try:
                age = int(self.person_age.get().strip())
            except ValueError:
                self.credit_remainder.set("")
                return
        if age <= 25:
            self.credit_remainder.set("")
            return
        income = sum(item.amount for item in self.manager.income)
        expenses = sum(item.amount for item in self.manager.expenses)
        remainder = income - expenses
        self.credit_remainder.set(f"Credit remainder: {RUPEE}{remainder:,.2f}")

    def add_transaction(self):
        try:
            amount = float(self.amount.get().strip())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid amount", "Enter a positive number for the amount.")
            return
        category = self.category.get().strip() or "General"
        description = self.description.get().strip() or "Unspecified"
        detail = self.detail.get().strip() or "-"
        if self.kind.get() == "Income":
            self.manager.income.append(Income(amount, category, description, detail))
        else:
            self.manager.expenses.append(Expense(amount, category, description, detail))
        self.clear_form()
        self.refresh()
        self.status.configure(text="Transaction added")

    def clear_form(self):
        self.amount.set("")
        self.category.set("")
        self.description.set("")
        self.detail.set("")

    def toggle_checkbox(self, event):
        row = self.table.identify_row(event.y)
        column = self.table.identify_column(event.x)
        if not row or column != "#1":
            return
        values = list(self.table.item(row, "values"))
        values[0] = "[x]" if values[0] == "[ ]" else "[ ]"
        self.table.item(row, values=values)

    def delete_selected(self):
        selected = [row for row in self.table.get_children() if self.table.set(row, "selected") == "[x]"]
        if not selected:
            messagebox.showinfo("Nothing selected", "Check the transactions you want to delete first.")
            return
        if not messagebox.askyesno("Delete transactions", f"Delete {len(selected)} selected transaction(s)?"):
            return
        rows_by_kind = {"Income": [], "Expense": []}
        for row in selected:
            kind, index = self.row_items[row]
            rows_by_kind[kind].append(index)
        for kind, indexes in rows_by_kind.items():
            collection = self.manager.income if kind == "Income" else self.manager.expenses
            for index in sorted(indexes, reverse=True):
                del collection[index]
        self.refresh()
        self.status.configure(text="Selected transactions deleted")

    def clear_history(self):
        count = len(self.manager.income) + len(self.manager.expenses)
        if not count:
            messagebox.showinfo("History is empty", "There are no transactions to clear.")
            return
        if not messagebox.askyesno("Clear history", f"Delete all {count} transaction(s)?"):
            return
        self.manager.income.clear()
        self.manager.expenses.clear()
        self.refresh()
        self.status.configure(text="History cleared")

    def refresh(self):
        income = sum(item.amount for item in self.manager.income)
        expense = sum(item.amount for item in self.manager.expenses)
        budget = self.manager.budget or 0
        self.card_values["income"].configure(text=f"{RUPEE}{income:,.2f}")
        self.card_values["expense"].configure(text=f"{RUPEE}{expense:,.2f}")
        self.card_values["savings"].configure(text=f"{RUPEE}{income - expense:,.2f}")
        self.card_values["budget"].configure(text=f"{RUPEE}{budget:,.2f}")
        for item in self.table.get_children():
            self.table.delete(item)
        self.row_items.clear()
        for index, item in enumerate(self.manager.income):
            row = self.table.insert("", "end", values=("[ ]", "Income", f"{RUPEE}{item.amount:,.2f}", item.category, item.description, item.source), tags=("income",))
            self.row_items[row] = ("Income", index)
        for index, item in enumerate(self.manager.expenses):
            expense_level = self.expense_level(item.amount)
            row = self.table.insert("", "end", values=("[ ]", "Expense", f"{RUPEE}{item.amount:,.2f}", item.category, item.description, item.payment), tags=(expense_level,))
            self.row_items[row] = ("Expense", index)
        self.status.configure(text=f"{len(self.table.get_children())} transactions")
        self.update_credit_remainder()

    @staticmethod
    def expense_level(amount):
        if amount < 50:
            return "expense_low"
        if amount <= 200:
            return "expense_moderate"
        return "expense_high"


if __name__ == "__main__":
    FinanceApp().mainloop()
