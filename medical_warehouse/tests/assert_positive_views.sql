-- data_tests/assert_positive_views.sql
-- This test returns records where view_count is negative.
-- If the query returns 0 rows, the test passes.

select *
from {{ ref('stg_telegram_messages') }}
where view_count < 0
