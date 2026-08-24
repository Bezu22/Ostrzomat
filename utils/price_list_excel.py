from pathlib import Path
from copy import copy

from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter

import database


DEFAULT_EXCEL_PATH = Path("data") / "cennik.xlsx"

SHEETS = {
    "Narzędzia": (
        "category", "tool_type", "blades", "diam_min", "diam_max",
        "price_1", "price_2_4", "price_5_10", "price_11_20",
    ),
    "Powłoki": ("coating_name", "diam_max", "length", "price"),
    "Usługi": ("service_name", "param_min", "param_max", "price"),
    "Zakresy ilościowe": (
        "tool_type", "blades", "diam_min", "diam_max", "qty_min", "qty_max", "price"
    ),
}

HEADERS = {
    "Narzędzia": ("Kategoria", "Typ narzędzia", "Ostrza", "Średnica min",
                  "Średnica max", "Cena 1", "Cena 2-4", "Cena 5-10", "Cena 11+"),
    "Powłoki": ("Nazwa powłoki", "Średnica max", "Długość", "Cena"),
    "Usługi": ("Nazwa usługi", "Parametr min", "Parametr max", "Cena"),
    "Zakresy ilościowe": (
        "Typ narzędzia", "Ostrza", "Średnica min", "Średnica max",
        "Ilość min", "Ilość max", "Cena",
    ),
}

TABLES = {
    "Narzędzia": "pricelist_tools",
    "Powłoki": "pricelist_coatings",
    "Usługi": "pricelist_services",
    "Zakresy ilościowe": "pricelist_tool_ranges",
}


def export_pricelist(path=DEFAULT_EXCEL_PATH):
    """Eksportuje aktualny cennik SQLite do jednego, edytowalnego pliku XLSX."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    workbook.remove(workbook.active)

    connection = database.get_connection()
    try:
        for sheet_name, columns in SHEETS.items():
            sheet = workbook.create_sheet(sheet_name)
            sheet.append(HEADERS[sheet_name])
            table = TABLES[sheet_name]
            if sheet_name == "Zakresy ilościowe":
                database.ensure_tool_ranges_table(connection)
            rows = connection.execute(
                f"SELECT {', '.join(columns)} FROM {table} ORDER BY id"
            ).fetchall()
            if sheet_name == "Zakresy ilościowe" and not rows:
                legacy_rows = connection.execute(
                    "SELECT tool_type, blades, diam_min, diam_max, price_1, price_2_4, price_5_10, price_11_20 "
                    "FROM pricelist_tools ORDER BY id"
                ).fetchall()
                ranges = ((1, 1), (2, 4), (5, 10), (11, 999999))
                rows = [
                    (tool_type, blades, diam_min, diam_max, qty_min, qty_max, prices[index])
                    for tool_type, blades, diam_min, diam_max, *prices in legacy_rows
                    for index, (qty_min, qty_max) in enumerate(ranges)
                ]
            for row in rows:
                sheet.append(list(row))
            sheet.freeze_panes = "A2"
            sheet.auto_filter.ref = sheet.dimensions
            for cell in sheet[1]:
                font = copy(cell.font)
                font.bold = True
                cell.font = font
            for column in sheet.columns:
                sheet.column_dimensions[column[0].column_letter].width = max(
                    12, min(28, max(len(str(cell.value or "")) for cell in column) + 2)
                )
    finally:
        connection.close()
    workbook.save(path)
    return path


def import_pricelist(path=DEFAULT_EXCEL_PATH):
    """Waliduje i importuje wszystkie arkusze XLSX do SQLite w jednej transakcji."""
    parsed = read_pricelist(path)

    connection = database.get_connection()
    try:
        connection.execute("BEGIN")
        for sheet_name, rows in parsed.items():
            table = TABLES[sheet_name]
            if sheet_name == "Zakresy ilościowe":
                database.ensure_tool_ranges_table(connection)
            connection.execute(f"DELETE FROM {table}")
            placeholders = ", ".join("?" for _ in SHEETS[sheet_name])
            connection.executemany(
                f"INSERT INTO {table} ({', '.join(SHEETS[sheet_name])}) VALUES ({placeholders})",
                rows,
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    return {sheet_name: len(rows) for sheet_name, rows in parsed.items()}


def read_pricelist(path=DEFAULT_EXCEL_PATH):
    """Wczytuje, typuje i sprawdza cały skoroszyt bez zapisu do bazy."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Brak pliku cennika: {path}")

    workbook = load_workbook(path, data_only=True, read_only=True)
    try:
        parsed = {}
        for sheet_name, columns in SHEETS.items():
            if sheet_name not in workbook.sheetnames:
                raise ValueError(f"Brak arkusza '{sheet_name}'")
            rows = workbook[sheet_name].iter_rows(values_only=True)
            header = tuple(next(rows, ()))
            if header != HEADERS[sheet_name]:
                raise ValueError(f"Nieprawidłowe nagłówki arkusza '{sheet_name}'")
            parsed[sheet_name] = []
            for row_number, row in enumerate(rows, start=2):
                if any(row):
                    try:
                        parsed[sheet_name].append(_parse_row(sheet_name, row, columns, row_number))
                    except ValueError as error:
                        raise ValueError(f"{sheet_name}!A{row_number}: {error}") from error
    finally:
        workbook.close()

    _validate_pricelist(parsed)
    return parsed


def _validate_pricelist(parsed):
    tool_keys = {(row[1], row[2]) for row in parsed["Narzędzia"]}
    for sheet_name, rows in parsed.items():
        for row_number, row in enumerate(rows, start=2):
            if sheet_name == "Narzędzia":
                min_index, max_index = 3, 4
                quantity_range = None
            elif sheet_name == "Zakresy ilościowe":
                min_index, max_index = 2, 3
                quantity_range = (4, 5)
            else:
                min_index, max_index = 1, 2
                quantity_range = None
            min_cell = get_column_letter(min_index + 1)
            max_cell = get_column_letter(max_index + 1)
            if row[min_index] > row[max_index]:
                raise ValueError(f"{sheet_name}!{min_cell}{row_number}/{max_cell}{row_number}: minimum jest większe od maksimum")
            if quantity_range and row[quantity_range[0]] > row[quantity_range[1]]:
                raise ValueError(f"{sheet_name}!E{row_number}/F{row_number}: ilość min jest większa od ilości max")
            if any(value < 0 for value in row[min_index:max_index + 1]):
                raise ValueError(f"{sheet_name}!{min_cell}{row_number}:{max_cell}{row_number}: zakres nie może być ujemny")
            if quantity_range:
                if (row[0], row[1]) not in tool_keys:
                    raise ValueError(f"{sheet_name}!A{row_number}: brak narzędzia w arkuszu Narzędzia")
                if any(
                    value != int(value) or value < 1
                    for value in row[quantity_range[0]:quantity_range[1] + 1]
                ):
                    raise ValueError(f"{sheet_name}!E{row_number}: ilości muszą być dodatnimi liczbami całkowitymi")
            price_start = quantity_range[1] + 1 if quantity_range else max_index + 1
            if any(value < 0 for value in row[price_start:]):
                raise ValueError(f"{sheet_name}!{get_column_letter(price_start + 1)}{row_number}: cena nie może być ujemna")

    ranges = parsed["Zakresy ilościowe"]
    for index, current in enumerate(ranges):
        for other in ranges[index + 1:]:
            same_key = current[:2] == other[:2]
            diam_overlap = current[2] <= other[3] and other[2] <= current[3]
            quantity_overlap = current[4] <= other[5] and other[4] <= current[5]
            if same_key and diam_overlap and quantity_overlap:
                first_row = index + 2
                second_row = ranges.index(other) + 2
                raise ValueError(
                    f"Zakresy ilościowe!A{first_row}:G{first_row}/A{second_row}:G{second_row}: "
                    "zakresy nakładają się dla tego samego narzędzia"
                )


def _parse_row(sheet_name, row, columns, row_number):
    if len(row) != len(columns) or any(value is None for value in row):
        missing_index = next((index for index, value in enumerate(row) if value is None), 0)
        raise ValueError(f"Niepełna wartość w komórce {get_column_letter(missing_index + 1)}{row_number}")
    values = list(row)
    if sheet_name == "Narzędzia":
        values[0:3] = [str(value).strip() for value in values[0:3]]
        numeric_start = 3
    elif sheet_name == "Zakresy ilościowe":
        values[0:2] = [str(value).strip() for value in values[0:2]]
        numeric_start = 2
    else:
        values[0] = str(values[0]).strip()
        numeric_start = 1
    try:
        for index in range(numeric_start, len(values)):
            values[index] = float(values[index])
    except (TypeError, ValueError) as error:
        raise ValueError(f"Nieprawidłowa liczba w komórce {get_column_letter(index + 1)}{row_number}") from error
    return tuple(values)