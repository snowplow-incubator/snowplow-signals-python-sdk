{#
Copyright (c) 2023-present Snowplow Analytics Ltd. All rights reserved.
This program is licensed to you under the Snowplow Personal and Academic License Version 1.0,
and you may not use this file except in compliance with the Snowplow Personal and Academic License Version 1.0.
You may obtain a copy of the Snowplow Personal and Academic License Version 1.0 at https://docs.snowplow.io/personal-and-academic-license-1.0/
#}


with prep as (
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
        total_revenue_last_7_days,
        -- Currently snowflake arrays are not sorted, freeze it for expected results
        {% if target.type == 'snowflake' %}
            ARRAY_SORT(op_systems) AS op_systems,
            ARRAY_SORT(op_systems_2) AS op_systems_2
        {% else %}
            op_systems,
            op_systems_2
        {% endif %}
        , min_revenue_last_7_days,
        max_revenue_last_7_days
    from {{ ref('ecommerce_transaction_interactions_features_1_attributes') }}
)

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
        last_os,
        last_device_class,
        last_mkt_source,
        last_mkt_medium,
        total_revenue_last_7_days,
        {{ snowplow_utils.get_array_to_string('op_systems', 'p', ', ') }} as op_systems,
        {{ snowplow_utils.get_array_to_string('op_systems_2', 'p', ', ') }} as op_systems_2,
        min_revenue_last_7_days,
        max_revenue_last_7_days

from prep p
