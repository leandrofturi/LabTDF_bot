import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

plt.style.use('ggplot')


def serialize(plt):
    buf = BytesIO()
    plt.savefig(buf, format='JPEG')
    buf.seek(0)
    return buf


def scatter_plot(data, x, y, title=None, xlabel=None, ylabel=None):
    plt.figure()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    p = sns.scatterplot(data=data, x=x, y=y).get_figure()
    return p


def contingency_table(df):
    """
    contingency_table Construção das tabelas de contingência.

    Args:
        df (DataFrame): DataFrame contendo os dados para construção das tabelas. 
            Veja que a coluna 'data' (data da informação) é obrigatória e 'severidade' ou 'classificação' são esperadas

    Returns:
        DataFrame: Tabela de contingência
    """

    c = [x for x in df.columns if x != 'data']
    dg = pd.get_dummies(df, columns=c, prefix=[""], prefix_sep=[""])
    dg = pd.pivot_table(dg, index=['data'], aggfunc=np.sum)
    dg.reset_index(level=0, inplace=True)
    return dg


def render_mpl_table(data, col_width=3.0, row_height=0.625, font_size=10,
                     header_color='#c0c0c0', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    """
    render_mpl_table Salva um Pandas DataFrame/Series como uma figura
    https://stackoverflow.com/questions/19726663/how-to-save-the-pandas-dataframe-series-data-as-a-figure

    Args:
        data (DataFrame/Series): Pandas DataFrame/Series
        col_width (float, optional): Column width. Defaults to 3.0.
        row_height (float, optional): Row height. Defaults to 0.625.
        font_size (int, optional): Font size. Defaults to 10.
        header_color (str, optional): Header color background. Defaults to '#c0c0c0'.
        row_colors (list, optional): Row colors. Defaults to ['#f1f1f2', 'w'].
        edge_color (str, optional): The color of edges to be drawn. Defaults to 'w'.
        bbox (list, optional): A bounding box to draw the table into. Defaults to [0, 0, 1, 1].
        header_columns (int, optional): Row of header column. Defaults to 0.
        ax (Axes, optional): Axes element of matplotlib. Defaults to None.

    Returns:
        Figure: Figure
        axes.Axes: Axes
    """

    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        _, ax = plt.subplots(figsize=size);
        ax.axis('off');
    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)
    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in mpl_table._cells.items():
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='k')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    return ax.get_figure(), ax


def contingency_plot(df, line, element, clsf_name):
    """
    contingency_plot scatter plot das tabelas de contingência.

    Args:
        df (DataFrame): Tabela contendo os dados a serem visualizados.
            Veja que a coluna 'data' (data da informação) é obrigatória e 'severidade' ou 'classificação' são esperadas
        line (text object): Localização do trecho da via, em termos de Linha (GTG).
        element (text object): Elemento da via.
        clsf_name (text object): Nome do objeto em contagem. Espera-se severidade ou classificação

    Yields:
        Figure: plot de uma severidade/classificação específica
    """        

    dg = contingency_table(df)
    for i in [x for x in dg.columns if x != 'data']:
        p = scatter_plot(dg, 'data', i, 
                         title=f'Localização: {line} - {element}', 
                         xlabel='data', ylabel=f'contagem {clsf_name}\n{i}');
        yield p


def sensor_plot(df, line, element, sensors_name):
    """
    sensor_plot scatter plot dos dados dos sensores (Aceleração, Bounce, Rock e Suspention Travel).

    Args:
        df (DataFrame): Tabela contendo os dados a serem visualizados.
            Veja que a coluna 'data' (data da informação) é obrigatória e os dados dos sensores são esperados.
        line (text object): Localização do trecho da via, em termos de Linha (GTG).
        element (text object): Elemento da via.
        sensors_name (list): Nome dos sensores a serem visualizados.
            Note que a ordem deve estar de acordo com a ordem das colunas de df.

    Yields:
        Figure: plot de um sensor específico
    """
        
    s = iter(sensors_name)
    for i in [x for x in df.columns if x != 'data']:
        p = scatter_plot(df, 'data', i, 
                         title=f'Localização: {line} - {element}', 
                         xlabel='data', ylabel=f'{next(s)}');
        yield p
