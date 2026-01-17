with detections as (
    select * from {{ source('telegram', 'yolo_detections') }}
),

messages as (
    select * from {{ ref('stg_telegram_messages') }}
),

channels as (
    select * from {{ ref('dim_channels') }}
),

dates as (
    select * from {{ ref('dim_dates') }}
),

final as (
    select
        d.message_id,
        c.channel_key,
        dt.date_key,
        d.detected_objects,
        d.confidence_scores,
        d.classification as image_category,
        d.image_path
    from detections d
    -- Join to messages to get the date for the date key
    join messages m on d.message_id = m.message_id and d.channel_name = m.channel_name
    -- Join to dimensions
    left join channels c on d.channel_name = c.channel_name
    left join dates dt on m.message_date::date = dt.full_date
)

select * from final
