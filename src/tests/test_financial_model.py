from math import isclose
from pathlib import Path
from shutil import copyfile

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

    assert len(formula_cells) == 275
    assert all(
        cell.comment
        and "What it computes:" in cell.comment.text
        and "Why:" in cell.comment.text
        for cell in formula_cells
    )
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
    assert _value(solution, "Cash", "B14") == ""
    assert _value(solution, "Cash", "F14") == ""


def test_bank_partner_costs_keep_company_ebitda_and_break_even_pending(
    evaluated_workbook,
):
    workbook, _, _, solution = evaluated_workbook

    assert isclose(_value(solution, "Assumptions", "C16"), 120000, abs_tol=0.01)
    assert workbook["Assumptions"]["C24"].value is None
    assert workbook["Assumptions"]["C25"].value is None
    assert workbook["Assumptions"]["C30"].value is None
    assert workbook["Assumptions"]["C40"].value is None
    assert workbook["Assumptions"]["C41"].value is None
    assert workbook["Bank Partner Economics"]["B5"].value is None

    assert all(_value(solution, "P&L", f"{column}27") == "" for column in "BCDEF")
    assert all(_value(solution, "P&L", f"{column}12") == "" for column in "BCDEF")
    assert all(
        workbook["Unit Economics"][f"J{row}"].value == "Pending"
        for row in range(5, 9)
    )
    assert all(
        workbook["Unit Economics"][f"O{row}"].value == "Pending"
        for row in range(5, 9)
    )
    assert _value(solution, "P&L", "B25") == ""
    assert _value(solution, "Valuation", "B5") == ""
    assert _value(solution, "Valuation", "B13") == ""


def test_funding_benchmarks_use_public_rates_and_label_scenarios(
    evaluated_workbook,
):
    _, _, _, solution = evaluated_workbook

    assert isclose(_value(solution, "Funding Benchmarks", "D5"), 43.33, abs_tol=0.01)
    assert isclose(_value(solution, "Funding Benchmarks", "E5"), 441.67, abs_tol=0.01)
    assert isclose(_value(solution, "Funding Benchmarks", "D6"), 45.6029, abs_tol=0.01)
    assert isclose(_value(solution, "Funding Benchmarks", "E6"), 439.3971, abs_tol=0.01)
    assert isclose(_value(solution, "Funding Benchmarks", "D7"), 70, abs_tol=0.01)
    assert isclose(_value(solution, "Funding Benchmarks", "E7"), 415, abs_tol=0.01)
    assert isclose(_value(solution, "Funding Benchmarks", "D8"), 84, abs_tol=0.01)
    assert isclose(_value(solution, "Funding Benchmarks", "E8"), 401, abs_tol=0.01)


def test_company_pnl_uses_contract_allocation_inputs(tmp_path):
    workbook_path = tmp_path / WORKBOOK_NAME
    copyfile(WORKBOOK_PATH, workbook_path)
    workbook = load_workbook(workbook_path, data_only=False)
    partner = workbook["Bank Partner Economics"]
    for cell, value in {
        "B5": 100,
        "B6": 20,
        "B7": 50,
        "B8": 10,
        "B9": 5000,
        "B10": 1000,
        "B11": 2000,
        "B12": 500,
    }.items():
        partner[cell] = value
    workbook.save(workbook_path)

    workbook = load_workbook(workbook_path, data_only=False)
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
    model = formulas.ExcelModel().loads(str(workbook_path)).finish()
    solution = model.calculate(outputs=output_keys)

    assert isclose(_value(solution, "P&L", "B10"), 10000, abs_tol=0.01)
    assert isclose(_value(solution, "P&L", "B14"), 2000, abs_tol=0.01)
    assert isclose(_value(solution, "P&L", "B15"), 5000, abs_tol=0.01)
    assert isclose(_value(solution, "P&L", "B16"), 1000, abs_tol=0.01)
    assert isclose(_value(solution, "P&L", "B18"), 2000, abs_tol=0.01)
    assert isclose(_value(solution, "P&L", "B19"), 0.2, abs_tol=0.0001)
    assert isclose(_value(solution, "P&L", "B25"), 7000, abs_tol=0.01)
    assert _value(solution, "P&L", "B28") == (
        "PagaFácil scenario; verify against executed contract and quotes"
    )


def test_unit_economics_discloses_unmeasured_churn_and_payback_timing(
    evaluated_workbook,
):
    workbook, _, _, _ = evaluated_workbook
    unit_economics = workbook["Unit Economics"]

    assert "Churn: Not measured" in unit_economics["A16"].value
    assert "Company payback is pending" in unit_economics["A17"].value


def test_company_valuation_is_pending_bank_partner_economics(
    evaluated_workbook,
):
    workbook, _, _, solution = evaluated_workbook

    assert all(
        _value(solution, "Valuation", f"B{row}") == "" for row in (13, 14, 15)
    )
    assert all(
        _value(solution, "Valuation", f"{column}{row}") == ""
        for row in range(21, 27)
        for column in "BCD"
    )
    assert workbook["Valuation"]["B5"].value.startswith(
        "=IF(OR('Bank Partner Economics'!"
    )

    assert _value(solution, "Assumptions", "C42") == 14693
    assert workbook["Assumptions"]["C43"].value == 25
    assert workbook["Assumptions"]["C44"].value == "2500-4000"
    assert isclose(_value(solution, "Unit Economics", "B24"), 36732500, abs_tol=0.01)
    assert isclose(_value(solution, "Unit Economics", "B25"), 10285100, abs_tol=0.01)
    forecast_active_customers = [100, 125, 150, 175, 100]
    for column, active_customers in zip("BCDEF", forecast_active_customers):
        assert isclose(
            _value(solution, "Unit Economics", f"{column}21"),
            active_customers,
            abs_tol=0.01,
        )
        assert isclose(
            _value(solution, "Unit Economics", f"{column}22"),
            active_customers / 14693,
            abs_tol=0.000001,
        )


def test_unresolved_valuation_outputs_stay_blank(tmp_path):
    workbook_path = tmp_path / WORKBOOK_NAME
    copyfile(WORKBOOK_PATH, workbook_path)
    workbook = load_workbook(workbook_path, data_only=False)
    for coordinate in ("C19", "C20", "C21", "C22", "C23"):
        workbook["Assumptions"][coordinate] = None
    workbook.save(workbook_path)

    workbook = load_workbook(workbook_path, data_only=False)
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
    model = formulas.ExcelModel().loads(str(workbook_path)).finish()
    solution = model.calculate(outputs=output_keys)

    assert all(
        _value(solution, "Valuation", f"B{row}") == "" for row in (13, 14, 15)
    )
    assert all(
        _value(solution, "Valuation", f"D{row}") == "" for row in (13, 14, 15)
    )
    assert all(
        _value(solution, "Valuation", f"{column}{row}") == ""
        for row in range(21, 27)
        for column in "BCD"
    )


def test_missing_population_keeps_scenario_outputs_pending(tmp_path):
    workbook_path = tmp_path / WORKBOOK_NAME
    copyfile(WORKBOOK_PATH, workbook_path)
    workbook = load_workbook(workbook_path, data_only=False)
    workbook["Assumptions"]["C42"] = None
    workbook.save(workbook_path)

    workbook = load_workbook(workbook_path, data_only=False)
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
    model = formulas.ExcelModel().loads(str(workbook_path)).finish()
    solution = model.calculate(outputs=output_keys)

    assert _value(solution, "Unit Economics", "B24") == ""
    assert _value(solution, "Unit Economics", "B25") == ""
    assert all(
        _value(solution, "Unit Economics", f"{column}22") == ""
        for column in "BCDEF"
    )


def test_unquoted_partner_costs_keep_entity_outputs_pending(evaluated_workbook):
    workbook, _, _, solution = evaluated_workbook

    assert _value(solution, "P&L", "B25") == ""
    assert _value(solution, "P&L", "C25") == ""
    assert _value(solution, "P&L", "B27") == ""
    assert workbook["Unit Economics"]["J6"].value == "Pending"
    assert workbook["Unit Economics"]["O6"].value == "Pending"
    assert _value(solution, "Cash", "B14") == ""
