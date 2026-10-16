import ttkbootstrap as tb
from ui import ExpenseTrackerApp

if __name__ == "__main__":

    root = tb.Window(themename="darkly")
    app = ExpenseTrackerApp(root)
    root.mainloop()