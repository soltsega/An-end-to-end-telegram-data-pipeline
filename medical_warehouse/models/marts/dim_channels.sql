with stg as (
    select * from {{ ref('stg_telegram_messages') }}
),

channel_stats as (
    select
        channel_name,
        count(*) as total_posts,
        min(created_at) as first_extracted_at,
        max(created_at) as last_extracted_at,
        avg(view_count) as avg_views
    from stg
    group by 1
)

select 
    {{ dbt_utils.generate_surrogate_key(['channel_name']) }} as channel_key,
    *
from channel_stats
