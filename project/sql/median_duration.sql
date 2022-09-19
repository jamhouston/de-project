with session_borders as (select session_id,
                                min(event_dtm) as session_start_dtm,
                                max(event_dtm) as session_end_dtm
                        from event
                        group by session_id),
                        
     session_number as (select customer_id,
                               sc.session_id,
                               row_number() over (partition by customer_id order by sb.session_start_dtm) as session_num,
                               session_end_dtm - session_start_dtm as session_duration
                               
                        from session_customer sc
                        join session_borders sb
                          on sc.session_id = sb.session_id),
                                          
     first_order_session as (select customer_id,
                                    min(session_num) as first_order_session_num
                             from session_number sn
                             join event e
                               on e.session_id = sn.session_id
                              and event_type = 'placed_order'
                             group by customer_id),
                             
     sessions_before_order as (select sn.session_id,
                                      sn.session_duration
                               from session_number sn
                               join first_order_session fos
                                 on sn.customer_id = fos.customer_id
                                and sn.session_num <= fos.first_order_session_num),
                   
                                            
     percentile as (select percentile_cont(0.5) within group(order by session_duration) as median_duration
                    from sessions_before_order)

select round((extract(epoch from median_duration) / 60)::integer) 
from percentile;