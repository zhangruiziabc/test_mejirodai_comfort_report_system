import numpy as np
import pandas as pd

xx = 587
yy = 150


def bilinear(src, xx, yy, df):
    """
    #     疎なデータを持つ配列に対しバイリニア補完を行う
    #     :param src: 入力配列
    #     :return: 補完後の配列
    #     参考URL(https://yamaken1343.hatenablog.jp/entry/2018/06/28/192639)
    #"""

    def search_near(src, x, y, df):
        """
        データのある近傍の空調機を検索し, 座標を返す
        :param src: 検索する配列
        :param x: 基準点のx座標(クリックされた点のx)
        :param y: 基準点のy座標(クリックされた点のy)
        :return: 検索した1点を2*1のnumpy.arrayで返す
        """

        def min_pear(a, b, x, y):
            """
            基準点とリスト内の2点間の距離が最も小さいペアを返す
            :param a: x座標のリスト
            :param b: y座標のリスト
            :param x: 基準点のx
            :param y: 基準点のy
            :return: リスト内からペア三つをarrayとして出力する
            """
            # 近傍に点が1点以下でもあるだけの点を用いて補完を行う
            if len(a) == 0:
                return x, y

            add = np.power((a - x), 2) + np.power((b - y), 2)
            add_sort = np.argsort(add)
            add_sort_array = np.array(
                [
                    [a[add_sort[0]], b[add_sort[0]]],
                    [a[add_sort[1]], b[add_sort[1]]],
                    [a[add_sort[2]], b[add_sort[2]]],
                    [a[add_sort[3]], b[add_sort[3]]],
                ]
            )
            return add_sort_array

        # 処理簡便化のためデータの有無を2値で持つ
        # 0であればFalse 0でなければTrue
        src = np.array(src != 0)
        # 処理対象の点にデータがあるとき, その点を4近傍として返す
        if src[x, y]:
            return np.array([[x, y], [x, y], [x, y], [x, y]])

        try:
            # スライスされるため, indexに入る値はsrcのインデックスと互換性がないことに注意する
            index_x, index_y = np.array(df.iloc[:, 2]), np.array(df.iloc[:, 1])
            array_top4 = min_pear(index_x, index_y, x, y)
            return array_top4

        # データが見つからなくても止まらないようにする
        except:
            return None

    point = [xx, yy]  # クリックした位置 x,yが逆になっていない

    n4p = search_near(src, point[1], point[0], df)
    print(n4p)


if __name__ == "__main__":
    path = "input\\"
    df = pd.read_csv(path + "AirconCoordinates.csv")
    x = 637  # 背景データのピクセル数x
    y = 756  # 背景データのピクセル数y
    Contour_Diagram_np = np.zeros((y, x), np.float64)
    print(Contour_Diagram_np)
    near_aircon = bilinear(Contour_Diagram_np, xx, yy, df)
