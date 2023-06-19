import time


class MineStack:
    def __init__(self):
        self.stack = []

    def push(self, mine):
        if self.contains_element(mine):
            print("Element already exists in the stack. Cannot push.")
            return

        self.stack.append(mine)

    def pop(self):
        if not self.is_empty():
            return self.stack.pop()
        else:
            print("Stack is empty. Cannot pop.")
            return None

    def is_empty(self):
        return len(self.stack) == 0

    def contains_element(self, mine):
        for item in self.stack:
            if item == mine:
                return True
        return False

    def expire_elements(self, expiration_time=500):
        current_time = int(time.time())
        expired_elements = []

        for mine in self.stack:
            if current_time - mine.timestamp > expiration_time:
                expired_elements.append(mine)

        for expired_element in expired_elements:
            self.stack.remove(expired_element)

        return expired_elements

    def clear(self):
        self.stack = []

    def __repr__(self):
        return f"MineStack({self.stack})"

    def __str__(self):
        elements = [str(item) for item in self.stack]
        return "\n".join(elements)


class Mine:
    def __init__(self, position, timestamp=None, status=True):
        self.position = position
        self.status = status
        self.timestamp = timestamp or int(time.time())

    def __eq__(self, other):
        if isinstance(other, Mine):
            return self.position == other.position
        return False

    def __hash__(self):
        return hash(self.position)

    def __repr__(self):
        return f"Mine({self.position}, {self.status})"
