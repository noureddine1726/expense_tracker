import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def draw_pie_chart(parent_frame, category_totals):
    for widget in parent_frame.winfo_children():
        widget.destroy()

    if not category_totals or sum(category_totals.values()) == 0:
        return

    labels = list(category_totals.keys())
    sizes = list(category_totals.values())

    fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    ax.set_title("Expenses by Category")

    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)