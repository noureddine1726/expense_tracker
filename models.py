class Expense:
    def __init__(self, amount, category, date, description, expense_id=None):
        self.id = expense_id
        self.amount = float(amount)
        self.category = category
        self.date = date
        self.description = description

    def to_tuple(self):
        return (self.id, self.amount, self.category, self.date, self.description)