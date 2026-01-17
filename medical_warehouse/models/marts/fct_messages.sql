with stg as (
    select * from {{ ref('stg_telegram_messages') }}
),

dim_channels as (
    select * from {{ ref('dim_channels') }}
)

select
    stg.message_id,
    c.channel_key,
    stg.message_date,
    stg.message_text,
    stg.message_length,
    stg.view_count,
    stg.forward_count,
    stg.has_media,
    stg.image_path
from stg
left join dim_channels c on stg.channel_name = c.channel_name
