from typing import Any, Dict, List

from app.engine.expression_evaluator import ExpressionEvaluator


class RuleEngine:
    def __init__(self, rules: List[Dict[str, Any]]):
        # Sort rules strictly by sequence
        self.rules = sorted(rules, key=lambda r: r.get("sequence", 10))

    def compute(self, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        running_context = dict(initial_context)
        computed_lines = []

        for rule in self.rules:
            code = rule["code"]
            calc_type = rule.get("calculation_type", "FIXED")
            category = rule.get("category", "BASIC")

            amount = 0.0
            if calc_type == "FIXED":
                amount = float(rule.get("amount", 0.0))
            elif calc_type == "PERCENTAGE":
                base_var = rule.get("base_variable", "BASIC")
                base_val = running_context.get(base_var, 0.0)
                pct = float(rule.get("percentage", 0.0))
                amount = round(base_val * (pct / 100.0), 2)
            elif calc_type == "FORMULA":
                formula = rule.get("formula", "0")
                amount = ExpressionEvaluator.evaluate(formula, running_context)

            running_context[code] = round(amount, 2)
            computed_lines.append({
                "rule_code": code,
                "rule_name": rule.get("name", code),
                "category": category,
                "sequence": rule.get("sequence", 10),
                "amount": round(amount, 2)
            })

        return {
            "context": running_context,
            "lines": computed_lines
        }
