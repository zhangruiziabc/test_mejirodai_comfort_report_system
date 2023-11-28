# https://yamaken1343.hatenablog.jp/entry/2018/06/28/192639
import requests
import json
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
from PIL import Image
import datetime
import schedule
from time import sleep
from io import BytesIO
import base64
import time
import traceback
import csv

# 警告の非表示化
import warnings

warnings.simplefilter("ignore")
#################################パラメータ指定####################################
path = "static/uploads/"
file = "mejirodai_3.jpg"
img = Image.open(path + file)
xmax, ymax = img.size
# 手動で設定するパラメータ
zip = 10
sensor_distance = 3  # センサ間の距離(m)
distance_y = 30  # 実際の部屋のy方向の距離(m)

x = int(math.ceil(xmax / zip))
y = int(math.ceil(ymax / zip))
# Contour_Diagram_np = np.zeros((y, x), np.float64)
cb_min, cb_max = 20, 28  # color bar range
cb_div = 32  # color bar division

# σ = sensor_distance / 6
σ = (sensor_distance / zip) / 3  # d = 3σ
pixel_to_distance = distance_y / ymax  # 実際の部屋のｙ方向の距離とピクセルとの関係


def request_data(base_serial, proxies=True):
    url = "https://api.webstorage.jp/v1/devices/current"
    proxies_dic = {
        "http": "http://gwproxy.daikin.co.jp:3128",
        "https": "http://gwproxy.daikin.co.jp:3128",
    }  # プロキシアドレスを入力
    header = {
        "Host": "api.webstorage.jp:443",
        "Content-Type": "application/json",
        "X-HTTP-Method-Override": "GET",
    }
    querystring = {
        "api-key": "pq2471h4eqs1rqql20r7048jrbbkjcm8vbkr4p6t725h2",
        "login-id": "tbaf2711",
        "login-pass": "daikin",
        "base-serial": [base_serial],
    }
    if proxies:
        response = requests.post(
            url,
            json.dumps(querystring).encode("utf-8"),
            proxies=proxies_dic,
            headers=header,
            verify=False,
        ).json()
    else:
        response = requests.post(
            url, json.dumps(querystring).encode("utf-8"), headers=header, verify=False
        ).json()
    return response


def request_data_add(base_serial, proxies=True):
    url = "https://api.webstorage.jp/v1/devices/current"
    proxies_dic = {
        "http": "http://gwproxy.daikin.co.jp:3128",
        "https": "http://gwproxy.daikin.co.jp:3128",
    }  # プロキシアドレスを入力
    header = {
        "Host": "api.webstorage.jp:443",
        "Content-Type": "application/json",
        "X-HTTP-Method-Override": "GET",
    }
    querystring = {
        "api-key": "ohs622h5aojal3c9noqo5eo4kvn06arte665iiqg73dr2",
        "login-id": "tbad5187",
        "login-pass": "tnglab",
        "base-serial": [base_serial],
    }
    if proxies:
        response = requests.post(
            url,
            json.dumps(querystring).encode("utf-8"),
            proxies=proxies_dic,
            headers=header,
            verify=False,
        ).json()
    else:
        response = requests.post(
            url, json.dumps(querystring).encode("utf-8"), headers=header, verify=False
        ).json()
    return response


def remake_dic(response_):
    dic = {}
    dic2 = {}
    for d in response_["devices"]:
        # センサ名とセンサ値のリストを取得
        dic.update({d["serial"]: d["channel"]})
        dic2.update({d["serial"]: datetime.datetime.fromtimestamp(int(d["unixtime"]))})
    return dic, dic2


def bilinear(src):
    """
    疎なデータを持つ配列に対しバイリニア補完を行う
    :param src: 入力配列
    :return: 補完後の配列
    参考URL(https://yamaken1343.hatenablog.jp/entry/2018/06/28/192639)
    """

    def search_near(src, x, y):
        """
        データのある近傍4点を検索し, 座標を返す
        :param src: 検索する配列
        :param x: 基準点のx座標
        :param y: 基準点のy座標
        :return: 検索した4点を2*4のnumpy.arrayで返す
        """

        def min_pear(a, b, x, y):
            """
            基準点とリスト内の2点間の距離が最も小さいペアを返す
            :param a: x座標のリスト
            :param b: y座標のリスト
            :param x: 基準点のx
            :param y: 基準点のy
            :return: リスト内のペア
            """
            # 近傍に点が4点以下でもあるだけの点を用いて補完を行う
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
        src = np.array(src != 0)

        # 処理対象の点にデータがあるとき, その点を4近傍として返す
        if src[x, y]:
            return np.array([[x, y], [x, y], [x, y], [x, y]])

        try:
            # スライスされるため, indexに入る値はsrcのインデックスと互換性がないことに注意する
            index_x, index_y = np.where(src[:, :])
            array_top4 = min_pear(index_x, index_y, x, y)
            return array_top4

        # データが見つからなくても止まらないようにする
        except:
            return None

    it = np.nditer(src, flags=["multi_index"])
    dst = np.zeros(src.shape)
    # 配列の各要素をなめる
    while not it.finished:
        idx = it.multi_index  # 現在参照する要素のインデックス
        it.iternext()

        # near four points 近傍四点を取得
        n4p = search_near(src, idx[0], idx[1])
        # 4点のどれかにデータがない場合の処理
        if n4p is None:
            continue

        # 参照する要素と近傍4点の距離を取得
        near_4_points_dist = np.array(
            [
                math.exp(
                    (np.linalg.norm((n4p[0] - idx) * pixel_to_distance)) ** 2
                    / (-2.0 * 0.2**2)
                ),
                math.exp(
                    (np.linalg.norm((n4p[1] - idx) * pixel_to_distance)) ** 2
                    / (-2.0 * 0.2**2)
                ),
                math.exp(
                    (np.linalg.norm((n4p[2] - idx) * pixel_to_distance)) ** 2
                    / (-2.0 * 0.2**2)
                ),
                math.exp(
                    (np.linalg.norm((n4p[3] - idx) * pixel_to_distance)) ** 2
                    / (-2.0 * 0.2**2)
                ),
            ]
        )
        # 近傍点と参照点が同じ場合と近傍点がないときnanが入るので, 変換する
        near_4_points_dist[np.isnan(near_4_points_dist)] = 0

        # 参照要素とデータの点が重なった時の処理
        if near_4_points_dist.sum() == 0:
            dst[idx] = src[idx]
            continue

        # 近傍点と参照点が同じ場合無視したいので次の処理でゼロにするために代入
        near_4_points_dist[near_4_points_dist == 0] = np.inf

        # 小さいほうが値が大きくなるように逆数を取る(距離なので近いほうが良いというふうにしたい)
        near_4_points_score = near_4_points_dist

        # 和が1になるように正規化
        near_4_points_score /= near_4_points_score.sum()

        # 結果を格納する配列に代入
        for i in range(len(n4p)):
            a, b = n4p[i]
            dst[idx] += near_4_points_score[i] * src[a, b]

    return dst


def plot(
    time,
    df_sensor_position,
    df_aircon_position,
    Contour_Diagram_np,
):
    # global Contour_Diagram_np
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot()
    x_np = np.arange(0, x)
    y_np = np.arange(0, y)
    interval_of_cf = np.linspace(cb_min, cb_max, cb_div + 1)
    # # make X and Y matrices representing x and y values of 2d plane
    X, Y = np.meshgrid(x_np, y_np)
    Z = Contour_Diagram_np

    # for i in range(len(df_sensor_position)):
    #     ax.scatter(
    #         math.ceil(df_sensor_position["x"][i] / zip),
    #         y - math.ceil(df_sensor_position["y"][i] / zip),
    #         c="k",
    #     )

    #     ax.text(
    #         math.ceil(df_sensor_position["x"][i] / zip) + 1,
    #         y - math.ceil(df_sensor_position["y"][i] / zip) + 1,
    #         round(float(df_sensor_position["temp"][i]), 1),
    #         size=8,
    #     )

    # for n in range(len(df_aircon_position)):
    #     if df_aircon_position["OnOff"][n] == False:
    #         ax.scatter(
    #             math.ceil(df_aircon_position["x"][n] / zip),
    #             y - math.ceil(df_aircon_position["y"][n] / zip),
    #             marker="s",
    #             c="r",
    #         )

    #         ax.text(
    #             math.ceil(df_aircon_position["x"][n] / zip) + 1,
    #             y - math.ceil(df_aircon_position["y"][n] / zip) - 2,
    #             df_aircon_position["serial"][n],
    #             size=6,
    #             c="r",
    #         )
    #     elif df_aircon_position["OnOff"][n] == True:
    #         ax.scatter(
    #             math.ceil(df_aircon_position["x"][n] / zip),
    #             y - math.ceil(df_aircon_position["y"][n] / zip),
    #             marker="s",
    #             c="g",
    #         )

    #         ax.text(
    #             math.ceil(df_aircon_position["x"][n] / zip) + 1,
    #             y - math.ceil(df_aircon_position["y"][n] / zip) - 2,
    #             df_aircon_position["serial"][n],
    #             size=6,
    #             c="g",
    #         )
    # plt.contourf(X, Y, Z, cmap='jet', norm=Normalize(vmin=19, vmax=22), alpha=0.2)
    # mappable = ax.contourf(X, Y, Z, interval_of_cf, cmap='jet', vmin=18, vmax=22, alpha=0.2, extend="both")
    # mappable = ax.contourf(X, Y, Z, interval_of_cf, cmap='jet', antialiased=True, alpha=0.4, extend="both")
    mappable = ax.contourf(
        X,
        Y,
        Z,
        interval_of_cf,
        cmap="jet",
        antialiased=True,
        vmin=cb_min,
        vmax=cb_max,
        alpha=0.0,
        extend="both",
    )
    fig.colorbar(mappable, ax=ax)
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    ax.imshow(img, extent=[*xlim, *ylim], aspect="auto")
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
    plt.title(time.strftime("%Y-%m-%d  %H:%M"))
    io = BytesIO()
    fig.savefig(io, format="png")
    # base64 形式に変換する。
    io.seek(0)
    base64_img = base64.b64encode(io.read()).decode()
    # plt.show()
    return base64_img


def get_current_state(equipmentId, proxies=True):
    url = "https://3w1p12712a.execute-api.ap-northeast-1.amazonaws.com/prod/get_current_quipment_states"
    # url = "https://wd2owx7oy1.execute-api.ap-northeast-1.amazonaws.com/prod/"
    # url = "https://gpf.dk-mejirodai.com/"

    param = json.dumps(
        {
            "equipmentId": equipmentId,
        }
    )
    # proxies_dic = {
    #     "http": "http://gwproxy.daikin.co.jp:3128",
    #     "https": "http://gwproxy.daikin.co.jp:3128",
    # }
    if proxies:
        res = requests.post(
            url,
            data=param,
            # proxies=proxies_dic,
            headers={
                "Content-Type": "application/json",
                "x-api-key": "KeUjOrNIAS6Jcu9kA7hKCjP6QwEvtJE7HiifSMy3",
            },
            verify=False,
        ).json()
    else:
        res = requests.post(
            url,
            data=param,
            headers={
                "Content-Type": "application/json",
                "x-api-key": "KeUjOrNIAS6Jcu9kA7hKCjP6QwEvtJE7HiifSMy3",
            },
            verify=False,
        ).json()

    data = res.get("body")
    data2 = json.loads(data)
    return data2


list576 = [
    ["58580816", "52C4162B"],
    ["58580816", "52C415C7"],
    ["58580816", "52C41630"],
    ["58580816", "52C4162C"],
    ["58580816", "52C4162D"],
    ["58580816", "52C4161A"],
    ["58580816", "52C4162F"],
    ["58580816", "52C41606"],
    ["58580816", "52C41605"],
    ["58580816", "52C41604"],
    ["58580816", "52C41608"],
    ["58580816", "52C41607"],
    ["58580816", "52C41601"],
    ["58580816", "52C41600"],
    ["58580816", "52C415FF"],
    ["58580816", "52C41603"],
    ["58580816", "52C415F5"],
    ["58580816", "52C415F7"],
    ["58580816", "52C415FC"],
    ["58580816", "52C415FB"],
    ["58580816", "52C415F6"],
    ["58580816", "52C41602"],
]

list503 = [
    ["58580C57", "528424F3"],
    ["58580C57", "5284280C"],
    ["58580C57", "5284259D"],
    ["58580C57", "52842809"],
    ["58580C57", "52842811"],
    ["58580C57", "52841EEF"],
    ["58580C57", "52841EF0"],
    ["58580C57", "5284280E"],
]

deviceIDs = ["wg3-1_0001",
            "wg3-1_0002", 
            "wg3-1_0003", 
            "wg3-1_0004", 
            "wg3-1_0005", 
            "wg3-1_0006", 
            "wg3-1_0007", 
            "wg3-1_0008", 
            "wg3-1_0009", 
            "wg3-1_0010", 
            "wg3-1_0011", 
            "wg3-1_0012", 
            "wg3-1_0013", 
            "wg3-1_0014", 
            "wg3-1_0015", 
            "wg3-1_0016", 
            "wg3-1_0017", 
            "wg3-1_0018", 
            "wg3-1_0019", 
            "wg3-1_0020", 
            "wg3-1_0021", 
            "wg3-1_0022", 
            "wg3-1_0023", 
            "wg3-1_0024", 
            "wg3-1_0025", 
            "wg3-1_0026", 
            "wg3-1_0027", 
            "wg3-1_0028", 
            "wg3-1_0029", 
            "wg3-1_0030", 
            "wg3-1_0031", 
            "wg3-1_0032", 
            "wg3-1_0033", 
            "wg3-1_0034", 
            "wg3-1_0035", 
            "wg3-1_0036", 
            "wg3-1_0037", 
            "wg3-1_0038", 
            "wg3-1_0039", 
            "wg3-1_0040", 
            "wg3-1_0041", 
            "wg3-1_0042", 
            "wg3-1_0043", 
            "wg3-1_0044"]



def main():
    try:
        current_state_A = get_current_state("a1fe7aa0-7a4a-11ec-b3c1-aa6ab95de3cd")
        current_state_B = get_current_state("a1f586d4-7a4a-11ec-b3c1-aa6ab95de3cd")
        current_state_C = get_current_state("a1f2052c-7a4a-11ec-b3c1-aa6ab95de3cd")
        current_state_D = get_current_state("02216ce0-355c-11ed-b9a3-3a77aff4ad92")
        current_state_E = get_current_state("02226762-355c-11ed-b9a3-3a77aff4ad92")
        current_state_F = get_current_state("022218de-355c-11ed-b9a3-3a77aff4ad92")
        current_state_G = get_current_state("0221c5c8-355c-11ed-b9a3-3a77aff4ad92")
        current_state_H = get_current_state("02211736-355c-11ed-b9a3-3a77aff4ad92")

        OnOff_A = current_state_A["OnOff_now"]
        OnOff_B = current_state_B["OnOff_now"]
        OnOff_C = current_state_C["OnOff_now"]
        OnOff_D = current_state_D["OnOff_now"]
        OnOff_E = current_state_E["OnOff_now"]
        OnOff_F = current_state_F["OnOff_now"]
        OnOff_G = current_state_G["OnOff_now"]
        OnOff_H = current_state_H["OnOff_now"]

        OnOff = [
            OnOff_A,
            OnOff_B,
            OnOff_C,
            OnOff_D,
            OnOff_E,
            OnOff_F,
            OnOff_G,
            OnOff_H,
        ]
        # global Contour_Diagram_np
        Contour_Diagram_np = np.zeros((y, x), np.float64)
        dt_now = datetime.datetime.now()
        dt_2min_before = dt_now - datetime.timedelta(minutes=1)
        dt_3min_before = dt_now - datetime.timedelta(minutes=2)
        df576 = pd.DataFrame(columns=["time", "serial", "CO2", "temp", "humid"])
        df503 = pd.DataFrame(columns=["time", "serial", "temp"])

        try:
            a = request_data("58580816", proxies=True)
            b = request_data_add("58580C57", proxies=True)
        except:
            a = request_data("58580816", proxies=False)
            b = request_data_add("58580C57", proxies=False)
        dict_c, dict_d = remake_dic(a)
        dict_c_add, dict_d_add = remake_dic(b)

        for n in list576:
            try:
                dc = dict_c[n[1]]
                dd = dict_d[n[1]]

                dff_c = pd.DataFrame(
                    [
                        [
                            dd,
                            n[1],
                            float(dc[0]["value"]),
                            float(dc[1]["value"]),
                            float(dc[2]["value"]),
                        ]
                    ],
                    columns=["time", "serial", "CO2", "temp", "humid"],
                )
                df576 = pd.concat([df576, dff_c], axis=0)
            except:
                traceback.print_exc()
                # pass

        for n in list503:
            try:
                dc_add = dict_c_add[n[1]]
                dd_add = dict_d_add[n[1]]

                dff_c_add = pd.DataFrame(
                    [
                        [
                            dd_add,
                            n[1],
                            float(dc_add[0]["value"]),
                        ]
                    ],
                    columns=["time", "serial", "temp"],
                )
                df503 = pd.concat([df503, dff_c_add], axis=0)
            except:
                traceback.print_exc()
                # pass

        df576.iloc[
            df576.time < df576.time.max() - datetime.timedelta(minutes=2), [2, 3, 4]
        ] = np.nan
        df576 = df576.dropna()
        df576.to_csv("/home/ec2-user/comfort_report_system_AWS/input/ondotori_data_df576.csv")

        df503.iloc[
            df503.time < df503.time.max() - datetime.timedelta(minutes=2), [2]
        ] = np.nan
        df503 = df503.dropna()
        df503.to_csv("/home/ec2-user/comfort_report_system_AWS/input/ondotori_data_df503.csv")
        
        try:
            path = "/home/ec2-user/comfort_report_system_AWS/input/"
            df_position_576 = pd.read_csv(path + "sensor_position_576.csv")
            df_position_503 = pd.read_csv(path + "sensor_position_503.csv")
            aircon_position = pd.read_csv(path + "aircon_position.csv")
            df_m_576 = pd.merge(df_position_576, df576)
            df_m_503 = pd.merge(df_position_503, df503)
            df_m = pd.concat([df_m_576, df_m_503])
            df_m = df_m.reset_index(drop=True)
            for m in range(len(OnOff)):
                aircon_position["OnOff"][m] = OnOff[m]

            for index, row in df_m.iterrows():
                Contour_Diagram_np[
                    y - math.ceil(row["y"] / zip), math.ceil(row["x"] / zip)
                ] = row["temp"]

            Contour_Diagram_np = bilinear(Contour_Diagram_np)
            Contour_Diagram_np[
                : int(math.ceil(213 / zip)), : int(math.ceil(130 / zip))
            ] = np.nan
            Contour_Diagram_np[
                int(math.ceil(520 / zip)) :, : int(math.ceil(130 / zip))
            ] = np.nan
            Contour_Diagram_np[
                : int(math.ceil(540 / zip)), int(math.ceil(330 / zip)) :
            ] = np.nan
            Contour_Diagram_np[
                int(math.ceil(725 / zip)) :, int(math.ceil(130 / zip)) :
            ] = np.nan
            # img = plot(dt_2min_before, df_position)

            fig = plot(
                df576.time.max(),
                df_m,
                aircon_position,
                Contour_Diagram_np,
            )

        except:
            traceback.print_exc()

        for deviceID in deviceIDs:
            plt.savefig(
                "/home/ec2-user/comfort_report_system_AWS/static/images/temperature_distribution_" + deviceID + ".png"
            )
        plt.clf()
        plt.close()
    except:
        traceback.print_exc()


if __name__ == "__main__":
    main()
    schedule.every(1).minute.at(":00").do(main)
    while True:
        schedule.run_pending()
        sleep(1)
