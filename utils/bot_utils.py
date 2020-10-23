from utils.mysql import MySQLpy
from sqlalchemy.sql import select


def list_elements(line):
    db = MySQLpy('labtdf')
    tb = db.table('vagao')
    stmt = select([tb.c.elemento_cc]).where(tb.c.linha_gtg == line).distinct()
    df = db.read_sql(stmt)
    df = df.iloc[:,0].tolist()
    return df


def list_lines():
    db = MySQLpy('labtdf')
    tb = db.table('vagao')
    stmt = select([tb.c.linha_gtg]).where(tb.c.elemento_cc != None).distinct()
    df = db.read_sql(stmt)
    df = df.iloc[:,0].tolist()
    return df