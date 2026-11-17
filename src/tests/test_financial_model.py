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

    assert len(formula_cells) == 274
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
    assert isclose(_value(solution, "Cash", "B14"), 248562.5233333, abs_tol=0.01)


def test_approved_cost_scenario_flows_through_forecast_and_break_even(
    evaluated_workbook,
):
    workbook, _, _, solution = evaluated_workbook

    assert isclose(_value(solution, "Assumptions", "C16"), 244229.19, abs_tol=0.01)
    assert isclose(_value(solution, "P&L", "B25"), 124229.19, abs_tol=0.01)
    assert all(
        isclose(_value(solution, "P&L", f"{column}25"), 30000, abs_tol=0.01)
        for column in "CDEF"
    )

    revenue = [_value(solution, "P&L", f"{column}12") for column in "BCDEF"]
    expected_revenue = [70000, 87500, 105000, 122500, 70000]
    assert all(
        isclose(actual, expected, abs_tol=0.01)
        for actual, expected in zip(revenue, expected_revenue)
    )

    ebitda = [_value(solution, "P&L", f"{column}27") for column in "BCDEF"]
    expected_ebitda = [-222729.19, -58125, -47750, -37375, -68500]
    assert all(
        isclose(actual, expected, abs_tol=0.01)
        for actual, expected in zip(ebitda, expected_ebitda)
    )
    assert isclose(_value(solution, "Cash", "F14"), 460312.5233333, abs_tol=0.01)
    assert isclose(_value(solution, "Unit Economics", "J6"), 1136, abs_tol=0.01)
    assert isclose(_value(solution, "Unit Economics", "O6"), 288, abs_tol=0.01)
    for column in "BCDEF":
        formula = workbook["Unit Economics"][f"{column}15"]
        assert formula.data_type == "f"
        assert f"'P&L'!{column}12" in formula.value
        assert f"'P&L'!{column}6" in formula.value
        expected_arpu = _value(solution, "P&L", f"{column}12") / _value(
            solution, "P&L", f"{column}6"
        )
        assert isclose(
            _value(solution, "Unit Economics", f"{column}15"),
            expected_arpu,
            abs_tol=0.01,
        )


def test_unit_economics_discloses_unmeasured_churn_and_payback_timing(
    evaluated_workbook,
):
    workbook, _, _, _ = evaluated_workbook
    unit_economics = workbook["Unit Economics"]

    assert "Churn: Not measured" in unit_economics["A16"].value
    assert "exact month is not modeled" in unit_economics["A17"].value


def test_illustrative_valuation_uses_equity_raise_and_sensitivity(
    evaluated_workbook,
):
    workbook, _, _, solution = evaluated_workbook

    assert isclose(_value(solution, "Cash", "F14"), 460312.5233333, abs_tol=0.01)
    assert isclose(_value(solution, "Cash", "B16"), 276187.514, abs_tol=0.01)
    assert isclose(_value(solution, "Cash", "B17"), 184125.0093333, abs_tol=0.01)
    assert isclose(_value(solution, "Valuation", "B7"), 460312.5233333, abs_tol=0.01)
    assert isclose(_value(solution, "Valuation", "B10"), 184125.0093333, abs_tol=0.01)
    assert workbook["Valuation"]["B10"].value == "=Cash!B17"

    assert isclose(_value(solution, "Valuation", "B13"), 15610.945, abs_tol=0.01)
    assert isclose(_value(solution, "Valuation", "D13"), 0.921842, abs_tol=0.00001)
    assert isclose(_value(solution, "Valuation", "B14"), -174906.902, abs_tol=0.01)
    assert isclose(_value(solution, "Valuation", "B15"), -227203.105, abs_tol=0.01)
    assert _value(solution, "Valuation", "D14") == ""
    assert _value(solution, "Valuation", "D15") == ""

    assert _value(solution, "Assumptions", "C42") == 16500
    assert isclose(_value(solution, "Unit Economics", "B24"), 41250000, abs_tol=0.01)
    assert isclose(_value(solution, "Unit Economics", "B25"), 11550000, abs_tol=0.01)
    forecast_active_customers = [100, 125, 150, 175, 100]
    for column, active_customers in zip("BCDEF", forecast_active_customers):
        assert isclose(
            _value(solution, "Unit Economics", f"{column}21"),
            active_customers,
            abs_tol=0.01,
        )
        assert isclose(
            _value(solution, "Unit Economics", f"{column}22"),
            active_customers / 16500,
            abs_tol=0.000001,
        )

    for row, method_output in (
        (21, "B13"),
        (22, "B13"),
        (23, "B14"),
        (24, "B14"),
        (25, "B15"),
        (26, "B15"),
    ):
        assert isclose(
            _value(solution, "Valuation", f"C{row}"),
            _value(solution, "Valuation", method_output),
            abs_tol=0.01,
        )

    sensitivity_expressions = {
        21: [
            "$B$5*0.5/(1+Assumptions!$C$20)^5-$B$9+$B$8",
            "$B$5*1.0/(1+Assumptions!$C$20)^5-$B$9+$B$8",
            "$B$5*2.0/(1+Assumptions!$C$20)^5-$B$9+$B$8",
        ],
        22: [
            "$B$5*Assumptions!$C$19/(1+0.25)^5-$B$9+$B$8",
            "$B$5*Assumptions!$C$19/(1+0.35)^5-$B$9+$B$8",
            "$B$5*Assumptions!$C$19/(1+0.45)^5-$B$9+$B$8",
        ],
        23: [
            "$B$5*0.5/(1+Assumptions!$C$22)^5-$B$10",
            "$B$5*1.0/(1+Assumptions!$C$22)^5-$B$10",
            "$B$5*2.0/(1+Assumptions!$C$22)^5-$B$10",
        ],
        24: [
            "$B$5*Assumptions!$C$21/(1+0.3)^5-$B$10",
            "$B$5*Assumptions!$C$21/(1+0.5)^5-$B$10",
            "$B$5*Assumptions!$C$21/(1+0.7)^5-$B$10",
        ],
        25: [
            "SUM('P&L'!B27/(1+Assumptions!$C$20)^1,'P&L'!C27/(1+Assumptions!$C$20)^2,'P&L'!D27/(1+Assumptions!$C$20)^3,'P&L'!E27/(1+Assumptions!$C$20)^4,'P&L'!F27/(1+Assumptions!$C$20)^5)+$B$5*0.5/(1+Assumptions!$C$20)^5-$B$9+$B$8",
            "SUM('P&L'!B27/(1+Assumptions!$C$20)^1,'P&L'!C27/(1+Assumptions!$C$20)^2,'P&L'!D27/(1+Assumptions!$C$20)^3,'P&L'!E27/(1+Assumptions!$C$20)^4,'P&L'!F27/(1+Assumptions!$C$20)^5)+$B$5*1.0/(1+Assumptions!$C$20)^5-$B$9+$B$8",
            "SUM('P&L'!B27/(1+Assumptions!$C$20)^1,'P&L'!C27/(1+Assumptions!$C$20)^2,'P&L'!D27/(1+Assumptions!$C$20)^3,'P&L'!E27/(1+Assumptions!$C$20)^4,'P&L'!F27/(1+Assumptions!$C$20)^5)+$B$5*2.0/(1+Assumptions!$C$20)^5-$B$9+$B$8",
        ],
        26: [
            "SUM('P&L'!B27/(1+0.25)^1,'P&L'!C27/(1+0.25)^2,'P&L'!D27/(1+0.25)^3,'P&L'!E27/(1+0.25)^4,'P&L'!F27/(1+0.25)^5)+$B$5*Assumptions!$C$23/(1+0.25)^5-$B$9+$B$8",
            "SUM('P&L'!B27/(1+0.35)^1,'P&L'!C27/(1+0.35)^2,'P&L'!D27/(1+0.35)^3,'P&L'!E27/(1+0.35)^4,'P&L'!F27/(1+0.35)^5)+$B$5*Assumptions!$C$23/(1+0.35)^5-$B$9+$B$8",
            "SUM('P&L'!B27/(1+0.45)^1,'P&L'!C27/(1+0.45)^2,'P&L'!D27/(1+0.45)^3,'P&L'!E27/(1+0.45)^4,'P&L'!F27/(1+0.45)^5)+$B$5*Assumptions!$C$23/(1+0.45)^5-$B$9+$B$8",
        ],
    }
    for row, expressions in sensitivity_expressions.items():
        for column, expression in zip("BCD", expressions):
            assert workbook["Valuation"][f"{column}{row}"].value.endswith(
                expression + ")"
            )

    assert _value(solution, "Valuation", "B21") < _value(
        solution, "Valuation", "C21"
    ) < _value(solution, "Valuation", "D21")
    assert _value(solution, "Valuation", "B22") > _value(
        solution, "Valuation", "C22"
    ) > _value(solution, "Valuation", "D22")
    assert _value(solution, "Valuation", "B23") < _value(
        solution, "Valuation", "C23"
    ) < _value(solution, "Valuation", "D23")
    assert _value(solution, "Valuation", "B24") > _value(
        solution, "Valuation", "C24"
    ) > _value(solution, "Valuation", "D24")
    assert _value(solution, "Valuation", "B25") < _value(
        solution, "Valuation", "C25"
    ) < _value(solution, "Valuation", "D25")
    assert _value(solution, "Valuation", "B26") < _value(
        solution, "Valuation", "C26"
    ) < _value(solution, "Valuation", "D26")


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


def test_missing_campus_population_keeps_market_ceiling_outputs_pending(tmp_path):
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


@pytest.mark.parametrize("missing_input", ["C40", "C41"])
def test_missing_legal_cost_input_keeps_dependent_outputs_pending(
    tmp_path, missing_input
):
    workbook_path = tmp_path / WORKBOOK_NAME
    copyfile(WORKBOOK_PATH, workbook_path)
    workbook = load_workbook(workbook_path, data_only=False)
    workbook["Assumptions"][missing_input] = None
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

    assert solution[_output_key("Assumptions", "C16")].value[0, 0] == ""
    assert solution[_output_key("P&L", "B25")].value[0, 0] == ""
    if missing_input == "C41":
        assert solution[_output_key("P&L", "C25")].value[0, 0] == ""
        assert solution[_output_key("P&L", "C28")].value[0, 0] == "Inputs pending"
        assert solution[_output_key("Unit Economics", "O6")].value[0, 0] == "Pending"
    else:
        assert solution[_output_key("P&L", "C25")].value[0, 0] == 30000
        assert (
            solution[_output_key("P&L", "C28")].value[0, 0]
            == "Complete with unverified legal/compliance assumptions"
        )
        assert isclose(
            solution[_output_key("Unit Economics", "O6")].value[0, 0],
            288,
            abs_tol=0.01,
        )
    assert solution[_output_key("Unit Economics", "J6")].value[0, 0] == "Pending"
