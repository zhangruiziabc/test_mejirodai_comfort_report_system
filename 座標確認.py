# https://yamaken1343.hatenablog.jp/entry/2018/06/28/192639

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
from PIL import Image
import datetime


if __name__ == "__main__":
    #################################パラメータ指定####################################
    path = "static\\images\\"
    img = Image.open(path + 'temperature_distribution_4.png')

    # 出力
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1)
    ax.imshow(img)
    plt.show()


