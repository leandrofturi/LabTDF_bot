import pandas as pd
import numpy as np
from utils import failure_plot as f_plot, bot_messages
from utils.mysql import MySQLpy
from sqlalchemy.sql import select
from sqlalchemy import and_, or_
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

# Ajustes de acordo com o nome das colunas no database
def fix_param(plot_argws):    
    if plot_argws['type'] == bot_messages.sensors:
        if plot_argws['param'] == bot_messages.three_seconds:
            plot_argws['param'] = '3_segundos'
        elif plot_argws['param'] == bot_messages.twenty_seconds:
            plot_argws['param'] = '20_segundos'

    elif plot_argws['type'] == bot_messages.contingency:
        if plot_argws['param'] == bot_messages.severity:
            plot_argws['param'] = 'severidades'
        elif plot_argws['param'] == bot_messages.abcd_classification:
            plot_argws['param'] = 'classificacao_abcd'

    elif plot_argws['type'] == bot_messages.speed_restriction:
        if plot_argws['param'] == bot_messages.acceleration:
            plot_argws['param'] = "aceleracao_g"
        elif plot_argws['param'] == bot_messages.suspentiontravel:
            plot_argws['param'] = "suspentiontravel_mm"
        elif plot_argws['param'] == bot_messages.bodyrock:
            plot_argws['param'] = "bodyrock_mm"
        elif plot_argws['param'] == bot_messages.bounce:
            plot_argws['param'] = "bounce_mm"


def contingency_table(plot_argws):
    db = MySQLpy('EFVM')
    tb = db.table('VBR_VTU')

    fix_param(plot_argws)
    if plot_argws['param'] == None:
        return None
    
    if plot_argws['by'] == 'E':
        stmt = select([tb.c.data, tb.c[plot_argws['param']]]) \
                .where(and_(tb.c.linha_gtg.ilike(plot_argws['line']), 
                            tb.c.elemento_cc.ilike(plot_argws['element'])))
    elif plot_argws['by'] == 'K':
        stmt = select([tb.c.data, tb.c[plot_argws['param']]]) \
            .where(and_(tb.c.km_ini_cc + tb.c.metro_ini_cc/1000 <= plot_argws['km'],
                   tb.c.km_fim_cc + tb.c.metro_fim_cc/1000 >= plot_argws['km']))
    else:
        return None

    df = db.read_sql(stmt)
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    df = df.dropna()

    df = f_plot.contingency_table(df, 'data', 'Data', plot_argws['param'])
    df['Data'] = df['Data'].apply(lambda x: x.strftime('%Y-%m-%d'))
    fig, _ = f_plot.render_mpl_table(df, header_columns=0, col_width=2.0)
    media = f_plot.serialize(fig)

    return media


def sensors_plot(plot_argws):
    db = MySQLpy('EFVM')
    tb = db.table('VBR_VTU')

    fix_param(plot_argws)
    if plot_argws['param'] == None:
        return None

    time = plot_argws['param']
    sensors = [f'aceleracao_g_{time}', f'bodyrock_mm_{time}', 
               f'bounce_mm_{time}', f'suspentiontravel_mm_{time}']

    if plot_argws['by'] == 'E':
        stmt = select([tb.c[k] for k in ['data']+sensors]) \
            .where(and_(tb.c.linha_gtg.ilike(plot_argws['line']), 
                        tb.c.elemento_cc.ilike(plot_argws['element'])))
    elif plot_argws['by'] == 'K':
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

    fix_param(plot_argws)
    if plot_argws['param'] == None:
        return None
    
    if plot_argws['by'] == 'E':
        stmt = select([tb.c.data, tb.c[plot_argws['param']]]) \
                .where(and_(tb.c.linha_gtg.ilike(plot_argws['line']), 
                            tb.c.elemento_cc.ilike(plot_argws['element'])))
    elif plot_argws['by'] == 'K':
        stmt = select([tb.c.data, tb.c[plot_argws['param']]]) \
            .where(and_(tb.c.km_ini_cc + tb.c.metro_ini_cc/1000 <= plot_argws['km'],
                   tb.c.km_fim_cc + tb.c.metro_fim_cc/1000 >= plot_argws['km']))
    else:
        return None

    df = db.read_sql(stmt)
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    df = df.dropna()

    figs = f_plot.contingency_plot(df, "data", plot_argws['param'], "Data")
    if df[plot_argws['param']].nunique() == 1:
        media = [f_plot.serialize(p) for p in figs]
        media = next(iter(media))
    else:
        media = [InputMediaPhoto(media=f_plot.serialize(p)) for p in figs]
    return media


def rest_velocidade_plot(plot_argws):
    db = MySQLpy('EFVM')
    tb = db.table('VBR_VTU')

    fix_param(plot_argws)
    if plot_argws['param'] == None:
        return None

    if plot_argws['by'] == 'E':
        stmt = [select([tb.c.velocidadekmh, tb.c[plot_argws['param']]]) \
                .where(and_(tb.c.linha_gtg.ilike(plot_argws['line']), 
                            tb.c.elemento_cc.ilike(plot_argws['element'])))]
    elif plot_argws['by'] == 'K':
        if plot_argws['km'] is None:
            return None
        elif isinstance(plot_argws['km'], list):
            stmt = [select([tb.c.velocidadekmh, tb.c[plot_argws['param']]]) \
                .where(and_(tb.c.km_ini_cc + tb.c.metro_ini_cc/1000 <= km,
                       tb.c.km_fim_cc + tb.c.metro_fim_cc/1000 >= km)) for km in plot_argws['km']]
        else:
            stmt = [select([tb.c.velocidadekmh, tb.c[plot_argws['param']]]) \
                .where(and_(tb.c.km_ini_cc + tb.c.metro_ini_cc/1000 <= plot_argws['km'],
                       tb.c.km_fim_cc + tb.c.metro_fim_cc/1000 >= plot_argws['km']))]
    else:
        return None

    dfs = [db.read_sql(s) for s in stmt]

    lim_sev = pd.DataFrame(np.array([[46, 16, 23, 11], [22, 9, 15, 6], [11, 6, 8, 3]]),
                       columns=['aceleracao_g','suspentiontravel_mm','bodyrock_mm','bounce_mm'])
    if plot_argws['param'] == "aceleracao_g":
        ylabel = "Aceleração (g)"
    elif plot_argws['param'] == "suspentiontravel_mm":
        ylabel = "Suspention Travel (mm)"
    elif plot_argws['param'] == "bodyrock_mm":
        ylabel = "Body Rock (mm)"
    elif plot_argws['param'] == "bounce_mm":
        ylabel = "Bounce (mm)"
    else:
        ylabel = ""

    if len(dfs) == 1:
        p = f_plot.rest_velocidade_plot(dfs[0], 'velocidadekmh', plot_argws['param'], 
                                        lim_sev[plot_argws['param']], 
                                        ["S1","S2","S3"], "Velocidade (km/h)", ylabel)
    else:
        kwargs = dict(zip(["Km " + str(k) for k in plot_argws['km']], dfs))
        p = f_plot.comp_velocidade_plot('velocidadekmh', plot_argws['param'], 
                                        lim_sev[plot_argws['param']], 
                                        ["S1","S2","S3"], "Velocidade (km/h)", ylabel, 
                                        **kwargs)
    
    media = f_plot.serialize(p)
    return media
    