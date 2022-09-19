with events as (select customer_id::integer,
                       timestamp as timestamp,
                       lag(timestamp) over (partition by customer_id order by timestamp) as previous_timestamp,
                       timestamp - lag(timestamp) over (partition by customer_id order by timestamp) as diff,
                       id,
                       type,
                       user_agent,
                       page,
                       product,
                       position,
                       ip
                from event_buffer),
             
session_borders as (select customer_id,
                           customer_id::varchar || '#' || extract(epoch from timestamp)::varchar as session_id,
                           timestamp as start_current_session,
                           coalesce(lead(timestamp) over(partition by customer_id order by timestamp), '9999-12-31'::date) as start_next_session,
                           timestamp,
                           id,
                           type,
                           user_agent,
                           page,
                           product,
                           position,
                           ip
                     from events
                
                     where diff > interval '20' minute or diff is null),

sessionized_data as (select e.customer_id,
                            md5(session_id::bytea) as session_id,
                            e.id as event_id,
                            e.timestamp as event_dtm,
                            e.type as event_type,
                            e.user_agent,
                            e.page as webpage,
                            e.product,
                            e.position,
                            e.ip
                     from events e
                     left join session_borders sb
                            on e.customer_id = sb.customer_id
                           and e.timestamp >= sb.start_current_session
                           and e.timestamp < coalesce(sb.start_next_session)),
                     
insert_event_table as (insert into event (event_id, session_id, event_type, ip, event_dtm, product, position, webpage)
                      (select event_id, 
                              session_id, 
                              event_type, 
                              ip, 
                              event_dtm, 
                              product, 
                              position, 
                              webpage
                       from sessionized_data))
                              
insert into session_customer (session_id, customer_id, user_agent)
                             (select distinct session_id,
                                              customer_id,
                                              user_agent
                              from sessionized_data);