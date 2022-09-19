DROP TABLE IF EXISTS event_buffer;

CREATE TABLE event_buffer(
    id BIGINT NOT NULL,
    type VARCHAR,
    user_agent VARCHAR,
    ip VARCHAR,
    customer_id VARCHAR NOT NULL,
    timestamp TIMESTAMP,
    product INT,
    position INT,
    page VARCHAR
);


DROP TABLE IF EXISTS event;

CREATE TABLE event(
    event_id BIGINT NOT NULL,
    session_id VARCHAR,
    event_type VARCHAR,
    ip VARCHAR,
    event_dtm TIMESTAMP,
    product INT,
    position INT,
    webpage VARCHAR
);


DROP TABLE IF EXISTS session_customer;

CREATE TABLE session_customer(
    
    session_id VARCHAR,
    customer_id INT,
    user_agent VARCHAR
);