from math import isclose
from pathlib import Path

import formulas
import pytest
from openpyxl import load_workbook


WORKBOOK_PATH = Path(__file__).parents[2] / "PagaFacil_Financial_Model.xlsx"
WORKBOOK_NAME = WORKBOOK_PATH.name


def _output_key(sheet: str, cell: str) -> str:
    return f"'[{WORKBOOK_NAME}]{sheet.upper()}'!{cell}"


@pytest.fixture(scope="module")
def evaluated_workbook():
    workbook = load_workbook(WORKBOOK_PATH, data_only=False)
    formula_cells = [
        cell
        for sheet in workbook
        for row in sheet.iter_rows()
        for cell in row
        if cell.data_type == "f"
    ]
    output_keys = [
        _output_key(cell.parent.title, cell.coordinate) for cell in formula_cells
    ]
    model = formulas.ExcelModel().loads(str(WORKBOOK_PATH)).finish()
    solution = model.calculate(outputs=output_keys)
    return workbook, formula_cells, output_keys, solution


def _value(solution, sheet: str, cell: str) -> object:
    return solution[_output_key(sheet, cell)].value[0, 0]


def test_all_workbook_formulas_evaluate_without_errors(evaluated_workbook):
    _, formula_cells, output_keys, solution = evaluated_workbook

    assert len(formula_cells) == 234
    assert all(cell.comment for cell in formula_cells)
    assert all(key in solution for key in output_keys)

    errors = [
        f"{cell.parent.title}!{cell.coordinate}: {type(solution[key].value[0, 0]).__name__}"
        for cell, key in zip(formula_cells, output_keys)
        if isinstance(solution[key].value[0, 0], formulas.XlError)
    ]
    assert not errors, "\n".join(errors)


def test_cash_collections_follow_january_and_august_origination_scenario(
    evaluated_workbook,
):
    _, _, _, solution = evaluated_workbook

    expected = [
        284166.6666667,
        381041.6666667,
        458541.6666667,
        536041.6666667,
        329375.0,
    ]
    actual = [_value(solution, "Cash", f"{column}8") for column in "BCDEF"]

    assert all(
        isclose(value, target, abs_tol=0.01)
        for value, target in zip(actual, expected)
    )
    assert isclose(_value(solution, "Cash", "B14"), 158562.5233333, abs_tol=0.01)


def test_unresolved_financing_and_valuation_outputs_stay_blank(evaluated_workbook):
    _, _, _, solution = evaluated_workbook

    assert _value(solution, "Cash", "F14") == ""
    assert _value(solution, "Cash", "B16") == ""
    assert _value(solution, "Cash", "B17") == ""
    assert all(
        _value(solution, "Valuation", f"B{row}") == "" for row in (13, 14, 15)
    )
    assert all(
        _value(solution, "Valuation", f"D{row}") == "" for row in (13, 14, 15)
    )
