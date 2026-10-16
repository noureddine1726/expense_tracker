import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models import Expense
from database import DatabaseManager
from charts import draw_pie_chart
from export import export_expenses_to_csv


class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Expense Tracker")
        self.root.geometry("1100x650")
        self.db = DatabaseManager()
        self._setup_styles()
        self._build_layout()
        self.refresh_data()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))

    def _build_layout(self):
        left_frame = ttk.LabelFrame(self.root, text="Manage Expense", padding=15)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(left_frame, text="Amount ($):").pack(anchor=tk.W, pady=(10, 2))
        self.amount_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.amount_var).pack(fill=tk.X)

        ttk.Label(left_frame, text="Category:").pack(anchor=tk.W, pady=(10, 2))
        self.category_var = tk.StringVar()
        self.category_cb = ttk.Combobox(left_frame, textvariable=self.category_var, state="readonly")
        self.category_cb['values'] = ('Food', 'Transport', 'Education', 'Shopping', 'Entertainment', 'Bills', 'Other')
        self.category_cb.pack(fill=tk.X)

        ttk.Label(left_frame, text="Date (YYYY-MM-DD):").pack(anchor=tk.W, pady=(10, 2))
        self.date_var = tk.StringVar(value=datetime.today().strftime('%Y-%m-%d'))
        ttk.Entry(left_frame, textvariable=self.date_var).pack(fill=tk.X)

        ttk.Label(left_frame, text="Description:").pack(anchor=tk.W, pady=(10, 2))
        self.desc_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.desc_var).pack(fill=tk.X)

        ttk.Button(left_frame, text="Add Expense", command=self.add_expense).pack(fill=tk.X, pady=(20, 5))
        ttk.Button(left_frame, text="Delete Selected", command=self.delete_expense).pack(fill=tk.X, pady=5)
        ttk.Button(left_frame, text="Export to CSV", command=self.export_data).pack(fill=tk.X, pady=5)

        right_frame = ttk.Frame(self.root, padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        dash_frame = ttk.Frame(right_frame)
        dash_frame.pack(fill=tk.X, pady=(0, 10))

        self.total_label = ttk.Label(dash_frame, text="Total Expenses: $0.00", font=('Helvetica', 14, 'bold'))
        self.total_label.pack(side=tk.LEFT)

        ttk.Label(dash_frame, text="Search:").pack(side=tk.LEFT, padx=(50, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(dash_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<KeyRelease>', self.search_data)

        table_frame = ttk.Frame(right_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        self.chart_frame = ttk.Frame(right_frame, height=250)
        self.chart_frame.pack(fill=tk.X, pady=10)

        columns = ('id', 'amount', 'category', 'date', 'description')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', selectmode='browse')

        self.tree.heading('id', text='ID')
        self.tree.heading('amount', text='Amount')
        self.tree.heading('category', text='Category')
        self.tree.heading('date', text='Date')
        self.tree.heading('description', text='Description')

        self.tree.column('id', width=40, anchor=tk.CENTER)
        self.tree.column('amount', width=100, anchor=tk.E)
        self.tree.column('category', width=120)
        self.tree.column('date', width=100, anchor=tk.CENTER)
        self.tree.column('description', width=300)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def add_expense(self):
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                raise ValueError("Amount must be positive.")
            category = self.category_var.get()
            date = self.date_var.get()
            desc = self.desc_var.get()

            if not category or not date:
                messagebox.showwarning("Input Error", "Category and Date are required.")
                return

            new_expense = Expense(amount, category, date, desc)
            self.db.add_expense(new_expense)

            self.amount_var.set("")
            self.desc_var.set("")
            self.refresh_data()
            messagebox.showinfo("Success", "Expense added successfully!")

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric amount.")

    def delete_expense(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select an expense to delete.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this expense?"):
            item = self.tree.item(selected[0])
            expense_id = item['values'][0]
            self.db.delete_expense(expense_id)
            self.refresh_data()

    def search_data(self, event=None):
        keyword = self.search_var.get()
        if keyword:
            expenses = self.db.search_expenses(keyword)
            self._update_table(expenses)
        else:
            self.refresh_data()

    def refresh_data(self):
        expenses = self.db.get_all_expenses()
        self._update_table(expenses)

    def _update_table(self, expenses):
        for item in self.tree.get_children():
            self.tree.delete(item)

        total_amount = 0
        category_totals = {}

        for exp in expenses:
            self.tree.insert('', tk.END, values=exp.to_tuple())
            total_amount += exp.amount
            category_totals[exp.category] = category_totals.get(exp.category, 0) + exp.amount

        self.total_label.config(text=f"Total Expenses: ${total_amount:.2f}")
        draw_pie_chart(self.chart_frame, category_totals)

    def export_data(self):
        expenses = self.db.get_all_expenses()
        if not expenses:
            messagebox.showinfo("Empty", "No data to export.")
            return

        filepath = export_expenses_to_csv(expenses)
        messagebox.showinfo("Success", f"Data exported to:\n{filepath}")