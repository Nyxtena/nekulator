#!/usr/bin/env python3
"""
NEKULATOR -- Athena's Python calculator.
Basic arithmetic (+ - * / %), exponentiation (^), roots (sqrt),
parentheses, and full memory functions (MS / M+ / M- / MR / MC).

Run:  python3 nekulator.py
Requires: tkinter (ships with standard Python)
"""
import ast
import math
import operator as op
import tkinter as tk


# ---------------------------------------------------------------- safe evaluator
_BINOPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
           ast.Div: op.truediv, ast.Mod: op.mod, ast.Pow: op.pow}
_UNARYOPS = {ast.UAdd: op.pos, ast.USub: op.neg}
_FUNCS = {"sqrt": math.sqrt}


def _eval_node(node):
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
        return _BINOPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARYOPS:
        return _UNARYOPS[type(node.op)](_eval_node(node.operand))
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in _FUNCS and not node.keywords and len(node.args) == 1):
        return _FUNCS[node.func.id](_eval_node(node.args[0]))
    raise ValueError("unsupported expression")


def calculate(expr):
    """Evaluate an arithmetic expression safely (no eval())."""
    expr = expr.replace("^", "**").strip()
    if not expr:
        return ""
    result = _eval_node(ast.parse(expr, mode="eval"))
    if isinstance(result, float):
        result = round(result, 10)
        if result.is_integer():
            return str(int(result))
        return str(result)
    return str(result)


# ---------------------------------------------------------------------- GUI app
class Nekulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Nekulator")
        self.resizable(False, False)
        self.configure(bg="#1a1a2e")
        self.memory = 0.0
        self.fresh = True  # next digit starts a new entry

        # memory indicator
        self.mem_label = tk.Label(self, text="", bg="#1a1a2e", fg="#4ecdc4",
                                  font=("Helvetica", 10, "bold"), anchor="w")
        self.mem_label.grid(row=0, column=0, columnspan=5, sticky="w", padx=8)

        # display
        self.display = tk.Entry(self, font=("Helvetica", 24), justify="right",
                                bg="#16213e", fg="#ffffff", relief="flat",
                                insertbackground="#ffffff")
        self.display.grid(row=1, column=0, columnspan=5, sticky="nsew",
                          padx=8, pady=(0, 8), ipady=10)
        self.display.insert(0, "0")

        buttons = [
            # row, col, label, action
            (2, 0, "MC", self.mem_clear), (2, 1, "MR", self.mem_recall),
            (2, 2, "MS", self.mem_store), (2, 3, "M+", self.mem_add),
            (2, 4, "M-", self.mem_sub),
            (3, 0, "C", self.clear_all), (3, 1, "(", lambda: self.insert("(")),
            (3, 2, ")", lambda: self.insert(")")), (3, 3, "√", lambda: self.insert("sqrt(")),
            (3, 4, "^", lambda: self.insert("^")),
            (4, 0, "7", lambda: self.insert("7")), (4, 1, "8", lambda: self.insert("8")),
            (4, 2, "9", lambda: self.insert("9")), (4, 3, "/", lambda: self.insert("/")),
            (4, 4, "%", lambda: self.insert("%")),
            (5, 0, "4", lambda: self.insert("4")), (5, 1, "5", lambda: self.insert("5")),
            (5, 2, "6", lambda: self.insert("6")), (5, 3, "*", lambda: self.insert("*")),
            (5, 4, "⌫", self.backspace),
            (6, 0, "1", lambda: self.insert("1")), (6, 1, "2", lambda: self.insert("2")),
            (6, 2, "3", lambda: self.insert("3")), (6, 3, "-", lambda: self.insert("-")),
            (7, 0, "0", lambda: self.insert("0")), (7, 1, ".", lambda: self.insert(".")),
            (7, 2, "±", self.negate), (7, 3, "+", lambda: self.insert("+")),
        ]
        mem_keys = {"MC", "MR", "MS", "M+", "M-"}
        for r, c, label, action in buttons:
            bg = "#4ecdc4" if label in mem_keys else "#0f3460" if label == "=" else "#16213e"
            fg = "#1a1a2e" if label in mem_keys else "#ffffff"
            btn = tk.Button(self, text=label, command=action, font=("Helvetica", 14),
                            bg=bg, fg=fg, relief="flat", width=4, height=2,
                            activebackground="#e94560", activeforeground="#ffffff")
            btn.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")

        # tall equals key, classic style
        eq = tk.Button(self, text="=", command=self.equals, font=("Helvetica", 14),
                       bg="#0f3460", fg="#ffffff", relief="flat",
                       activebackground="#e94560", activeforeground="#ffffff")
        eq.grid(row=6, column=4, rowspan=2, padx=3, pady=3, sticky="nsew")

        # keyboard support
        self.bind("<Return>", lambda e: self.equals())
        self.bind("<KP_Enter>", lambda e: self.equals())
        self.bind("<BackSpace>", lambda e: self.backspace())
        self.bind("<Escape>", lambda e: self.clear_all())
        for ch in "0123456789.+-*/%^()":
            self.bind(ch, lambda e, k=ch: self.insert(k))

    # ------------------------------------------------------------- display ops
    def _get(self):
        return self.display.get()

    def _set(self, text):
        self.display.delete(0, tk.END)
        self.display.insert(0, text)
        self.fresh = False

    def insert(self, char):
        if self.fresh or self._get() in ("0", "Error"):
            self._set(char if char != "." else "0.")
        else:
            self._set(self._get() + char)

    def clear_all(self):
        self._set("0")
        self.fresh = True

    def backspace(self):
        text = self._get()
        self._set(text[:-1] if len(text) > 1 else "0")
        if self._get() == "0":
            self.fresh = True

    def negate(self):
        try:
            self._set(calculate(f"-({self._get()})"))
        except Exception:
            self._set("Error")
        self.fresh = True

    def equals(self):
        try:
            self._set(calculate(self._get()))
        except ZeroDivisionError:
            self._set("Error")
        except Exception:
            self._set("Error")
        self.fresh = True

    # ------------------------------------------------------------------ memory
    def _display_value(self):
        try:
            return float(calculate(self._get()))
        except Exception:
            return 0.0

    def _refresh_mem(self):
        self.mem_label.config(text="M" if self.memory != 0 else "")

    def mem_store(self):
        self.memory = self._display_value()
        self._refresh_mem()
        self.fresh = True

    def mem_add(self):
        self.memory += self._display_value()
        self._refresh_mem()
        self.fresh = True

    def mem_sub(self):
        self.memory -= self._display_value()
        self._refresh_mem()
        self.fresh = True

    def mem_recall(self):
        val = self.memory
        self._set(str(int(val)) if float(val).is_integer() else str(val))
        self.fresh = True

    def mem_clear(self):
        self.memory = 0.0
        self._refresh_mem()


if __name__ == "__main__":
    Nekulator().mainloop()
