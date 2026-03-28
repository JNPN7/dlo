from sqlglot import exp, parse_one


class SqlParser:
    def __init__(self, query: str):
        self.query = query
        self._expr = None

    @property
    def expr(self):
        if self._expr is None:
            self._expr = parse_one(self.query)

        return self._expr

    def extract_table(self):
        # Get CTE names so we can exclude them
        ctes = self.expr.find_all(exp.CTE)
        cte_names = {cte.alias_or_name for cte in ctes}

        tables = self.expr.find_all(exp.Table)
        table_names = {
            ".".join(part for part in [t.catalog, t.db, t.name] if part)
            for t in tables if t.name not in cte_names
        }

        return table_names
