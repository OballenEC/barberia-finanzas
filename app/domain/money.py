from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

CENT = Decimal("0.01")


class MoneyError(ValueError):
    pass


def to_decimal(value) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, str, float)):
        try:
            return Decimal(str(value))
        except InvalidOperation as e:
            raise MoneyError(f"Valor monetario inválido: {value!r}") from e
    raise MoneyError(f"Tipo no soportado para dinero: {type(value).__name__}")


def q2(value) -> Decimal:
    return to_decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


def fmt(value) -> str:
    return str(q2(value))


def parse_money(user_input: str, *, field: str = "importe") -> Decimal:
    if user_input is None or str(user_input).strip() == "":
        raise MoneyError(f"{field} es obligatorio")
    cleaned = str(user_input).replace(",", "").strip()
    try:
        d = Decimal(cleaned)
    except InvalidOperation as e:
        raise MoneyError(f"{field} no es un número válido: {user_input!r}") from e
    if d < 0:
        raise MoneyError(f"{field} no puede ser negativo")
    return q2(d)


def parse_positive_int(user_input: str, *, field: str = "cantidad") -> int:
    try:
        n = int(str(user_input).strip())
    except (TypeError, ValueError) as e:
        raise MoneyError(f"{field} debe ser un entero") from e
    if n <= 0:
        raise MoneyError(f"{field} debe ser mayor que cero")
    return n