with session_start as (select distinct session_id,
                                       min(event_dtm) as session_start_dtm
                       from event
                       group by session_id),
                        
     session_number as (select customer_id,
                               sc.session_id,
                               row_number() over (partition by customer_id order by ss.session_start_dtm) as session_num
                        from session_customer sc
                        join session_start ss
                          on sc.session_id = ss.session_id),
                                          
     first_order_session as (select customer_id,
                                    min(session_num) as first_order_session_num
                             from session_number sn
                             join event e
                               on e.session_id = sn.session_id
                              and event_type = 'placed_order'
                             group by customer_id)                     
                                            
select percentile_cont(0.5) within group(order by first_order_session_num) 
from first_order_session;