import uuid
import sqlite3
from werkzeug.exceptions import UnprocessableEntity, InternalServerError

class StackError(InternalServerError):
    pass


class OperationError(UnprocessableEntity):
    pass


class Operations:
    @staticmethod
    def add(stack):
        if len(stack) < 2:
            raise StackError('Insufficient operands in stack')
        right = stack.pop()
        left = stack.pop()
        stack.append(left + right)

    @staticmethod
    def subtract(stack):
        if len(stack) < 2:
            raise StackError('Insufficient operands in stack')
        right = stack.pop()
        left = stack.pop()
        stack.append(left - right)

    @staticmethod
    def multiply(stack):
        if len(stack) < 2:
            raise StackError('Insufficient operands in stack')
        right = stack.pop()
        left = stack.pop()
        stack.append(left * right)

    @staticmethod
    def divide(stack):
        if len(stack) < 2:
            raise StackError('Insufficient operands in stack')
        right = stack.pop()
        left = stack.pop()
        if right == 0:
            raise StackError('Division by zero')
        stack.append(left / right)


OPERATIONS = {
    'add': Operations.add,
    'subtract': Operations.subtract,
    'multiply': Operations.multiply,
    'divide': Operations.divide,
}


class StackService:
    def __init__(self):
        self.conn = sqlite3.connect('stacks.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS stacks (id TEXT PRIMARY KEY, stack_values TEXT)''')
        self.conn.commit()

    def create_stack(self):
        stack_id = str(uuid.uuid4())
        try:
            self.cursor.execute("INSERT INTO stacks (id, stack_values) VALUES (?, ?)", (stack_id, "[]"))
            self.conn.commit()
            return stack_id
        except sqlite3.IntegrityError:
            raise StackError('Stack already exists')

    def get_stacks(self):
        self.cursor.execute("SELECT * FROM stacks")
        stacks = {row[0]: eval(row[1]) for row in self.cursor.fetchall()}
        return stacks

    def get_stack(self, stack_id):
        self.cursor.execute("SELECT stack_values FROM stacks WHERE id = ?", (stack_id,))
        row = self.cursor.fetchone()
        if row:
            return eval(row[0])
        else:
            raise StackError(f'Stack with id {stack_id} does not exist')

    def update_stack(self, stack_id, new_values):
        if not isinstance(new_values, list):
            raise StackError('New values must be a list')
        self.cursor.execute("UPDATE stacks SET stack_values = ? WHERE id = ?", (str(new_values), stack_id))
        if self.cursor.rowcount == 0:
            raise StackError(f'Stack with id {stack_id} does not exist')
        self.conn.commit()
        return new_values

    def do_operation(self, stack_id, operation):
        if operation not in OPERATIONS:
            raise OperationError('Invalid operation')

        self.cursor.execute("SELECT stack_values FROM stacks WHERE id = ?", (stack_id,))
        row = self.cursor.fetchone()
        if not row:
            raise StackError(f'Stack with id {stack_id} does not exist')

        stack = eval(row[0])
        operation_func = OPERATIONS[operation]
        operation_func(stack)
        self.cursor.execute("UPDATE stacks SET stack_values = ? WHERE id = ?", (str(stack), stack_id))
        self.conn.commit()
        return stack

    def push_stack(self, stack_id, value):
        self.cursor.execute("SELECT stack_values FROM stacks WHERE id = ?", (stack_id,))
        row = self.cursor.fetchone()
        if not row:
            raise StackError(f'Stack with id {stack_id} does not exist')

        stack = eval(row[0])
        stack.append(value)
        self.cursor.execute("UPDATE stacks SET stack_values = ? WHERE id = ?", (str(stack), stack_id))
        self.conn.commit()
        return stack

    def delete_stack(self, stack_id):
        self.cursor.execute("DELETE FROM stacks WHERE id = ?", (stack_id,))
        if self.cursor.rowcount == 0:
            raise StackError(f'Stack with id {stack_id} does not exist')
        self.conn.commit()
