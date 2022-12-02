import sqlite3

import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
    

'''
CREATE DATABASE ebay;
\c ebay; 
DROP TABLE IF EXISTS transactions;
CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY NOT NULL, 
    user_id VARCHAR(40) NOT NULL, 
    cart_id VARCHAR(40) NOT NULL, 
    total  NUMERIC(9, 2) NOT NULL, 
    method VARCHAR(40) NOT NULL, 
    transaction_time TIMESTAMP DEFAULT NOW()
);

'''

# 2022-11-26 17:36:06.564 CST [89259] LOG:  listening on IPv6 address "::1", port 5432
# 2022-11-26 17:36:06.564 CST [89259] LOG:  listening on IPv4 address "127.0.0.1", port 5432
# 2022-11-26 17:36:06.565 CST [89259] LOG:  listening on Unix socket "/tmp/.s.PGSQL.5432"
# 2022-11-26 17:36:06.573 CST [89260] LOG:  database system was shut down at 2022-09-11 23:50:07 CDT
# 2022-11-26 17:36:06.578 CST [89259] LOG:  database system is ready to accept connections