with dates as (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2024-01-01' as date)",
        end_date="cast('2026-01-01' as date)"
    )
    }}
)
select
    date_day,
    extract(year from date_day) as year,
    extract(month from date_day) as month,
    to_char(date_day, 'Month') as month_name,
    extract(day from date_day) as day_of_month,
    to_char(date_day, 'Day') as day_name,
    extract(dow from date_day) as day_of_week,
    extract(quarter from date_day) as quarter
from dates
