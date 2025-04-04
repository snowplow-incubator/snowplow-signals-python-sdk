{#
Copyright (c) 2023-present Snowplow Analytics Ltd. All rights reserved.
This program is licensed to you under the Snowplow Personal and Academic License Version 1.0,
and you may not use this file except in compliance with the Snowplow Personal and Academic License Version 1.0.
You may obtain a copy of the Snowplow Personal and Academic License Version 1.0 at https://docs.snowplow.io/personal-and-academic-license-1.0/
#}



select

    domain_userid,
    -- valid_at_tstamp,
    lower_limit,
    upper_limit,
    first_mkt_source,
    first_mkt_medium,
    first_referrer_source,
    first_referrer_medium,
    page_view_events_count_last_7_days,
    page_ping_events_count_last_7_days,
    pricing_pageview_count_last_7_days,
    demo_pageview_count_last_7_days,
    media_video_event_count_last_7_days,
    form_focus_change_event_count_last_7_days,
    last_geo_country,
    last_timezone,
    cast(last_os as {{ dbt.type_string() }}) as last_os,
    cast(last_device_class as {{ dbt.type_string() }}) as last_device_class,
    last_mkt_source,
    last_mkt_medium,
    total_revenue_last_7_days

from {{ ref('ecommerce_transaction_interactions_features_1_attributes') }}
