import os
import sys
import pandas as pd
import psycopg2
if sys.version_info >= (3,0):
    from urllib.parse import urlparse as urlparser
elif sys.version_info >= (2,0): # but less than 3
    import urlparse
    urlparse.uses_netloc.append("postgres")
    urlparser = urlparse.urlparse
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine
import time

load_dotenv(find_dotenv())

def _get_conn(environ_str):
    try:
        url = urlparser(os.environ[environ_str])
        return psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
    except:
        return None
        #raise Exception("Could not connect to {}".format(environ_str))

#TODO change env var to EXCHANGES_DATABASE_URL_AWS_DEV
#TODO add DATABASE_URL_AWS_DEV to point to old db url...
try:
    aws_exchanges_conn = _get_conn("EXCHANGES_DATABASE_URL_AWS_DEV")
except:
    aws_exchanges_conn = None
try:
    aws_conn = _get_conn("DATABASE_URL_AWS_DEV")
except:
    aws_conn = None

try:
    aws_exchanges_engine = create_engine(os.environ["EXCHANGES_DATABASE_URL_AWS_DEV"])
except:
    aws_exchanges_engine = None
try:
    aws_engine = create_engine(os.environ["DATABASE_URL_AWS_DEV"])
except:
    aws_engine = None

def getEngine(environment):
    if(environment == 'aws_dev'):
        return {
            'aws_dev':aws_engine,
        }[environment.lower()]
    elif(environment == 'aws_exchanges'):
        return {
            'aws_exchanges':aws_exchanges_engine,
        }[environment.lower()]
    else:
        raise NameError('Invalid environment name.')

def getConn(environment):
    if(environment == 'aws_dev'):
        return {
            'aws_dev':aws_conn
        }[environment.lower()]
    elif(environment == 'aws_exchanges'):
        return {
            'aws_exchanges': aws_exchanges_conn
        }[environment.lower()]
    else:
        raise NameError('Invalid environment name.')

def commit(environment):
    conn = getConn(environment)
    conn.commit()

def getCursor(environment):
    conn = getConn(environment)
    cur = conn.cursor()
    return cur

def insert(sql,environment):
    cur = getCursor(environment)
    cur.execute(sql)

def query(sql, params=None,environment="dev",dataframe=False):
    if dataframe:
        if params is not None:
            return pd.read_sql(sql, getEngine(environment),params=params)
        else:
            return pd.read_sql(sql, getEngine(environment))
    else:
        cur = getCursor(environment)
        if params is not None:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        return cur.fetchall()

def runCommand(sql, environment):
    cur = getCursor(environment)
    cur.execute(sql)
    return commit(environment)

def getCurrentDateAndTime():
    return time.strftime("%Y%m%dT%H%M%S")

def storeInDb(df,tableName,environment,engine=None,index=False,index_label=None,addMilestoneCol=True, schema=None):
    if engine == None:
        engine = getEngine(environment)
    if addMilestoneCol:
        df[ 'in_z' ] = pd.to_datetime(getCurrentDateAndTime())
    if len(df):
        df.to_sql(tableName,engine,index=index,index_label=index_label,if_exists='append', schema=schema)

def table_exits(schema_name,table_name,environment):
    sql = "select exists( select 1 from information_schema.tables where table_schema = %s and table_name = %s );"
    return query(sql,params=(schema_name,table_name),environment=environment)[0][0]
