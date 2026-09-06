from simpleeval import SimpleEval


class ExpressionEvaluator:
    @staticmethod
    def evaluate(formula: str, context: dict) -> float:
        s = SimpleEval()
        s.names = context
        try:
            val = s.eval(formula)
            return float(val)
        except Exception as e:
            raise ValueError(f"Failed to evaluate formula '{formula}' with context {context}: {str(e)}") from e
