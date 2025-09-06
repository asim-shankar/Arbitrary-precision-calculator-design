import re

# ----------------------------
#  Helpers
# ----------------------------

def strip_leading_zeros(num: str) -> str:
    if '.' in num:
        num = num.rstrip('0').rstrip('.')
    return num.lstrip("0") or "0"


def normalize_decimals(a: str, b: str):
    """Make two decimals have the same number of digits after the dot."""
    if '.' not in a: a += '.0'
    if '.' not in b: b += '.0'
    int_a, frac_a = a.split('.')
    int_b, frac_b = b.split('.')
    max_len = max(len(frac_a), len(frac_b))
    frac_a = frac_a.ljust(max_len, '0')
    frac_b = frac_b.ljust(max_len, '0')
    return int_a + frac_a, int_b + frac_b, max_len


# ----------------------------
#  Big Integer Operations
# ----------------------------

def add_bigint(a: str, b: str) -> str:
    a, b = a[::-1], b[::-1]
    carry, result = 0, []
    for i in range(max(len(a), len(b))):
        digit_a = int(a[i]) if i < len(a) else 0
        digit_b = int(b[i]) if i < len(b) else 0
        s = digit_a + digit_b + carry
        result.append(str(s % 10))
        carry = s // 10
    if carry: result.append(str(carry))
    return strip_leading_zeros("".join(result[::-1]))


def sub_bigint(a: str, b: str) -> str:
    if a == b: return "0"
    a, b = a[::-1], b[::-1]
    result, borrow = [], 0
    for i in range(len(a)):
        digit_a = int(a[i])
        digit_b = int(b[i]) if i < len(b) else 0
        diff = digit_a - digit_b - borrow
        if diff < 0:
            diff += 10
            borrow = 1
        else:
            borrow = 0
        result.append(str(diff))
    return strip_leading_zeros("".join(result[::-1]))


def mul_bigint(a: str, b: str) -> str:
    if a == "0" or b == "0": return "0"
    a, b = a[::-1], b[::-1]
    result = [0] * (len(a) + len(b))
    for i in range(len(a)):
        for j in range(len(b)):
            result[i + j] += int(a[i]) * int(b[j])
            result[i + j + 1] += result[i + j] // 10
            result[i + j] %= 10
    while len(result) > 1 and result[-1] == 0: result.pop()
    return "".join(map(str, result[::-1]))


def div_bigint(a: str, b: str, precision=50) -> str:
    if b == "0": raise ZeroDivisionError("Division by zero")
    a, b = strip_leading_zeros(a), strip_leading_zeros(b)
    quotient, remainder = "", ""
    for digit in a:
        remainder += digit
        remainder = strip_leading_zeros(remainder)
        q = 0
        while int(remainder) >= int(b):
            remainder = str(int(remainder) - int(b))
            q += 1
        quotient += str(q)
    # add decimal places
    if remainder != "0":
        quotient += "."
        for _ in range(precision):
            remainder += "0"
            remainder = strip_leading_zeros(remainder)
            q = 0
            while int(remainder) >= int(b):
                remainder = str(int(remainder) - int(b))
                q += 1
            quotient += str(q)
            if remainder == "0": break
    return strip_leading_zeros(quotient)


# ----------------------------
#  Decimal-aware wrappers
# ----------------------------

def add_decimal(a, b):
    A, B, scale = normalize_decimals(a, b)
    result = add_bigint(A, B)
    if scale > 0:
        return result[:-scale] + "." + result[-scale:]
    return result

def sub_decimal(a, b):
    A, B, scale = normalize_decimals(a, b)
    if int(A) >= int(B):
        result = sub_bigint(A, B)
        if scale > 0:
            return result[:-scale] + "." + result[-scale:]
        return result
    else:
        result = sub_bigint(B, A)
        if scale > 0:
            return "-" + result[:-scale] + "." + result[-scale:]
        return "-" + result

def mul_decimal(a, b):
    int_a, frac_a = (a.split('.') + ["0"])[:2]
    int_b, frac_b = (b.split('.') + ["0"])[:2]
    scale = len(frac_a) + len(frac_b)
    result = mul_bigint(int_a + frac_a, int_b + frac_b)
    if scale > 0:
        result = result.zfill(scale+1)
        return result[:-scale] + "." + result[-scale:]
    return result

def div_decimal(a, b, precision=50):
    int_a, frac_a = (a.split('.') + ["0"])[:2]
    int_b, frac_b = (b.split('.') + ["0"])[:2]
    scale = max(len(frac_a), len(frac_b))
    A = (int_a + frac_a).ljust(len(int_a)+scale, "0")
    B = (int_b + frac_b).ljust(len(int_b)+scale, "0")
    return div_bigint(A, B, precision)


# ----------------------------
#  Expression Parsing & Eval
# ----------------------------

def precedence(op):
    if op in ('+', '-'): return 1
    if op in ('*', '/'): return 2
    return 0

def apply_op(a, b, op):
    if op == '+': return add_decimal(a, b)
    if op == '-': return sub_decimal(a, b)
    if op == '*': return mul_decimal(a, b)
    if op == '/': return div_decimal(a, b)
    raise ValueError("Unsupported operator")

def eval_expr(expr: str) -> str:
    tokens = re.findall(r'\d+(?:\.\d+)?|[+\-*/()]', expr.replace(" ", ""))
    values, ops = [], []

    def process():
        b, a = values.pop(), values.pop()
        values.append(apply_op(a, b, ops.pop()))

    for token in tokens:
        if re.match(r'^\d+(\.\d+)?$', token):
            values.append(token)
        elif token == '(':
            ops.append(token)
        elif token == ')':
            while ops and ops[-1] != '(':
                process()
            ops.pop()
        else:  # operator
            while ops and precedence(ops[-1]) >= precedence(token):
                process()
            ops.append(token)

    while ops: process()

    return strip_leading_zeros(values[0])
