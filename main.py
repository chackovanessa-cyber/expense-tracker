from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
import csv
import matplotlib.pyplot as plt

selected_id = None

# ---------------- Database Connection ----------------

def connect_db():
    return sqlite3.connect("expense.db")


# ---------------- Show Expenses ----------------

def show_expenses():
    for row in tree.get_children():
        tree.delete(row)

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()

    conn.close()

    for row in rows:
        tree.insert("", END, values=row)


# ---------------- Add Expense ----------------

def add_expense():

    date = date_entry.get()
    category = category_combo.get()
    description = description_entry.get()
    amount = amount_entry.get()

    if date == "" or category == "" or description == "" or amount == "":
        messagebox.showerror("Error", "All fields are required!")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be numeric!")
        return

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO expenses(date, category, description, amount)
        VALUES(?,?,?,?)
    """, (date, category, description, amount))

    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Expense Added Successfully!")

    date_entry.delete(0, END)
    category_combo.set("")
    description_entry.delete(0, END)
    amount_entry.delete(0, END)

    show_expenses()
    update_total()


# ---------------- Select Record ----------------

def select_record(event):
    global selected_id

    selected = tree.focus()

    if not selected:
        return

    values = tree.item(selected, "values")

    selected_id = values[0]

    date_entry.delete(0, END)
    date_entry.insert(0, values[1])

    category_combo.set(values[2])

    description_entry.delete(0, END)
    description_entry.insert(0, values[3])

    amount_entry.delete(0, END)
    amount_entry.insert(0, values[4])


# ---------------- Update Expense ----------------

def update_expense():
    global selected_id

    if selected_id is None:
        messagebox.showerror("Error", "Please select an expense.")
        return

    date = date_entry.get()
    category = category_combo.get()
    description = description_entry.get()
    amount = amount_entry.get()

    if date == "" or category == "" or description == "" or amount == "":
        messagebox.showerror("Error", "All fields are required!")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be numeric!")
        return

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE expenses
        SET date=?, category=?, description=?, amount=?
        WHERE id=?
    """, (date, category, description, amount, selected_id))

    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Expense Updated Successfully!")

    date_entry.delete(0, END)
    category_combo.set("")
    description_entry.delete(0, END)
    amount_entry.delete(0, END)

    selected_id = None

    show_expenses()
    update_total()
def clear_fields():
    global selected_id

    date_entry.delete(0, END)
    category_combo.set("")
    description_entry.delete(0, END)
    amount_entry.delete(0, END)

    selected_id = None

    tree.selection_remove(tree.selection())
def delete_expense():
    global selected_id

    if selected_id is None:
        messagebox.showerror("Error", "Please select an expense.")
        return

    answer = messagebox.askyesno(
        "Delete",
        "Are you sure you want to delete this expense?"
    )

    if answer:

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM expenses WHERE id=?",
            (selected_id,)
        )

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Success",
            "Expense Deleted Successfully!"
        )

        clear_fields()
        show_expenses()
        update_total()
def export_csv():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()

    conn.close()

    if len(rows) == 0:
        messagebox.showerror("Error", "No expenses found!")
        return

    with open("expenses.csv", "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(["ID", "Date", "Category", "Description", "Amount"])
        writer.writerows(rows)

    messagebox.showinfo("Success", "Expenses exported successfully!")
    # ---------------- SHOW CHART ---------------- #


def show_chart():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
         SELECT category, SUM(amount)
         FROM expenses
         GROUP BY category
     """)

    data = cursor.fetchall()

    conn.close()

    if len(data) == 0:
        messagebox.showerror("Error", "No expense data found!")
        return

    categories = []
    amounts = []

    for row in data:
        categories.append(row[0])
        amounts.append(row[1])

    plt.figure(figsize=(8, 5))

    plt.bar(categories, amounts)

    plt.title("Expenses by Category")
    plt.xlabel("Category")
    plt.ylabel("Total Amount")

    plt.show()
def search_expense():

    category = search_combo.get()

    if category == "":
        messagebox.showerror("Error", "Please select a category.")
        return

    for row in tree.get_children():
        tree.delete(row)

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM expenses WHERE category=?",
        (category,)
    )

    rows = cursor.fetchall()

    conn.close()

    for row in rows:
        tree.insert("", END, values=row)

def update_total():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0]

    conn.close()

    if total is None:
        total = 0

    total_label.config(text=f"Total Expense: ₹{total:.2f}")


def show_all():
    show_expenses()
    update_total()
    search_combo.set("")
# ---------------- Main Window ----------------

root = Tk()
root.title("Expense Tracker")
root.geometry("950x600")
root.resizable(False, False)

title = Label(root, text="Expense Tracker", font=("Arial", 20, "bold"), fg="blue")
title.pack(pady=10)

input_frame = Frame(root)
input_frame.pack(pady=10)

Label(input_frame, text="Date").grid(row=0, column=0, padx=10, pady=5)
date_entry = Entry(input_frame, width=20)
date_entry.grid(row=0, column=1)

Label(input_frame, text="Category").grid(row=0, column=2, padx=10)

category_combo = ttk.Combobox(
    input_frame,
    values=[
        "Food",
        "Travel",
        "Shopping",
        "Bills",
        "Entertainment",
        "Others"
    ],
    width=18,
    state="readonly"
)
category_combo.grid(row=0, column=3)

Label(input_frame, text="Description").grid(row=1, column=0, padx=10, pady=5)
description_entry = Entry(input_frame, width=20)
description_entry.grid(row=1, column=1)

Label(input_frame, text="Amount").grid(row=1, column=2)
amount_entry = Entry(input_frame, width=20)
amount_entry.grid(row=1, column=3)

button_frame = Frame(root)
button_frame.pack(pady=15)

Button(button_frame, text="Add Expense", width=15, command=add_expense).grid(row=0, column=0, padx=5)

Button(button_frame, text="Update", width=15, command=update_expense).grid(row=0, column=1, padx=5)

Button(
    button_frame,
    text="Delete",
    width=15,
    command=delete_expense
).grid(row=0, column=2, padx=5)

Button(
    button_frame,
    text="Clear",
    width=15,
    command=clear_fields
).grid(row=0, column=3, padx=5)

Button(
    button_frame,
    text="Export CSV",
    width=15,
    command=export_csv
).grid(row=0, column=4, padx=5)
Button(
    button_frame,
    text="Show Chart",
    width=15,
    command=show_chart
).grid(row=0, column=5, padx=5)

columns = ("ID", "Date", "Category", "Description",
           "Amount")
search_frame = Frame(root)
search_frame.pack(pady=10)

Label(search_frame, text="Search Category").grid(row=0, column=0, padx=5)

search_combo = ttk.Combobox(
    search_frame,
    values=[
        "Food",
        "Travel",
        "Shopping",
        "Bills",
        "Entertainment",
        "Others"
    ],
    width=18,
    state="readonly"
)

search_combo.grid(row=0, column=1, padx=5)
Button(
 search_frame,
  text="Search",
  width=12,
  command=search_expense
  ).grid(row=0, column=2, padx=5)
Button(
    search_frame,
    text="Show All",
    width=12,
    command=show_all
).grid(row=0, column=3, padx=5)
tree = ttk.Treeview(root, columns=columns, show="headings", height=15)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=170, anchor=CENTER)

tree.pack(pady=20)

tree.bind("<<TreeviewSelect>>", select_record)
total_label = Label(
    root,
    text="Total Expense: ₹0.00",
    font=("Arial", 14, "bold"),
    fg="green"
)

total_label.pack(pady=10)

show_expenses()

root.mainloop()