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


def contingency_plot(df, local, element, clsf_name):
    """
    contingency_plot scatter plot das tabelas de contingência.

    Args:
        df (DataFrame): Tabela contendo os dados a serem visualizados.
            Veja que a coluna 'data' (data da informação) é obrigatória e 'severidade' ou 'classificação' são esperadas
        local (text object): Localização do trecho da via, em termos de Linha (GTG).
        element (text object): Elemento da via.
        clsf_name (text object): Nome do objeto em contagem. Espera-se severidade ou classificação

    Yields:
        Figure: plot de uma severidade/classificação específica
    """        

    dg = contingency_table(df)
    for i in [x for x in dg.columns if x != 'data']:
        p = scatter_plot(dg, 'data', i, 
                         title=f'Localização: {local} - {element}', 
                         xlabel='data', ylabel=f'contagem {clsf_name}\n{i}')
        yield p


def sensor_plot(df, local, element, sensors_name):
    """
    sensor_plot scatter plot dos dados dos sensores (Aceleração, Bounce, Rock e Suspention Travel).

    Args:
        df (DataFrame): Tabela contendo os dados a serem visualizados.
            Veja que a coluna 'data' (data da informação) é obrigatória e os dados dos sensores são esperados.
        local (text object): Localização do trecho da via, em termos de Linha (GTG).
        element (text object): Elemento da via.
        sensors_name (list): Nome dos sensores a serem visualizados.
            Note que a ordem deve estar de acordo com a ordem das colunas de df.

    Yields:
        Figure: plot de um sensor específico
    """
        
    s = iter(sensors_name)
    for i in [x for x in df.columns if x != 'data']:
        p = scatter_plot(df, 'data', i, 
                         title=f'Localização: {local} - {element}', 
                         xlabel='data', ylabel=f'{next(s)}')
        yield p
