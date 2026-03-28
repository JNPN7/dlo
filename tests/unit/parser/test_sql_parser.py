from collections import Counter

import pytest

from dlo.core.parser.sql_parser import SqlParser

COMPLEX_QUERY_TABLES = ["main.sales.orders", "sales.customers", "profiles"]
COMPLEX_QUERY = """
WITH ranked_orders AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.order_date,
        o.total_amount,
        ROW_NUMBER() OVER (
            PARTITION BY o.customer_id
            ORDER BY o.order_date DESC
        ) AS rn
    FROM main.sales.orders o               -- catalog.schema.table
    WHERE o.order_date >= date_sub(current_date(), 60)
),

customer_summary AS (
    SELECT
        c.customer_id,
        c.customer_name,
        COUNT(ro.order_id) AS recent_orders,
        SUM(ro.total_amount) AS recent_spend
    FROM sales.customers c                 -- schema.table
    LEFT JOIN ranked_orders ro
        ON c.customer_id = ro.customer_id
    GROUP BY c.customer_id, c.customer_name
),

enriched_data AS (
    SELECT
        cs.customer_id,
        cs.customer_name,
        cs.recent_orders,
        cs.recent_spend,
        p.segment,
        p.region
    FROM customer_summary cs
    LEFT JOIN profiles p                   -- table (unqualified)
        ON cs.customer_id = p.customer_id
)

SELECT
    ed.customer_id,
    ed.customer_name,
    ed.segment,
    ed.region,
    ed.recent_orders,
    ed.recent_spend,

    -- Correlated subquery
    (
        SELECT COUNT(*)
        FROM main.sales.orders o2
        WHERE o2.customer_id = ed.customer_id
          AND o2.total_amount > ed.recent_spend / 2
    ) AS high_value_orders

FROM enriched_data ed

WHERE EXISTS (
    SELECT 1
    FROM profiles p2
    WHERE p2.customer_id = ed.customer_id
      AND p2.segment = 'PREMIUM'
)

ORDER BY ed.recent_spend DESC;
"""


class TestSqlParser:
    @pytest.mark.parametrize("query, query_tables", [(COMPLEX_QUERY, COMPLEX_QUERY_TABLES)])
    def test_sql_parser(self, query, query_tables):
        sql_parser = SqlParser(query)
        tables = sql_parser.extract_table()
        print(tables)
        assert Counter(tables) == Counter(COMPLEX_QUERY_TABLES)
