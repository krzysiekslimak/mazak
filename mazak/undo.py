class Command:
    def __init__(self, undo_fn, redo_fn):
        self._undo_fn = undo_fn
        self._redo_fn = redo_fn

    def undo(self):
        self._undo_fn()

    def redo(self):
        self._redo_fn()


class CompositeCommand(Command):
    def __init__(self, commands):
        super().__init__(self._undo_all, self._redo_all)
        self._commands = commands

    def _undo_all(self):
        for command in reversed(self._commands):
            command.undo()

    def _redo_all(self):
        for command in self._commands:
            command.redo()


class UndoManager:
    def __init__(self):
        self._undo_stack = []
        self._redo_stack = []

    def push(self, command: Command):
        self._undo_stack.append(command)
        self._redo_stack.clear()

    def undo(self):
        if not self._undo_stack:
            return
        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)

    def redo(self):
        if not self._redo_stack:
            return
        command = self._redo_stack.pop()
        command.redo()
        self._undo_stack.append(command)

    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    def can_redo(self) -> bool:
        return bool(self._redo_stack)

    def clear(self):
        self._undo_stack.clear()
        self._redo_stack.clear()
