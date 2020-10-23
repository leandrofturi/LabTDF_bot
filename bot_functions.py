from utils.mysql import MySQLpy
from sqlalchemy.sql import select, column
from sqlalchemy.orm import load_only
from sqlalchemy import and_
from utils import failure_plot as f_plot
from telegram import InputMediaPhoto


def contingency_plot(local, element, sev=True):
    db = MySQLpy('labtdf')
    tb = db.table('vagao')
    
    if sev:
        clsf_name = 'severidade'
        stmt = select([tb.c.data, tb.c.severidades]).where(
            and_(tb.c.linha_gtg == local, tb.c.elemento_cc == element))
    else:
        clsf_name = 'classificação'
        stmt = select([tb.c.data, tb.c.classificacao_abcd]).where(
            and_(tb.c.linha_gtg == local, tb.c.elemento_cc == element))
    
    df = db.read_sql(stmt)
    
    if df.iloc[:,1].nunique() == 1:
        media = [f_plot.serialize(p) for p in f_plot.contingency_plot(df, local, element, clsf_name)]
        media = next(iter(media))
    else:
        media = [InputMediaPhoto(media=f_plot.serialize(p)) for p in f_plot.contingency_plot(df, local, element, clsf_name)]
    return media


def sensors_plot(local, element, time):
    db = MySQLpy('labtdf')
    tb = db.table('vagao')

    time = time.replace(' ', '_')
    sensors_name = [f'aceleracao_g_{time}', f'bodyrock_mm_{time}', 
                    f'bounce_mm_{time}', f'suspentiontravel _mm_{time}']
    colnames = [p.name for p in tb.c]
    sensors_name = [p for p in sensors_name if p in colnames]
    if len(sensors_name) == 0:
        return None

    sensors_name.append('data')
    stmt = [tb.c[k] for k in sensors_name]
    stmt = select(stmt)
    df = db.read_sql(stmt)
    
    if len(df.columns) == 2:
        media = [f_plot.serialize(p) for p in f_plot.sensor_plot(df, local, element, sensors_name)]
        media = next(iter(media))
    else:
        media = [InputMediaPhoto(media=f_plot.serialize(p)) for p in f_plot.sensor_plot(df, local, element, sensors_name)]
    return media
