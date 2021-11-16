import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib import style
import pandas as pd

style.use('ggplot')
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)


def animate(i):
    graph_data = open('graph_data.txt', 'r').read()
    lines = graph_data.split('\n')
    # xs = []
    # ys = []
    dic = {}
    for line in lines:
        if len(line) > 1:
            x, y = line.split()
            dic[x] = y
            # xs.append(x)
            # ys.append(int(y))
    # print(dic)
    ax.clear()
    data = {'Occurence': dic}
    # df = pd.DataFrame(dic, columns=['Occ'], index=dic.keys())
    df = pd.DataFrame(data)
    df = df.astype(float)
    df.plot.barh(ax=ax)
    # ax.barh(range(len(dic)), dic.values(), align='center')

ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()
