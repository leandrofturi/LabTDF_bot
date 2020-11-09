import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

# Style
style='ggplot'

# Colors
laranja='#ca571a'
cinza='#6f6f6e'
terra='#57473f'


def serialize(plt):
    buf = BytesIO()
    plt.savefig(buf, format='JPEG', bbox_inches="tight")
    buf.seek(0)
    return buf


def scatter_plot(data, x, y, xlabel=None, ylabel=None):
    plt.figure()
    plt.style.use(style)
    plt.xlabel(xlabel)
    plt.xticks(rotation=45)
    plt.ylabel(ylabel)
    p = sns.scatterplot(data=data, x=x, y=y, color=laranja).get_figure()
    return p


def render_mpl_table(data, col_width=3.0, row_height=0.625, font_size=10,
                     header_color='#c0c0c0', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    '''
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
    '''

    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        _, ax = plt.subplots(figsize=size)
        ax.axis('off')
    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)
    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in mpl_table._cells.items():
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='k')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors)])
    return ax.get_figure(), ax


def contingency_table(df, x, xlabel, clfs):
    '''
    contingency_table Construção das tabelas de contingência.

    Args:
        df (DataFrame): DataFrame contendo os dados para construção das tabelas. 
        x (text object): Nome da coluna no DataFrame contendo os dados do eixo x (e.g. data).
        clfs (List of text object): Nomes das colunas no DataFrame contendo os dados de contingência (e.g. 'severidade').

    Returns:
        DataFrame: Tabela de contingência
    '''

    dg = pd.get_dummies(df, columns=[clfs], prefix=[""], prefix_sep=[""])
    dg = pd.pivot_table(dg, index=x, aggfunc=np.sum)
    dg.reset_index(level=0, inplace=True)
    dg.columns = [xlabel] + dg.columns[1:].tolist()
    return dg


def contingency_plot(df, x, clfs, xlabel):
    '''
    contingency_plot scatter plot das tabelas de contingência.

    Args:
        df (DataFrame): Dados a serem visualizados.
        x (text object): Nome da coluna no DataFrame contendo os dados do eixo x (e.g. data).
        clfs (List of text object): Nomes das colunas no DataFrame contendo os dados de contingência (e.g. 'severidade').
        xlabel (text object)

    Yields:
        Figure: plot de uma severidade/classificação específica
    '''        

    dg = contingency_table(df, x, xlabel, clfs)
    for i in [y for y in dg.columns if y != xlabel]:
        p = scatter_plot(dg, xlabel, i, 
                         xlabel=xlabel, ylabel=f'{i}')
        yield p


def sensor_plot(df, x, sensors, xlabel, sensors_name):
    '''
    sensor_plot scatter plot dos dados dos sensores (e.g.: Aceleração, Bounce, Rock e Suspention Travel).

    Args:
        df (DataFrame): Dados a serem visualizados.
        x (text object): Nome da coluna no DataFrame contendo os dados do eixo x (e.g. data).
        sensors (List of text object): Nomes das colunas no DataFrame contendo os dados dos sensores.
        xlabel (text object)
        sensors_name (List): Nome dos sensores a serem visualizados.
            Note que a ordem deve estar de acordo com a ordem das colunas de df.

    Yields:
        Figure: plot de um sensor específico
    '''

    s = iter(sensors_name)
    for i in sensors:
        p = scatter_plot(df, x, i, 
                         xlabel=xlabel, ylabel=f'{next(s)}')
        yield p


def rest_velocidade_plot(df, x, y, lim_y, lim_label, xlabel, ylabel):
    '''
    rest_velocidade_plot Visualização de restrição de velocidade.

    Args:
        df (DataFrame): Dados a serem visualizados.
        x (text object): Nome da coluna no DataFrame contendo os dados do eixo x (e.g. velocidade).
        y (text object): Nome da coluna no DataFrame contendo os dados do eixo y (e.g. bounce).
        lim_y (List): Limites especificados (e.g. limites de severidade para bounce).
        lim_label (List): Label dos limites especificados. Mesmo tamanho de lim_y.
        xlabel (text object)
        ylabel (text object)

    Returns:
        Figure.
    '''    

    plt.figure()
    plt.style.use(style)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.plot(df[x], df[y], color=laranja, marker=".", linestyle='None')

    pn = np.poly1d(np.polyfit(df[x], df[y], 1))
    X = list(set(df[x]))
    X.sort()
    Y = pn(X)
    plt.plot(X, Y, color=cinza, linestyle='-')
    ci = 1.96*np.std(Y)/np.mean(Y)
    plt.fill_between(X, (Y-ci), (Y+ci), color=cinza, alpha=.25)

    for i in range(lim_y.size):
        plt.plot(X, np.repeat(lim_y[i], len(X), axis=0), color=terra, linestyle='--', linewidth=1)
        plt.text(min(X), lim_y[i]+0.1, lim_label[i], color=terra)

    return plt.gcf()


def comp_velocidade_plot(x, y, lim_y, lim_label, xlabel, ylabel, **kwargs):
    '''
    comp_velocidade_plot Visualização de restrição de velocidade em múltiplas localizações.

    Args:
        x (text object): Nome da coluna no DataFrame contendo os dados do eixo x (e.g. velocidade).
        y (text object): Nome da coluna no DataFrame contendo os dados do eixo y (e.g. bounce).
        lim_y (List): Limites especificados (e.g. limites de severidade para bounce).
        lim_label (List): Label dos limites especificados. Mesmo tamanho de lim_y.
        xlabel (text object)
        ylabel (text object)
        kwargs (Dict): Dicionário contendo os dados a serem visualizados, onde as keys serão utilizadas como labels
            e.g.: {'Km 80':df1, 'Km 160':df2}

    Returns:
        Figure
    '''    
    plt.figure()
    plt.style.use(style)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    for label, df in kwargs.items():
        plt.plot(df[x], df[y], marker=".", linestyle='None', label=label)

    plt.legend(loc='best')

    X = sum([df[x].tolist() for label, df in kwargs.items()], [])
    X = list(set(X))
    X.sort()

    for i in range(lim_y.size):
        plt.plot(X, np.repeat(lim_y[i], len(X), axis=0), color=terra, linestyle='--', linewidth=1)
        plt.text(min(X), lim_y[i]+0.1, lim_label[i], color=terra)

    return plt.gcf()
