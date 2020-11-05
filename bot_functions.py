import pandas as pd
from utils.mysql import MySQLpy
from sqlalchemy.sql import select
from sqlalchemy import and_, or_
from utils import failure_plot as f_plot
from utils import bot_messages
from telegram import InputMediaPhoto


# --- lists ---

def list_elements():
    db = MySQLpy('EFVM')
    tb = db.table('VBR_VTU')

    stmt = select([tb.c.elemento_cc]) \
        .where(tb.c.elemento_cc != None) \
            .order_by(tb.c.elemento_cc) \
                .distinct()
    df = db.read_sql(stmt)

    return df.iloc[:,0].tolist()

def list_lines(element):
    db = MySQLpy('EFVM')
    tb = db.table('VBR_VTU')

    stmt = select([tb.c.linha_gtg]) \
        .where(and_(tb.c.linha_gtg != None, 
                    tb.c.elemento_cc.ilike(element))) \
            .order_by(tb.c.linha_gtg) \
                .distinct()
    df = db.read_sql(stmt)

    return df.iloc[:,0].tolist()


def range_km():
    db = MySQLpy('EFVM')
    tb = db.table('VBR_VTU')
    
    stmt = select([tb.c.km_ini_cc, tb.c.metro_ini_cc,
                   tb.c.km_fim_cc, tb.c.metro_fim_cc]) \
                       .order_by(tb.c.km_ini_cc) \
                           .distinct()
    df = db.read_sql(stmt)

    lo = (df['km_ini_cc'] + df['metro_ini_cc']/1000).min()
    hi = (df['km_fim_cc'] + df['metro_fim_cc']/1000).max()
    
    return lo, hi


# --- plots ---

def contingency_table(plot_argws):
    db = MySQLpy('EFVM')
    tb = db.table('VBR_VTU')

    if plot_argws['param'] == bot_messages.severity:
        clfs = 'severidades'
    elif plot_argws['param'] == bot_messages.abcd_classification:
        clfs = 'classificacao_abcd'
    else:
        return None
    
    if plot_argws['km'] is None:
        stmt = select([tb.c.data, tb.c[clfs]]) \
                .where(and_(tb.c.linha_gtg.ilike(plot_argws['line']), 
                            tb.c.elemento_cc.ilike(plot_argws['element'])))
    elif plot_argws['element'] is None:
        stmt = select([tb.c.data, tb.c[clfs]]) \
            .where(and_(tb.c.km_ini_cc + tb.c.metro_ini_cc/1000 <= plot_argws['km'],
                   tb.c.km_fim_cc + tb.c.metro_fim_cc/1000 >= plot_argws['km']))
    else:
        return None

    df = db.read_sql(stmt)
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    df = df.dropna()

    df = f_plot.contingency_table(df, 'data', 'Data', clfs)
    df['Data'] = df['Data'].apply(lambda x: x.strftime('%Y-%m-%d'))
    fig, _ = f_plot.render_mpl_table(df, header_columns=0, col_width=2.0)
    media = f_plot.serialize(fig)

    return media


def sensors_plot(plot_argws):
    db = MySQLpy('EFVM')
    tb = db.table('VBR_VTU')

    time = plot_argws['param']
    time = time.replace(' ', '_').lower()
    sensors = [f'aceleracao_g_{time}', f'bodyrock_mm_{time}', 
               f'bounce_mm_{time}', f'suspentiontravel_mm_{time}']

    if plot_argws['km'] is None:
        stmt = select([tb.c[k] for k in ['data']+sensors]) \
            .where(and_(tb.c.linha_gtg.ilike(plot_argws['line']), 
                        tb.c.elemento_cc.ilike(plot_argws['element'])))
    elif plot_argws['element'] is None:
        stmt = select([tb.c[k] for k in ['data']+sensors]) \
            .where(and_(tb.c.km_ini_cc + tb.c.metro_ini_cc/1000 <= plot_argws['km'],
                   tb.c.km_fim_cc + tb.c.metro_fim_cc/1000 >= plot_argws['km']))
    else:
        return None

    df = db.read_sql(stmt)
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    df = df.dropna()

    sensors_name = ['Aceleração (g)', 'Bodyrock (mm)', 
                    'Bounce (mm)', 'Suspention Travel (mm)']
    figs = f_plot.sensor_plot(df, 'data', sensors, 'Data', sensors_name)
    if len(df.columns) == 2:
        media = [f_plot.serialize(p) for p in figs]
        media = next(iter(media))
    else:
        media = [InputMediaPhoto(media=f_plot.serialize(p)) for p in figs]
    return media


def contingency_plot(plot_argws):
    db = MySQLpy('EFVM')
    tb = db.table('VBR_VTU')

    if plot_argws['param'] == bot_messages.severity:
        clfs = 'severidades'
    elif plot_argws['param'] == bot_messages.abcd_classification:
        clfs = 'classificacao_abcd'
    else:
        return None
    
    if plot_argws['km'] is None:
        stmt = select([tb.c.data, tb.c[clfs]]) \
                .where(and_(tb.c.linha_gtg.ilike(plot_argws['line']), 
                            tb.c.elemento_cc.ilike(plot_argws['element'])))
    elif plot_argws['element'] is None:
        stmt = select([tb.c.data, tb.c[clfs]]) \
            .where(and_(tb.c.km_ini_cc + tb.c.metro_ini_cc/1000 <= plot_argws['km'],
                   tb.c.km_fim_cc + tb.c.metro_fim_cc/1000 >= plot_argws['km']))
    else:
        return None

    df = db.read_sql(stmt)
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    df = df.dropna()

    figs = f_plot.contingency_plot(df, "data", clfs, "Data")
    if df[clfs].nunique() == 1:
        media = [f_plot.serialize(p) for p in figs]
        media = next(iter(media));
    else:
        media = [InputMediaPhoto(media=f_plot.serialize(p)) for p in figs]
    return media
