import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO

def plot():
    sns.set_theme(style="darkgrid")
    iris = sns.load_dataset("iris")

    f, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect("equal")

    p = sns.kdeplot(
        data=iris.query("species != 'versicolor'"),
        x="sepal_width",
        y="sepal_length",
        hue="species",
        thresh=.1,
    ).get_figure()
    buf = BytesIO()
    p.savefig(buf, format='png')
    buf.seek(0)
    
    return(buf)