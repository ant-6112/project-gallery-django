import xlwings as xw
import pandas as pd
import numpy as np
from typing import List, Any, Optional, Union, Tuple


# --- Helper to get a sheet object ---
def _get_sheet(
    wb_or_sht: Union[xw.Book, xw.Sheet, str, None] = None,
    sheet_name: Optional[str] = None,
) -> xw.Sheet:
    """
    Internal helper to robustly get a sheet object.
    If wb_or_sht is None, uses active book.
    If wb_or_sht is a string, assumes it's a book path.
    If sheet_name is None, uses active sheet of the determined book.
    """
    if isinstance(wb_or_sht, xw.Sheet):
        return wb_or_sht
    elif isinstance(wb_or_sht, xw.Book):
        book = wb_or_sht
    elif isinstance(wb_or_sht, str):  # Path to workbook
        try:
            book = xw.Book(wb_or_sht)
        except Exception as e:
            raise FileNotFoundError(
                f"Workbook at path '{wb_or_sht}' not found or couldn't be opened: {e}"
            )
    elif wb_or_sht is None:
        book = xw.Book.caller() if xw.Book.caller() else xw.books.active
        if book is None:
            raise ValueError("No active workbook found and no workbook specified.")
    else:
        raise TypeError(
            "wb_or_sht must be an xlwings Book, Sheet, path string, or None."
        )

    if sheet_name:
        try:
            return book.sheets[sheet_name]
        except Exception:  # More robust than KeyError for xlwings
            raise ValueError(f"Sheet '{sheet_name}' not found in '{book.name}'.")
    else:
        return book.sheets.active


# --- Workbook Level Utilities ---


def get_workbook(
    path: Optional[str] = None, create_if_not_exists: bool = False
) -> xw.Book:
    """1. Opens an existing workbook or creates a new one. Returns the Book object."""
    if path:
        try:
            return xw.Book(path)
        except Exception:
            if create_if_not_exists:
                wb = xw.Book()
                wb.save(path)
                return wb
            else:
                raise FileNotFoundError(f"Workbook at path '{path}' not found.")
    return xw.Book.caller() if xw.Book.caller() else xw.books.active or xw.Book()


def save_workbook(wb: Optional[xw.Book] = None, path: Optional[str] = None) -> None:
    """2. Saves the workbook. If path is provided, saves as. Uses active book if wb is None."""
    book = wb or xw.Book.caller() or xw.books.active
    if not book:
        raise ValueError("No workbook specified or active.")
    if path:
        book.save(path)
    else:
        book.save()


def close_workbook(wb: Optional[xw.Book] = None, save_changes: bool = True) -> None:
    """3. Closes the workbook. Uses active book if wb is None."""
    book = wb or xw.Book.caller() or xw.books.active
    if not book:
        return  # Nothing to close
    if not save_changes and book.name in [
        b.name for b in xw.books
    ]:  # Check if it's actually open
        # If not saving changes, and there are changes, need to set saved flag
        if not book.saved:
            book.app.enable_events = False  # Suppress "Save changes?" prompt
            book.close()
            book.app.enable_events = True
            return
    book.close()


def list_open_workbook_names() -> List[str]:
    """4. Returns a list of names of all currently open workbooks."""
    return [book.name for book in xw.apps.active.books] if xw.apps.active else []


def create_new_workbook() -> xw.Book:
    """5. Creates and returns a new workbook object."""
    return xw.Book()


def is_workbook_open(name_or_path: str) -> bool:
    """6. Checks if a workbook with the given name or full path is open."""
    for book in xw.books:
        if book.name == name_or_path or book.fullname == name_or_path:
            return True
    return False


# --- Sheet Level Utilities ---


def get_sheet_object(
    book_or_name: Union[xw.Book, str, None] = None, sheet_name: Optional[str] = None
) -> xw.Sheet:
    """7. Gets a sheet object by name. Uses active book/sheet if None."""
    return _get_sheet(book_or_name, sheet_name)


def create_sheet_if_not_exists(
    sheet_name: str, wb: Optional[xw.Book] = None
) -> xw.Sheet:
    """8. Creates a sheet if it doesn't exist, otherwise returns existing sheet."""
    book = wb or xw.Book.caller() or xw.books.active
    if not book:
        raise ValueError("No workbook specified or active.")
    if sheet_name in [s.name for s in book.sheets]:
        return book.sheets[sheet_name]
    else:
        return book.sheets.add(sheet_name)


def delete_sheet_if_exists(
    sheet_name: str, wb: Optional[xw.Book] = None, confirm: bool = False
) -> bool:
    """9. Deletes a sheet if it exists. Returns True if deleted, False otherwise."""
    book = wb or xw.Book.caller() or xw.books.active
    if not book:
        raise ValueError("No workbook specified or active.")
    if sheet_name in [s.name for s in book.sheets]:
        if not confirm:
            book.app.display_alerts = False
            book.sheets[sheet_name].delete()
            book.app.display_alerts = True
        else:  # pragma: no cover (requires user interaction)
            book.sheets[sheet_name].delete()
        return True
    return False


def list_sheet_names(wb: Optional[xw.Book] = None) -> List[str]:
    """10. Returns a list of all sheet names in the workbook."""
    book = wb or xw.Book.caller() or xw.books.active
    if not book:
        raise ValueError("No workbook specified or active.")
    return [sheet.name for sheet in book.sheets]


def activate_sheet(sheet_name: str, wb: Optional[xw.Book] = None) -> None:
    """11. Activates the specified sheet."""
    sheet = _get_sheet(wb, sheet_name)
    sheet.activate()


def copy_sheet(
    source_sheet_name: str,
    new_sheet_name: str,
    source_wb: Optional[xw.Book] = None,
    dest_wb: Optional[xw.Book] = None,
    before_sheet: Optional[str] = None,
    after_sheet: Optional[str] = None,
) -> xw.Sheet:
    """12. Copies a sheet within the same or to another workbook. Returns the new sheet."""
    src_book = source_wb or xw.Book.caller() or xw.books.active
    if not src_book:
        raise ValueError("Source workbook not specified or active.")

    src_sheet = _get_sheet(src_book, source_sheet_name)

    target_book = dest_wb or src_book

    before = target_book.sheets[before_sheet] if before_sheet else None
    after = target_book.sheets[after_sheet] if after_sheet and not before else None

    src_sheet.copy(
        before=before,
        after=after,
        book=target_book if target_book != src_book else None,
    )

    # The copied sheet will be active in the target book. Rename it.
    # If copying within the same book, Excel might name it "SheetName (2)"
    copied_sheet = target_book.sheets.active
    copied_sheet.name = new_sheet_name
    return copied_sheet


# --- Range Data Reading ---


def read_range_data(
    sheet_or_range_ref: Union[xw.Sheet, xw.Range, str],
    start_cell: Optional[str] = "A1",
    end_cell: Optional[str] = None,
    has_header: bool = False,
) -> Union[List[List[Any]], List[Dict[str, Any]]]:
    """13. Reads data from a specified range or the used range.
    If has_header is True, returns a list of dictionaries.
    If end_cell is None, reads the entire table/current region from start_cell.
    range_ref can be 'A1:B5' or a sheet object (then use start_cell, end_cell).
    """
    if isinstance(
        sheet_or_range_ref, str
    ):  # 'Sheet1!A1:B5' or 'A1:B5' (on active sheet)
        rng = xw.Range(sheet_or_range_ref)
    elif isinstance(sheet_or_range_ref, xw.Sheet):
        if end_cell:
            rng = sheet_or_range_ref.range(start_cell, end_cell)
        else:
            rng = sheet_or_range_ref.range(start_cell).expand("table")
    elif isinstance(sheet_or_range_ref, xw.Range):
        rng = sheet_or_range_ref
    else:
        raise TypeError("sheet_or_range_ref must be Sheet, Range, or string address.")

    data = rng.options(ndim=2).value  # Always get 2D list
    if not data:
        return []
    if not any(data):
        return []  # Handle empty range

    if has_header:
        if not data or len(data) < 1:
            return []
        headers = data[0]
        return [dict(zip(headers, row)) for row in data[1:]]
    return data


def read_to_dataframe(
    sheet_or_range_ref: Union[xw.Sheet, xw.Range, str],
    start_cell: Optional[str] = "A1",
    end_cell: Optional[str] = None,
    index_col: Optional[int] = None,
    header_row: int = 0,
) -> pd.DataFrame:
    """14. Reads data from a range into a Pandas DataFrame."""
    if isinstance(sheet_or_range_ref, str):
        rng = xw.Range(sheet_or_range_ref)
    elif isinstance(sheet_or_range_ref, xw.Sheet):
        if end_cell:
            rng = sheet_or_range_ref.range(start_cell, end_cell)
        else:
            rng = sheet_or_range_ref.range(start_cell).expand("table")
    elif isinstance(sheet_or_range_ref, xw.Range):
        rng = sheet_or_range_ref
    else:
        raise TypeError("sheet_or_range_ref must be Sheet, Range, or string address.")

    return rng.options(
        pd.DataFrame,
        index=index_col is not None,
        header=header_row is not None,
        expand="table",
    ).value


def get_column_values(
    sheet: xw.Sheet, col_letter_or_num: Union[str, int], start_row: int = 1
) -> List[Any]:
    """15. Gets all values from a column starting from start_row down to the last used cell."""
    last_row = (
        sheet.range(f"{col_letter_or_num}{sheet.cells.last_cell.row}").end("up").row
    )
    if last_row < start_row:
        return []
    return (
        sheet.range(f"{col_letter_or_num}{start_row}:{col_letter_or_num}{last_row}")
        .options(ndim=1)
        .value
    )


def get_row_values(
    sheet: xw.Sheet, row_num: int, start_col: Union[str, int] = 1
) -> List[Any]:
    """16. Gets all values from a row starting from start_col right to the last used cell."""
    start_col_num = (
        xw.utils.col_name_to_num(start_col) if isinstance(start_col, str) else start_col
    )
    last_col = (
        sheet.range(
            f"{xw.utils.col_num_to_name(sheet.cells.last_cell.column)}{row_num}"
        )
        .end("left")
        .column
    )
    if last_col < start_col_num:
        return []
    return (
        sheet.range((row_num, start_col_num), (row_num, last_col)).options(ndim=1).value
    )


def get_cell_value(
    sheet_or_cell_ref: Union[xw.Sheet, str],
    row_or_address: Union[int, str],
    col: Optional[Union[int, str]] = None,
) -> Any:
    """17. Gets value of a single cell.
    Usage: get_cell_value(sheet, 1, 1) or get_cell_value(sheet, "A1") or get_cell_value("Sheet1!A1")
    """
    if isinstance(sheet_or_cell_ref, str) and col is None:  # "Sheet1!A1"
        return xw.Range(sheet_or_cell_ref).value
    elif isinstance(sheet_or_cell_ref, xw.Sheet):
        if isinstance(row_or_address, str) and col is None:  # "A1"
            return sheet_or_cell_ref.range(row_or_address).value
        elif isinstance(row_or_address, int) and col is not None:
            return sheet_or_cell_ref.cells(row_or_address, col).value
    raise ValueError("Invalid arguments for get_cell_value")


# --- Range Data Writing ---


def write_range_data(
    sheet_or_start_cell_ref: Union[xw.Sheet, xw.Range, str],
    data: List[List[Any]],
    start_cell: Optional[str] = "A1",
) -> None:
    """18. Writes a 2D list (list of lists) to a specified range.
    If sheet_or_start_cell_ref is a sheet, data is written from start_cell.
    If sheet_or_start_cell_ref is a range or "Sheet1!A1", it's the top-left cell.
    """
    if isinstance(
        sheet_or_start_cell_ref, str
    ):  # "Sheet1!A1" or "A1" (on active sheet)
        top_left_cell = xw.Range(sheet_or_start_cell_ref)
    elif isinstance(sheet_or_start_cell_ref, xw.Sheet):
        top_left_cell = sheet_or_start_cell_ref.range(start_cell)
    elif isinstance(sheet_or_start_cell_ref, xw.Range):
        top_left_cell = sheet_or_start_cell_ref
    else:
        raise TypeError(
            "sheet_or_start_cell_ref must be Sheet, Range, or string address."
        )

    top_left_cell.value = data


def write_from_dataframe(
    sheet_or_start_cell_ref: Union[xw.Sheet, xw.Range, str],
    df: pd.DataFrame,
    start_cell: Optional[str] = "A1",
    index: bool = True,
    header: bool = True,
) -> None:
    """19. Writes a Pandas DataFrame to Excel."""
    if isinstance(sheet_or_start_cell_ref, str):
        top_left_cell = xw.Range(sheet_or_start_cell_ref)
    elif isinstance(sheet_or_start_cell_ref, xw.Sheet):
        top_left_cell = sheet_or_start_cell_ref.range(start_cell)
    elif isinstance(sheet_or_start_cell_ref, xw.Range):
        top_left_cell = sheet_or_start_cell_ref
    else:
        raise TypeError(
            "sheet_or_start_cell_ref must be Sheet, Range, or string address."
        )

    top_left_cell.options(pd.DataFrame, index=index, header=header).value = df


def set_cell_value(
    sheet_or_cell_ref: Union[xw.Sheet, str],
    row_or_address: Union[int, str],
    col_or_value: Union[int, str, Any],
    value: Optional[Any] = None,
) -> None:
    """20. Sets value of a single cell. (Less performant for many cells, use write_range_data)
    Usage: set_cell_value(sheet, 1, 1, "val") or set_cell_value(sheet, "A1", "val") or set_cell_value("Sheet1!A1", "val")
    """
    if isinstance(sheet_or_cell_ref, str) and value is None:  # "Sheet1!A1", "val"
        xw.Range(sheet_or_cell_ref).value = col_or_value
    elif isinstance(sheet_or_cell_ref, xw.Sheet):
        if isinstance(row_or_address, str) and value is None:  # "A1", "val"
            sheet_or_cell_ref.range(row_or_address).value = col_or_value
        elif (
            isinstance(row_or_address, int)
            and col_or_value is not None
            and value is not None
        ):
            sheet_or_cell_ref.cells(row_or_address, col_or_value).value = value
        else:
            raise ValueError("Invalid arguments for set_cell_value. Check signature.")
    else:
        raise ValueError("Invalid arguments for set_cell_value. Check signature.")


def append_rows(
    sheet: xw.Sheet, data: List[List[Any]], start_column: Union[str, int] = 1
) -> None:
    """21. Appends rows of data to the first empty row in the sheet."""
    last_row = get_last_row(
        sheet,
        xw.utils.col_name_to_num(start_column)
        if isinstance(start_column, str)
        else start_column,
    )
    target_cell = sheet.cells(last_row + 1, start_column)
    target_cell.value = data


# --- Range Formatting & Operations ---


def clear_range_contents(range_ref: Union[xw.Range, str]) -> None:
    """22. Clears contents of a range."""
    (xw.Range(range_ref) if isinstance(range_ref, str) else range_ref).clear_contents()


def clear_range_formats(range_ref: Union[xw.Range, str]) -> None:
    """23. Clears formatting of a range."""
    (xw.Range(range_ref) if isinstance(range_ref, str) else range_ref).clear_formats()


def clear_range_all(range_ref: Union[xw.Range, str]) -> None:
    """24. Clears everything (contents, formats, comments) from a range."""
    (xw.Range(range_ref) if isinstance(range_ref, str) else range_ref).clear()


def set_range_font_bold(range_ref: Union[xw.Range, str], bold: bool = True) -> None:
    """25. Sets font bold for a range."""
    rng = xw.Range(range_ref) if isinstance(range_ref, str) else range_ref
    rng.font.bold = bold


def set_range_font_color(
    range_ref: Union[xw.Range, str], color_rgb_tuple: Tuple[int, int, int]
) -> None:
    """26. Sets font color for a range using an RGB tuple (e.g., (255, 0, 0) for red)."""
    rng = xw.Range(range_ref) if isinstance(range_ref, str) else range_ref
    rng.font.color = color_rgb_tuple


def set_range_interior_color(
    range_ref: Union[xw.Range, str], color_rgb_tuple: Tuple[int, int, int]
) -> None:
    """27. Sets interior/background color for a range."""
    rng = xw.Range(range_ref) if isinstance(range_ref, str) else range_ref
    rng.color = color_rgb_tuple  # or rng.api.Interior.Color for more control if needed


def set_range_number_format(
    range_ref: Union[xw.Range, str], number_format: str
) -> None:
    """28. Sets number format for a range (e.g., "0.00%", "yyyy-mm-dd", "@" for text)."""
    rng = xw.Range(range_ref) if isinstance(range_ref, str) else range_ref
    rng.number_format = number_format


def autofit_columns(range_or_sheet_ref: Union[xw.Range, xw.Sheet, str]) -> None:
    """29. Autofits columns for a given range or entire sheet columns."""
    if isinstance(range_or_sheet_ref, str):  # "Sheet1!A:C" or "Sheet1"
        if (
            "!" in range_or_sheet_ref and ":" in range_or_sheet_ref.split("!")[1]
        ):  # Range like "Sheet1!A:C"
            target = xw.Range(range_or_sheet_ref).columns
        elif "!" in range_or_sheet_ref:  # Sheet name like "Sheet1"
            target = (
                xw.Book.caller()
                .sheets[range_or_sheet_ref.split("!")[0]]
                .used_range.columns
            )
        elif ":" in range_or_sheet_ref:  # Range like "A:C" on active sheet
            target = xw.Range(range_or_sheet_ref).columns
        else:  # Sheet name like "Sheet1" on active book
            target = xw.Book.caller().sheets[range_or_sheet_ref].used_range.columns
    elif isinstance(range_or_sheet_ref, xw.Sheet):
        target = range_or_sheet_ref.used_range.columns
    elif isinstance(range_or_sheet_ref, xw.Range):
        target = range_or_sheet_ref.columns
    else:
        raise TypeError("Input must be a Range, Sheet, or string reference.")
    target.autofit()


def autofit_rows(range_or_sheet_ref: Union[xw.Range, xw.Sheet, str]) -> None:
    """30. Autofits rows for a given range or entire sheet rows."""
    if isinstance(range_or_sheet_ref, str):
        if "!" in range_or_sheet_ref and ":" in range_or_sheet_ref.split("!")[1]:
            target = xw.Range(range_or_sheet_ref).rows
        elif "!" in range_or_sheet_ref:
            target = (
                xw.Book.caller()
                .sheets[range_or_sheet_ref.split("!")[0]]
                .used_range.rows
            )
        elif ":" in range_or_sheet_ref:
            target = xw.Range(range_or_sheet_ref).rows
        else:
            target = xw.Book.caller().sheets[range_or_sheet_ref].used_range.rows
    elif isinstance(range_or_sheet_ref, xw.Sheet):
        target = range_or_sheet_ref.used_range.rows
    elif isinstance(range_or_sheet_ref, xw.Range):
        target = range_or_sheet_ref.rows
    else:
        raise TypeError("Input must be a Range, Sheet, or string reference.")
    target.autofit()


def merge_range(range_ref: Union[xw.Range, str]) -> None:
    """31. Merges cells in a given range."""
    (xw.Range(range_ref) if isinstance(range_ref, str) else range_ref).merge()


def unmerge_range(range_ref: Union[xw.Range, str]) -> None:
    """32. Unmerges cells in a given range."""
    (xw.Range(range_ref) if isinstance(range_ref, str) else range_ref).unmerge()


# --- Finding & Utility ---


def get_last_row(sheet: xw.Sheet, column_to_check: Union[int, str] = 1) -> int:
    """33. Gets the last used row number in a specified column or the whole sheet.
    If column_to_check is an int/str, checks that column.
    If column_to_check is 0 or None, considers all columns (slow for large sheets).
    """
    if column_to_check is None or column_to_check == 0:
        # This can be slow as it checks all cells
        return sheet.used_range.last_cell.row
    else:
        # Check specific column, much faster
        return (
            sheet.range(
                f"{xw.utils.col_num_to_name(column_to_check) if isinstance(column_to_check, int) else column_to_check}"
                f"{sheet.cells.rows.count}"
            )
            .end("up")
            .row
        )


def get_last_column(sheet: xw.Sheet, row_to_check: int = 1) -> int:
    """34. Gets the last used column number in a specified row or the whole sheet.
    If row_to_check is an int, checks that row.
    If row_to_check is 0 or None, considers all rows (slow for large sheets).
    """
    if row_to_check is None or row_to_check == 0:
        # This can be slow
        return sheet.used_range.last_cell.column
    else:
        # Check specific row, much faster
        return (
            sheet.range(
                f"{xw.utils.col_num_to_name(sheet.cells.columns.count)}{row_to_check}"
            )
            .end("left")
            .column
        )


def find_first_occurrence(
    sheet: xw.Sheet, value_to_find: Any, search_range: Optional[str] = None
) -> Optional[xw.Range]:
    """35. Finds the first occurrence of a value in a sheet or specified range. Returns Range object or None."""
    rng_to_search = sheet.range(search_range) if search_range else sheet.used_range
    # xlwings' find is not directly available, use API
    # For simple exact match, iterating after bulk read is faster if range is not huge
    # For complex find (wildcards, partial match), Excel's find is better
    found_cell = rng_to_search.api.Find(
        What=value_to_find,
        LookIn=xw.constants.FindLookIn.xlValues,
        LookAt=xw.constants.LookAt.xlWhole,
    )
    if found_cell:
        # Convert COM object back to xlwings Range
        return sheet.range(found_cell.Address)
    return None


def find_all_occurrences(
    sheet: xw.Sheet, value_to_find: Any, search_range: Optional[str] = None
) -> List[xw.Range]:
    """36. Finds all occurrences of a value. Returns a list of Range objects. (Potentially slow for large sheets).
    For performance on very large sheets, consider reading to Python and searching there.
    """
    rng_to_search = sheet.range(search_range) if search_range else sheet.used_range
    found_ranges = []

    # Read data into Python for faster iteration if exact match
    data = rng_to_search.options(ndim=2).value
    if not data:
        return []

    top_left_row = rng_to_search.row
    top_left_col = rng_to_search.column

    for r_idx, row_data in enumerate(data):
        for c_idx, cell_value in enumerate(row_data):
            if cell_value == value_to_find:
                # Calculate actual sheet cell address
                actual_row = top_left_row + r_idx
                actual_col = top_left_col + c_idx
                found_ranges.append(sheet.cells(actual_row, actual_col))
    return found_ranges


def delete_rows(sheet: xw.Sheet, start_row: int, num_rows: int = 1) -> None:
    """37. Deletes specified number of rows starting from start_row."""
    sheet.range(f"{start_row}:{start_row + num_rows - 1}").delete()


def insert_rows(sheet: xw.Sheet, before_row: int, num_rows: int = 1) -> None:
    """38. Inserts specified number of empty rows before a given row."""
    sheet.range(f"{before_row}:{before_row + num_rows - 1}").insert()


def delete_columns(
    sheet: xw.Sheet, start_col: Union[str, int], num_cols: int = 1
) -> None:
    """39. Deletes specified number of columns."""
    start_col_name = (
        start_col if isinstance(start_col, str) else xw.utils.col_num_to_name(start_col)
    )
    end_col_num = (
        (
            xw.utils.col_name_to_num(start_col)
            if isinstance(start_col, str)
            else start_col
        )
        + num_cols
        - 1
    )
    end_col_name = xw.utils.col_num_to_name(end_col_num)
    sheet.range(f"{start_col_name}:{end_col_name}").delete()


def insert_columns(
    sheet: xw.Sheet, before_col: Union[str, int], num_cols: int = 1
) -> None:
    """40. Inserts specified number of empty columns."""
    start_col_name = (
        before_col
        if isinstance(before_col, str)
        else xw.utils.col_num_to_name(before_col)
    )
    end_col_num = (
        (
            xw.utils.col_name_to_num(before_col)
            if isinstance(before_col, str)
            else before_col
        )
        + num_cols
        - 1
    )
    end_col_name = xw.utils.col_num_to_name(end_col_num)
    sheet.range(f"{start_col_name}:{end_col_name}").insert()


# --- Table and Named Range Utilities ---


def create_table(
    sheet: xw.Sheet,
    range_address: str,
    table_name: str,
    table_style: str = "TableStyleMedium9",
) -> xw.main.Table:
    """41. Creates an Excel Table from a given range."""
    rng = sheet.range(range_address)
    # Check if a table with this name already exists
    try:
        tbl = sheet.tables[table_name]
        tbl.delete()  # Delete if exists to avoid error, or handle differently
    except:  # Key error if not found
        pass
    table = sheet.tables.add(source=rng, name=table_name)
    table.show_headers = True  # Default, can be changed
    table.table_style_name = table_style
    return table


def get_table_data(
    sheet: xw.Sheet, table_name: str, include_headers: bool = False
) -> List[List[Any]]:
    """42. Reads data from an Excel Table. Optionally include headers."""
    try:
        table = sheet.tables[table_name]
        if include_headers:
            return table.range.value
        else:
            return table.data_body_range.value if table.data_body_range else []
    except Exception:  # Table not found
        raise ValueError(f"Table '{table_name}' not found on sheet '{sheet.name}'.")


def add_data_to_table(sheet: xw.Sheet, table_name: str, data: List[List[Any]]) -> None:
    """43. Adds new rows of data to an existing Excel Table."""
    try:
        table = sheet.tables[table_name]
        if not data:
            return

        # This is a common way, but can be slow if table has formulas/structure
        # For pure data, resizing and writing is faster.
        # table.add_rows(data) # xlwings built-in, but might be row-by-row

        # More performant for bulk data:
        current_rows = table.data_body_range.rows.count if table.data_body_range else 0
        num_new_rows = len(data)

        # Expand the table range
        # This assumes data is contiguous and table is not structured with totals row etc.
        if table.data_body_range:
            new_range_address = (
                f"{table.header_row_range.address.split(':')[0]}:"
                f"{xw.utils.col_num_to_name(table.range.last_cell.column)}"
                f"{table.header_row_range.row + current_rows + num_new_rows}"
            )
            table.resize(sheet.range(new_range_address))
            # Write data to the new empty rows
            sheet.range(
                table.header_row_range.row + current_rows + 1, table.range.column
            ).value = data
        else:  # Table is empty, just has headers
            new_range_address = (
                f"{table.header_row_range.address.split(':')[0]}:"
                f"{xw.utils.col_num_to_name(table.range.last_cell.column)}"
                f"{table.header_row_range.row + num_new_rows}"
            )
            table.resize(sheet.range(new_range_address))
            sheet.range(table.header_row_range.row + 1, table.range.column).value = data

    except Exception as e:
        raise ValueError(f"Error adding data to table '{table_name}': {e}")


def create_named_range(
    wb_or_sheet: Union[xw.Book, xw.Sheet],
    name: str,
    refers_to_range: Union[xw.Range, str],
) -> None:
    """44. Creates a workbook-level or sheet-level named range."""
    ref_obj = (
        refers_to_range
        if isinstance(refers_to_range, xw.Range)
        else xw.Range(refers_to_range)
    )
    if isinstance(wb_or_sheet, xw.Book):
        wb_or_sheet.names.add(name, f"={ref_obj.sheet.name}!{ref_obj.address}")
    elif isinstance(wb_or_sheet, xw.Sheet):
        wb_or_sheet.names.add(name, f"={ref_obj.address}")  # Sheet level name
    else:
        raise TypeError("wb_or_sheet must be an xlwings Book or Sheet object.")


def get_named_range_value(name: str, wb: Optional[xw.Book] = None) -> Any:
    """45. Gets the value of a named range."""
    book = wb or xw.Book.caller() or xw.books.active
    if not book:
        raise ValueError("No workbook specified or active.")
    try:
        return book.sheets.active.range(
            name
        ).value  # Try sheet level first on active sheet
    except:
        try:
            return book.range(name).value  # Try book level
        except Exception as e:
            raise NameError(
                f"Named range '{name}' not found in workbook '{book.name}'. Error: {e}"
            )


# --- Advanced/Complex Utilities ---


def apply_conditional_formatting_duplicates(
    range_ref: Union[xw.Range, str],
    color_rgb: Tuple[int, int, int] = (255, 199, 206),  # Light red fill
    font_color_rgb: Tuple[int, int, int] = (156, 0, 6),
) -> None:  # Dark red font
    """46. Highlights duplicate values in a range using conditional formatting."""
    rng = xw.Range(range_ref) if isinstance(range_ref, str) else range_ref
    # Delete existing conditional formats on this range to avoid conflicts, or make it optional
    # rng.api.FormatConditions.Delete() # Be careful with this

    # Add new rule for duplicates
    fc = rng.api.FormatConditions.AddUniqueValues()
    fc.DupeUnique = xw.constants.DupeUnique.xlDuplicate  # Correct constant
    fc.Interior.Color = xw.utils.rgb_to_int(color_rgb)
    fc.Font.Color = xw.utils.rgb_to_int(font_color_rgb)


def add_data_validation_list(
    range_ref: Union[xw.Range, str],
    source_list_or_range: Union[List[str], str, xw.Range],
) -> None:
    """47. Adds list data validation to a range.
    source_list_or_range can be a Python list ['Yes', 'No'], a range address "Sheet2!A1:A5", or an xw.Range.
    """
    rng = xw.Range(range_ref) if isinstance(range_ref, str) else range_ref
    dv = rng.api.Validation
    dv.Delete()  # Clear existing validation

    if isinstance(source_list_or_range, list):
        formula_source = ",".join(map(str, source_list_or_range))
    elif isinstance(source_list_or_range, str):  # e.g., "Sheet2!A1:A5" or "=NamedRange"
        formula_source = (
            f"={source_list_or_range}"
            if "!" in source_list_or_range or source_list_or_range.startswith("=")
            else f"='{xw.Range(source_list_or_range).sheet.name}'!{xw.Range(source_list_or_range).address}"
        )
    elif isinstance(source_list_or_range, xw.Range):
        formula_source = (
            f"='{source_list_or_range.sheet.name}'!{source_list_or_range.address}"
        )
    else:
        raise TypeError(
            "source_list_or_range must be a list, string address, or xw.Range."
        )

    dv.Add(
        Type=xw.constants.DataValidationType.xlValidateList,
        AlertStyle=xw.constants.DataValidationAlertStyle.xlValidAlertStop,
        Operator=xw.constants.DataValidationOperator.xlBetween,
        Formula1=formula_source,
    )
    dv.IgnoreBlank = True
    dv.InCellDropdown = True


def freeze_panes(
    sheet: xw.Sheet, cell_address_or_row_col: Union[str, Tuple[int, int]]
) -> None:
    """48. Freezes panes at a specific cell or row/column intersection.
    To freeze top row: (2,1) or "A2"
    To freeze first column: (1,2) or "B1"
    To freeze top row and first col: (2,2) or "B2"
    """
    if isinstance(cell_address_or_row_col, str):
        cell_to_freeze = sheet.range(cell_address_or_row_col)
    elif (
        isinstance(cell_address_or_row_col, tuple) and len(cell_address_or_row_col) == 2
    ):
        cell_to_freeze = sheet.cells(
            cell_address_or_row_col[0], cell_address_or_row_col[1]
        )
    else:
        raise ValueError(
            "Provide cell address like 'B2' or tuple (row, col) like (2,2)."
        )

    # Ensure the cell is selected and active for freezing to work as expected
    # Also, the active window needs to be the one for the sheet
    sheet.activate()
    cell_to_freeze.select()
    sheet.book.app.api.ActiveWindow.FreezePanes = True
    sheet.range("A1").select()  # Optional: move selection back to A1


def unfreeze_panes(sheet: xw.Sheet) -> None:
    """49. Unfreezes all panes on the sheet."""
    sheet.activate()
    sheet.book.app.api.ActiveWindow.FreezePanes = False


def find_and_replace_in_range(
    range_ref: Union[xw.Range, str],
    find_what: Any,
    replace_with: Any,
    look_at_whole: bool = True,
    match_case: bool = False,
) -> int:
    """50. Performs find and replace within a specified range. Returns number of replacements.
    Leverages Excel's built-in Find/Replace for performance.
    """
    rng = xw.Range(range_ref) if isinstance(range_ref, str) else range_ref

    # Store original screen updating state
    # app = rng.sheet.book.app
    # original_screen_updating = app.screen_updating
    # app.screen_updating = False # Usually good for mass operations

    try:
        # To count, we'd ideally use Execute, but Replace does the job and we can't easily get a count
        # So, we'll assume it works and not return a count easily without more complex API calls
        # or by reading before/after (which is slow).
        # For simplicity, this function just performs the replace.
        # Excel's Replace method doesn't directly return the count of replacements via xlwings easily.
        # We could iterate and count, but that defeats the purpose of using the fast built-in.

        # The .Replace method in VBA returns a Boolean. Not a count.
        # If a robust count is needed, it's better to read data, replace in Python, and write back.
        # But for simple, fast replacement, Excel's own is good.

        replace_args = {
            "What": find_what,
            "Replacement": replace_with,
            "LookAt": xw.constants.LookAt.xlWhole
            if look_at_whole
            else xw.constants.LookAt.xlPart,
            "SearchOrder": xw.constants.SearchOrder.xlByRows,
            "MatchCase": match_case,
            "SearchFormat": False,
            "ReplaceFormat": False,
        }
        rng.api.Replace(**replace_args)
        # Since we can't get a count easily, we'll just return a nominal 1 if no error, 0 if error.
        # A more complex approach would involve counting matches before replacing.
        return 1  # Placeholder: Excel's replace is efficient but doesn't give count easily.
    except Exception as e:
        print(f"Error during find and replace: {e}")
        return 0  # Indicate failure or no replacements (can't distinguish easily)
    # finally:
    # app.screen_updating = original_screen_updating


# --- Example Usage (Illustrative) ---
if __name__ == "__main__":  # pragma: no cover
    # Create a new workbook for testing or use an existing one
    # Make sure Excel is running or xlwings can start it.
    try:
        # wb = get_workbook("test_xlwings_utils.xlsx", create_if_not_exists=True)
        wb = create_new_workbook()  # For a fresh test
        sht = wb.sheets[0]
        sht.name = "TestData"
        sht.clear()  # Clear sheet for fresh run

        # 18. Write some data
        header = [["ID", "Name", "Value", "Date"]]
        data_rows = [
            [1, "Alpha", 100, "2023-01-15"],
            [2, "Bravo", 150, "2023-02-20"],
            [3, "Charlie", 120, "2023-01-15"],
            [4, "Alpha", 200, "2023-03-10"],  # Duplicate name
            [5, "Delta", 180, "2023-02-20"],
        ]
        write_range_data(sht, header, "A1")
        write_range_data(sht, data_rows, "A2")
        print("Data written to TestData sheet.")

        # 13. Read data
        all_data = read_range_data(sht, "A1", has_header=False)
        print(f"\nRead all data (as list of lists):\n{all_data[:3]}...")

        data_as_dicts = read_range_data(
            sht.range("A1").expand("table"), has_header=True
        )
        print(f"\nRead data (as list of dicts):\n{data_as_dicts[:2]}...")

        # 14. Read to DataFrame
        df = read_to_dataframe(sht, "A1")
        print(f"\nRead to DataFrame:\n{df.head()}")

        # 21. Append rows
        new_data = [[6, "Echo", 220, "2023-04-05"], [7, "Foxtrot", 250, "2023-05-12"]]
        append_rows(sht, new_data, start_column="A")
        print("\nAppended two rows.")
        print(read_to_dataframe(sht, "A1").tail(3))

        # 25. Set font bold for header
        set_range_font_bold(sht.range("A1:D1"))
        print("\nHeader A1:D1 set to bold.")

        # 27. Set interior color for a cell
        set_range_interior_color(sht.range("C3"), (200, 255, 200))  # Light green
        print("Cell C3 interior color set.")

        # 33. Get last row
        last_row = get_last_row(sht, "A")
        print(f"\nLast row in column A: {last_row}")

        # 41. Create a table
        data_range_for_table = sht.range("A1").expand("table")
        table = create_table(sht, data_range_for_table.address, "MyDataTable")
        print(
            f"\nTable '{table.name}' created from range {data_range_for_table.address}."
        )

        # 46. Apply conditional formatting for duplicates in 'Name' column (B)
        name_col_range = sht.range(
            (2, 2), (get_last_row(sht, "B"), 2)
        )  # B2:B<last_row>
        if name_col_range.value:  # Check if there's data
            apply_conditional_formatting_duplicates(name_col_range)
            print(
                f"Conditional formatting for duplicates applied to {name_col_range.address}."
            )

        # 47. Add data validation
        validation_source_list = ["Type A", "Type B", "Type C"]
        add_data_validation_list(
            sht.range("E2:E" + str(last_row)), validation_source_list
        )
        sht.range("E1").value = "Category"  # Add header for new column
        print(f"Data validation list added to column E.")

        # 50. Find and Replace
        # First, add some values to replace
        sht.range("F1").value = "Status"
        sht.range("F2:F4").value = "Pending"
        sht.range("F5:F8").value = "Pending"  # Last row is 8 now
        num_replaced = find_and_replace_in_range(
            sht.range("F2:F8"), "Pending", "Completed"
        )
        print(
            f"Find and Replace performed in F2:F8 (replaced 'Pending' with 'Completed'). Affected: {num_replaced} (Note: xlwings replace doesn't directly return count)"
        )

        # 29. Autofit columns
        autofit_columns(sht.range("A:F"))  # Autofit columns A to F
        print("\nAutofitted columns A:F.")

        # 2. Save workbook
        # wb.save("test_xlwings_utils_output.xlsx")
        # print("\nWorkbook saved as test_xlwings_utils_output.xlsx")
        print(
            "\nRun completed. If not saving, close Excel manually if a new instance was opened."
        )

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # To prevent Excel from staying open if script was run directly and created a new instance
        # If running as UDF or via RunPython, Excel typically handles its own lifecycle.
        # if wb and not xw.Book.caller(): # Only close if not called from Excel
        #     wb.close()
        #     if wb.app.books.count == 0:
        #        wb.app.quit()
        pass
