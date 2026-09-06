from app.engine.rule_engine import RuleEngine


def test_salary_rule_engine_basic_computation():
    rules = [
        {"code": "BASIC", "name": "Basic Salary", "category": "BASIC", "sequence": 1, "calculation_type": "FIXED", "amount": 5000.0},
        {"code": "HRA", "name": "House Rent Allowance", "category": "ALLOWANCE", "sequence": 2, "calculation_type": "PERCENTAGE", "percentage": 20.0, "base_variable": "BASIC"},
        {"code": "GROSS", "name": "Gross Salary", "category": "GROSS", "sequence": 3, "calculation_type": "FORMULA", "formula": "BASIC + HRA"},
        {"code": "PF", "name": "Provident Fund", "category": "DEDUCTION", "sequence": 4, "calculation_type": "PERCENTAGE", "percentage": 12.0, "base_variable": "BASIC"},
        {"code": "NET", "name": "Net Salary", "category": "NET", "sequence": 5, "calculation_type": "FORMULA", "formula": "GROSS - PF"},
    ]

    engine = RuleEngine(rules)
    result = engine.compute(initial_context={})

    ctx = result["context"]
    assert ctx["BASIC"] == 5000.0
    assert ctx["HRA"] == 1000.0
    assert ctx["GROSS"] == 6000.0
    assert ctx["PF"] == 600.0
    assert ctx["NET"] == 5400.0
