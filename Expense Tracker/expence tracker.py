#expence tracker
import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import json
from datetime import datetime
from collections import deque

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("💰 Expense Tracker")
        self.expenses = []
        self.history = deque(maxlen=50)  
        self.future = deque(maxlen=50)   
        self.load_expenses()

        self.setup_ui()
        self.update_table()

    def load_expenses(self, filename="expenses.csv"):
        if os.path.exists(filename):
            with open(filename, mode="r") as file:
                self.expenses = list(csv.DictReader(file))
        self.save_state()

    def save_expenses(self, filename="expenses.csv"):
        with open(filename, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["Date", "Description", "Category", "Amount"])
            writer.writeheader()
            writer.writerows(self.expenses)

    def save_state(self):
        self.history.append(json.dumps(self.expenses))
        self.future.clear()

    def undo(self):
        if len(self.history) > 1:
            self.future.append(self.history.pop())
            self.expenses = json.loads(self.history[-1])
            self.update_table()
            self.save_expenses()

    def redo(self):
        if self.future:
            self.history.append(self.future.pop())
            self.expenses = json.loads(self.history[-1])
            self.update_table()
            self.save_expenses()

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%d-%m-%Y")
            return True
        except ValueError:
            return False

    def add_expense(self):
        date = self.date_entry.get()
        desc = self.desc_entry.get()
        category = self.category_var.get()
        amount = self.amount_entry.get()

        if not all([date, desc, category, amount]):
            messagebox.showerror("Error", "All fields are required!")
            return

        if not self.validate_date(date):
            messagebox.showerror("Error", "Use DD-MM-YYYY format!")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number!")
            return

        self.save_state()
        self.expenses.append({
            "Date": date,
            "Description": desc,
            "Category": category,
            "Amount": amount
        })
        self.save_expenses()
        self.clear_entries()
        self.update_table()
        messagebox.showinfo("Success", "Expense added!")

    def edit_expense(self):
        selected = self.get_selected_expense()
        if not selected:
            return

        self.save_state()
        self.delete_expense(silent=True)

        # Pre-fill form
        self.clear_entries()
        self.date_entry.insert(0, selected[0])
        self.desc_entry.insert(0, selected[1])
        self.category_var.set(selected[2])
        self.amount_entry.insert(0, selected[3].replace("₹", ""))

    def delete_expense(self, silent=False):
        selected = self.tree.focus()
        if not selected:
            if not silent:
                messagebox.showerror("Error", "No expense selected!")
            return

        if not silent and not messagebox.askyesno("Confirm", "Delete this expense?"):
            return

        self.save_state()
        index = int(selected.lstrip("I")) - 1
        self.expenses.pop(index)
        self.save_expenses()
        self.update_table()

        if not silent:
            messagebox.showinfo("Success", "Expense deleted!")

    def setup_ui(self):
        input_frame = ttk.LabelFrame(self.root, text="Add/Edit Expense", padding=10)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(input_frame, text="Date (DD-MM-YYYY):").grid(row=0, column=0, sticky="w")
        self.date_entry = ttk.Entry(input_frame)
        self.date_entry.grid(row=0, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(input_frame, text="Description:").grid(row=1, column=0, sticky="w")
        self.desc_entry = ttk.Entry(input_frame)
        self.desc_entry.grid(row=1, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(input_frame, text="Category:").grid(row=2, column=0, sticky="w")
        self.category_var = tk.StringVar()
        self.category_entry = ttk.Combobox(
            input_frame,
            textvariable=self.category_var,
            values=["Food", "Transport", "Bills", "Entertainment", "Healthcare", "Other"]
        )
        self.category_entry.grid(row=2, column=1, pady=5, padx=5, sticky="ew")

        ttk.Label(input_frame, text="Amount (₹):").grid(row=3, column=0, sticky="w")
        self.amount_entry = ttk.Entry(input_frame)
        self.amount_entry.grid(row=3, column=1, pady=5, padx=5, sticky="ew")

        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=4, columnspan=2, pady=5)
        ttk.Button(btn_frame, text="Add/Update", command=self.add_expense).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear", command=self.clear_entries).pack(side=tk.LEFT, padx=2)

        table_frame = ttk.LabelFrame(self.root, text="Expenses", padding=10)
        table_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        columns = ("Date", "Description", "Category", "Amount")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100 if col != "Description" else 150)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(expand=True, fill=tk.BOTH)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<Double-1>", lambda e: self.edit_expense())

        ctrl_frame = ttk.Frame(self.root)
        ctrl_frame.grid(row=2, column=0, pady=5)

        ttk.Button(ctrl_frame, text="✏️ Edit", command=self.edit_expense).pack(side=tk.LEFT, padx=2)
        ttk.Button(ctrl_frame, text="🗑️ Delete", command=self.delete_expense).pack(side=tk.LEFT, padx=2)
        ttk.Button(ctrl_frame, text="⏪ Undo", command=self.undo).pack(side=tk.LEFT, padx=2)
        ttk.Button(ctrl_frame, text="⏩ Redo", command=self.redo).pack(side=tk.LEFT, padx=2)
        ttk.Button(ctrl_frame, text="📊 Charts", command=self.show_charts).pack(side=tk.LEFT, padx=2)
        ttk.Button(ctrl_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT, padx=2)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

    def clear_entries(self):
        self.date_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.category_var.set("")
        self.amount_entry.delete(0, tk.END)

    def update_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        category_colors = {
            "Food": "#FFDDC1",
            "Transport": "#C1FFD7",
            "Bills": "#C1D0FF",
            "Entertainment": "#E6C1FF",
            "Healthcare": "#FFC1E0",
            "Other": "#F0F0F0"
        }

        for i, expense in enumerate(self.expenses):
            tag = expense["Category"]
            self.tree.insert("", tk.END, iid=f"I{i+1}", values=(
                expense["Date"],
                expense["Description"],
                expense["Category"],
                f'₹{float(expense["Amount"]):.2f}'
            ), tags=(tag,))

        for cat, color in category_colors.items():
            self.tree.tag_configure(cat, background=color)

    def get_selected_expense(self):
        selected = self.tree.focus()
        return self.tree.item(selected)["values"] if selected else None

    def show_charts(self):
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            categories = {}
            for expense in self.expenses:
                cat = expense["Category"]
                categories[cat] = categories.get(cat, 0) + float(expense["Amount"])

            if not categories:
                messagebox.showinfo("Info", "No data to display!")
                return

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

            # Pie Chart
            ax1.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%')
            ax1.set_title("Expense Distribution")

            ax2.bar(categories.keys(), categories.values())
            ax2.set_title("Amount by Category")
            plt.xticks(rotation=45)

            chart_window = tk.Toplevel(self.root)
            chart_window.title("Expense Charts")
            canvas = FigureCanvasTkAgg(fig, master=chart_window)
            canvas.draw()
            canvas.get_tk_widget().pack()

        except ImportError:
            messagebox.showerror("Error", "Install matplotlib first: pip install matplotlib")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()