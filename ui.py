import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from datetime import datetime
from models import Expense
from database import DatabaseManager
from charts import draw_pie_chart
from export import export_expenses_to_csv


class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Expense Tracker")
        self.root.geometry("1150x700")
        self.db = DatabaseManager()
        self._build_layout()
        self.refresh_data()

    def _build_layout(self):
        main_frame = tb.Frame(self.root, padding=25)
        main_frame.pack(fill=BOTH, expand=YES)

        # --- Left Panel (Inputs & Buttons) ---
        left_frame = tb.Labelframe(main_frame, text="Manage Expenses", padding=20, bootstyle="info")
        left_frame.pack(side=LEFT, fill=Y, padx=(0, 20))

        tb.Label(left_frame, text="Amount ($):", font=("Helvetica", 10)).pack(anchor=W, pady=(10, 5))
        self.amount_var = tb.StringVar()
        tb.Entry(left_frame, textvariable=self.amount_var, bootstyle="primary").pack(fill=X)

        tb.Label(left_frame, text="Category:", font=("Helvetica", 10)).pack(anchor=W, pady=(15, 5))
        self.category_var = tb.StringVar()
        self.category_cb = tb.Combobox(left_frame, textvariable=self.category_var, state="readonly",
                                       bootstyle="primary")
        self.category_cb['values'] = ('Food', 'Transport', 'Education', 'Shopping', 'Entertainment', 'Bills', 'Other')
        self.category_cb.pack(fill=X)

        tb.Label(left_frame, text="Date (YYYY-MM-DD):", font=("Helvetica", 10)).pack(anchor=W, pady=(15, 5))
        self.date_var = tb.StringVar(value=datetime.today().strftime('%Y-%m-%d'))
        tb.Entry(left_frame, textvariable=self.date_var, bootstyle="primary").pack(fill=X)

        tb.Label(left_frame, text="Description:", font=("Helvetica", 10)).pack(anchor=W, pady=(15, 5))
        self.desc_var = tb.StringVar()
        tb.Entry(left_frame, textvariable=self.desc_var, bootstyle="primary").pack(fill=X)

        tb.Button(left_frame, text="Add Expense", command=self.add_expense, bootstyle="success").pack(fill=X,
                                                                                                      pady=(35, 10))
        tb.Button(left_frame, text="Delete Selected", command=self.delete_expense, bootstyle="danger-outline").pack(
            fill=X, pady=5)
        tb.Button(left_frame, text="Export to CSV", command=self.export_data, bootstyle="info-outline").pack(fill=X,
                                                                                                             pady=5)

        # --- Right Panel (Dashboard, Table, Chart) ---
        right_frame = tb.Frame(main_frame)
        right_frame.pack(side=RIGHT, fill=BOTH, expand=YES)

        # Dashboard (Total & Search)
        dash_frame = tb.Frame(right_frame)
        dash_frame.pack(fill=X, pady=(0, 20))

        self.total_label = tb.Label(dash_frame, text="Total Expenses: $0.00", font=("Helvetica", 16, "bold"),
                                    bootstyle="inverse-primary")
        self.total_label.pack(side=LEFT)

        tb.Label(dash_frame, text="Search:", font=("Helvetica", 10)).pack(side=LEFT, padx=(50, 5))
        self.search_var = tb.StringVar()
        search_entry = tb.Entry(dash_frame, textvariable=self.search_var, bootstyle="secondary")
        search_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)
        search_entry.bind('<KeyRelease>', self.search_data)

        # Table
        table_frame = tb.Frame(right_frame)
        table_frame.pack(fill=BOTH, expand=YES)

        # Chart
        self.chart_frame = tb.Frame(right_frame, height=250)
        self.chart_frame.pack(fill=X, pady=(20, 0))

        columns = ('id', 'amount', 'category', 'date', 'description')
        self.tree = tb.Treeview(table_frame, columns=columns, show='headings', selectmode='browse', bootstyle="primary")

        self.tree.heading('id', text='ID')
        self.tree.heading('amount', text='Amount')
        self.tree.heading('category', text='Category')
        self.tree.heading('date', text='Date')
        self.tree.heading('description', text='Description')

        self.tree.column('id', width=40, anchor=CENTER)
        self.tree.column('amount', width=100, anchor=E)
        self.tree.column('category', width=120)
        self.tree.column('date', width=100, anchor=CENTER)
        self.tree.column('description', width=300)

        scrollbar = tb.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)

    def add_expense(self):
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                raise ValueError("Amount must be positive.")
            category = self.category_var.get()
            date = self.date_var.get()
            desc = self.desc_var.get()

            if not category or not date:
                Messagebox.show_warning("Category and Date are required.", "Input Error")
                return

            new_expense = Expense(amount, category, date, desc)
            self.db.add_expense(new_expense)

            self.amount_var.set("")
            self.desc_var.set("")
            self.refresh_data()
            Messagebox.show_info("Expense added successfully!", "Success")

        except ValueError:
            Messagebox.show_error("Please enter a valid numeric amount.", "Error")

    def delete_expense(self):
        selected = self.tree.selection()
        if not selected:
            Messagebox.show_warning("Please select an expense to delete.", "Selection Error")
            return

        if Messagebox.yesno("Are you sure you want to delete this expense?", "Confirm Delete") == "Yes":
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
            self.tree.insert('', END, values=exp.to_tuple())
            total_amount += exp.amount
            category_totals[exp.category] = category_totals.get(exp.category, 0) + exp.amount

        self.total_label.config(text=f"Total Expenses: ${total_amount:.2f}")
        draw_pie_chart(self.chart_frame, category_totals)

    def export_data(self):
        expenses = self.db.get_all_expenses()
        if not expenses:
            Messagebox.show_info("No data to export.", "Empty")
            return

        filepath = export_expenses_to_csv(expenses)
        Messagebox.show_info(f"Data exported to:\n{filepath}", "Success")s