import pandas as pd
from utils.mysql import MySQLpy
from sqlalchemy.sql import select
from sqlalchemy import and_, or_
from utils import failure_plot as f_plot
from utils import bot_messages
from telegram import InputMediaPhoto


def list_lines(plot_argws):
    db = MySQLpy('labtdf')
    tb = db.table('vagao')
    
    if plot_argws['type'] == bot_messages.sensors:
        time = plot_argws['param']
        time = time.replace(' ', '_')
        stmt = select([tb.c.linha_gtg]).where(and_(tb.c.elemento_cc != None,
                                                   tb.c.linha_gtg != None,
                                                   or_(tb.c[f'aceleracao_g_{time}'] != None,
                                                       tb.c[f'bodyrock_mm_{time}'] != None,
                                                       tb.c[f'bounce_mm_{time}'] != None,
                                                       tb.c[f'suspentiontravel_mm_{time}'] != None))).distinct()
    elif plot_argws['type'] == bot_messages.contingency:
        if plot_argws['param'] == bot_messages.severity:
            stmt = select([tb.c.linha_gtg]).where(and_(tb.c.elemento_cc != None,
                                                       tb.c.linha_gtg != None,
                                                       tb.c.severidades != None)).distinct()
        elif plot_argws['param'] == bot_messages.abcd_classification:
            stmt = select([tb.c.linha_gtg]).where(and_(tb.c.elemento_cc != None,
                                                       tb.c.linha_gtg != None,
                                                       tb.c.classificacao_abcd != None)).distinct()
    else:
        return None
    
    df = db.read_sql(stmt)

    return df.iloc[:,0].tolist()


def list_elements(plot_argws):
    db = MySQLpy('labtdf')
    tb = db.table('vagao')
    
    if plot_argws['type'] == bot_messages.sensors:
        stmt = select([tb.c.elemento_cc]).where(tb.c.linha_gtg.ilike(plot_argws['line'])).distinct()
    elif plot_argws['type'] == bot_messages.contingency:
        if plot_argws['param'] == bot_messages.severity:
            stmt = select([tb.c.elemento_cc]).where(tb.c.linha_gtg.ilike(plot_argws['line'])).distinct()
        elif plot_argws['param'] == bot_messages.abcd_classification:
            stmt = select([tb.c.elemento_cc]).where(tb.c.linha_gtg.ilike(plot_argws['line'])).distinct()
        else:
            return None
    else:
        return None
    
    df = db.read_sql(stmt)
    
    return df.iloc[:,0].tolist()


def contingency_table(plot_argws):
    db = MySQLpy('labtdf')
    tb = db.table('vagao')

    if plot_argws['param'] == bot_messages.severity:
        stmt = select([tb.c.data, 
                       tb.c.severidades]).where(and_(tb.c.linha_gtg.ilike(plot_argws['line']), 
                                                     tb.c.elemento_cc.ilike(plot_argws['element'])))
    elif plot_argws['param'] == bot_messages.abcd_classification:
        stmt = select([tb.c.data, 
                       tb.c.classificacao_abcd]).where(and_(tb.c.linha_gtg.ilike(plot_argws['line']), 
                                                            tb.c.elemento_cc.ilike(plot_argws['element'])))
    else:
        return None
    
    df = db.read_sql(stmt)
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    df = df.dropna()
    df['data'] = df["data"].apply(lambda t: t.strftime("%Y-%m-%d"))
    
    df = f_plot.contingency_table(df)
    fig, _ = f_plot.render_mpl_table(df, header_columns=0, col_width=2.0);
    media = f_plot.serialize(fig)
    
    return media


def sensors_plot(plot_argws):
    db = MySQLpy('labtdf')
    tb = db.table('vagao')

    time = plot_argws['param']
    time = time.replace(' ', '_')

    stmt = select([tb.c.data,
                  tb.c[f'aceleracao_g_{time}'],
                  tb.c[f'bodyrock_mm_{time}'],
                  tb.c[f'bounce_mm_{time}'],
                  tb.c[f'suspentiontravel_mm_{time}']]).where(and_(tb.c.linha_gtg.ilike(plot_argws['line']), 
                                                                  tb.c.elemento_cc.ilike(plot_argws['element'])))
    df = db.read_sql(stmt)
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    df = df.dropna()
    
    sensors_name = ['aceleração [g]', 'bodyrock [mm]', 
                    'bounce [mm]', 'suspentiontravel [mm]']
    figs = f_plot.sensor_plot(df, plot_argws['line'], plot_argws['element'], sensors_name)
    if len(df.columns) == 2:
        media = [f_plot.serialize(p) for p in figs];
        media = next(iter(media));
    else:
        media = [InputMediaPhoto(media=f_plot.serialize(p)) for p in figs];
    return media


def contingency_plot(plot_argws):
    db = MySQLpy('labtdf')
    tb = db.table('vagao')
    
    if plot_argws['param'] == bot_messages.severity:
        stmt = select([tb.c.data, 
                       tb.c.severidades]).where(and_(tb.c.linha_gtg.ilike(plot_argws['line']), 
                                                     tb.c.elemento_cc.ilike(plot_argws['element'])))
    elif plot_argws['param'] == bot_messages.abcd_classification:
        stmt = select([tb.c.data, 
                       tb.c.classificacao_abcd]).where(and_(tb.c.linha_gtg.ilike(plot_argws['line']), 
                                                            tb.c.elemento_cc.ilike(plot_argws['element'])))
    else:
        return None
    
    df = db.read_sql(stmt)
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    df = df.dropna()
    
    figs = f_plot.contingency_plot(df, plot_argws['line'], plot_argws['element'])
    if df.iloc[:,1].nunique() == 1:
        media = [f_plot.serialize(p) for p in figs];
        media = next(iter(media));
    else:
        media = [InputMediaPhoto(media=f_plot.serialize(p)) for p in figs];
    return media
