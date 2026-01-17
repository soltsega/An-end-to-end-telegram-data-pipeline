with source as (
    select * from {{ source('telegram', 'telegram_messages') }}
),

renamed as (
    select
        id as environment_id,
        message_id,
        channel_name,
        message_date::timestamp as message_date,
        message_text,
        has_media,
        image_path,
        views as view_count,
        forwards as forward_count,
        length(message_text) as message_length,
        created_at
    from source
    where message_id is not null
)

select * from renamed
