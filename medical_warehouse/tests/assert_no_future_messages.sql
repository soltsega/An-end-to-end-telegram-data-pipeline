-- data_tests/assert_no_future_messages.sql
-- This test returns records where the message_date is in the future.
-- If the query returns 0 rows, the test passes.

select *
from {{ ref('stg_telegram_messages') }}
where message_date > current_timestamp
