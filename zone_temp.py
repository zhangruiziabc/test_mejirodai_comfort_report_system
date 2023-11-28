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
import traceback

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

zip = 10
xmax = 637
ymax = 756
xmax = int(math.ceil(xmax / zip))
ymax = int(math.ceil(ymax / zip))


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
                    (np.linalg.norm((n4p[0] - idx) * (30 / 756))) ** 2
                    / (-2.0 * 0.2 * 2)
                ),
                math.exp(
                    (np.linalg.norm((n4p[1] - idx) * (30 / 756))) ** 2
                    / (-2.0 * 0.2**2)
                ),
                math.exp(
                    (np.linalg.norm((n4p[2] - idx) * (30 / 756))) ** 2
                    / (-2.0 * 0.2**2)
                ),
                math.exp(
                    (np.linalg.norm((n4p[3] - idx) * (30 / 756))) ** 2
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

def main():
    try:
        Contour_Diagram_np = np.zeros((ymax, xmax), np.float64)
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
                # traceback.print_exc()
                pass

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
                # traceback.print_exc()
                pass

        df576.iloc[
            df576.time < df576.time.max() - datetime.timedelta(minutes=2), [2, 3, 4]
        ] = np.nan
        df576 = df576.dropna()

        df503.iloc[
            df503.time < df503.time.max() - datetime.timedelta(minutes=2), [2]
        ] = np.nan
        df503 = df503.dropna()

        try:
            path = "/home/ec2-user/comfort_report_system_AWS/input/"
            df_position_576 = pd.read_csv(path + "sensor_position_576.csv")
            df_position_503 = pd.read_csv(path + "sensor_position_503.csv")
            df_m_576 = pd.merge(df_position_576, df576)
            df_m_503 = pd.merge(df_position_503, df503)
            df_m = pd.concat([df_m_576, df_m_503])
            df_m = df_m.reset_index(drop=True)
            for index, row in df_m.iterrows():
                Contour_Diagram_np[
                    math.ceil(row["y"] / zip), math.ceil(row["x"] / zip) 
                ] = row["temp"]

            Z = bilinear(Contour_Diagram_np)
            Z[: int(math.ceil(238 / zip)), : int(math.ceil(128 / zip))] = np.nan
            Z[int(math.ceil(550 / zip)) :, : int(math.ceil(130 / zip))] = np.nan
            Z[int(math.ceil(211 / zip)):, int(math.ceil(330 / zip)) :] = np.nan
            Z[: int(math.ceil(44 / zip)), : int(math.ceil(634 / zip))] = np.nan
            # エリアごとに温度算出
            Z_1 = Z.copy()
            Z_1[int(math.ceil(210 / zip)):] = np.nan
            Z_1[:, :int(math.ceil(480 / zip))] = np.nan
            Z_1_temp = np.nanmean(Z_1)

            Z_2 = Z.copy()
            Z_2[int(math.ceil(210 / zip)):] = np.nan
            Z_2[:, int(math.ceil(480 / zip)):] = np.nan
            Z_2[:, :int(math.ceil(350 / zip))] = np.nan
            Z_2_temp = np.nanmean(Z_2)

            Z_3 = Z.copy()
            Z_3[int(math.ceil(210 / zip)):] = np.nan
            Z_3[:, int(math.ceil(350 / zip)):] = np.nan
            Z_3_temp = np.nanmean(Z_3)

            Z_4 = Z.copy()
            Z_4[:int(math.ceil(220 / zip))] = np.nan
            Z_4[int(math.ceil(350 / zip)):] = np.nan
            Z_4[:, :int(math.ceil(180 / zip))] = np.nan
            Z_4_temp = np.nanmean(Z_4)

            Z_5 = Z.copy()
            Z_5[:int(math.ceil(350 / zip))] = np.nan
            Z_5[int(math.ceil(550 / zip)):] = np.nan
            Z_5[:, :int(math.ceil(180 / zip)):] = np.nan
            Z_5_temp = np.nanmean(Z_5)

            Z_6 = Z.copy()
            Z_6[:int(math.ceil(550 / zip))] = np.nan
            Z_6_temp = np.nanmean(Z_6)

            Z_7 = Z.copy()
            Z_7[:int(math.ceil(350 / zip))] = np.nan
            Z_7[int(math.ceil(550 / zip)):] = np.nan
            Z_7[:, int(math.ceil(180 / zip)):] = np.nan
            Z_7_temp = np.nanmean(Z_7)

            Z_8 = Z.copy()
            Z_8[:int(math.ceil(240 / zip))] = np.nan
            Z_8[int(math.ceil(350 / zip)):] = np.nan
            Z_8[:, int(math.ceil(180 / zip)):] = np.nan
            Z_8_temp = np.nanmean(Z_8)

            # ノードレッドでの制御実行
            temperature_Z_1 = {
            "latestTemperature": Z_1_temp,
            "equipmentName": "MAC-2-1-2a_D",
            }
            questionnairess_data_Z_1 = temperature_Z_1
            questionnairess_headers = {"Content-Type": "application/json"}
            print("http://172.31.25.131:1880/equipmentControlForSeatRecommend")
            url = "http://172.31.25.131:1880/equipmentControlForSeatRecommend"
            res_Z_1 = requests.post(
                url, json=questionnairess_data_Z_1, headers=questionnairess_headers
            )
            res_Z_1 = res_Z_1.json()

            temperature_Z_2 = {
            "latestTemperature": Z_2_temp,
            "equipmentName": "MAC-2-1-2a_E",
            }
            questionnairess_data_Z_2 = temperature_Z_2
            questionnairess_headers = {"Content-Type": "application/json"}
            print("http://172.31.25.131:1880/equipmentControlForSeatRecommend")
            url = "http://172.31.25.131:1880/equipmentControlForSeatRecommend"
            res_Z_2 = requests.post(
                url, json=questionnairess_data_Z_2, headers=questionnairess_headers
            )
            res_Z_2 = res_Z_2.json()

            temperature_Z_3 = {
            "latestTemperature": Z_3_temp,
            "equipmentName": "MAC-2-1-2a_C",
            }
            questionnairess_data_Z_3 = temperature_Z_3
            questionnairess_headers = {"Content-Type": "application/json"}
            print("http://172.31.25.131:1880/equipmentControlForSeatRecommend")
            url = "http://172.31.25.131:1880/equipmentControlForSeatRecommend"
            res_Z_3 = requests.post(
                url, json=questionnairess_data_Z_3, headers=questionnairess_headers
            )
            res_Z_3 = res_Z_3.json()

            temperature_Z_4 = {
            "latestTemperature": Z_4_temp,
            "equipmentName": "MAC-2-1-2a_A",
            }
            questionnairess_data_Z_4 = temperature_Z_4
            questionnairess_headers = {"Content-Type": "application/json"}
            print("http://172.31.25.131:1880/equipmentControlForSeatRecommend")
            url = "http://172.31.25.131:1880/equipmentControlForSeatRecommend"
            res_Z_4 = requests.post(
                url, json=questionnairess_data_Z_4, headers=questionnairess_headers
            )
            res_Z_4 = res_Z_4.json()

            temperature_Z_5 = {
            "latestTemperature": Z_5_temp,
            "equipmentName": "MAC-2-1-2a_F",
            }
            questionnairess_data_Z_5 = temperature_Z_5
            questionnairess_headers = {"Content-Type": "application/json"}
            print("http://172.31.25.131:1880/equipmentControlForSeatRecommend")
            url = "http://172.31.25.131:1880/equipmentControlForSeatRecommend"
            res_Z_5 = requests.post(
                url, json=questionnairess_data_Z_5, headers=questionnairess_headers
            )
            res_Z_5 = res_Z_5.json()

            temperature_Z_6 = {
            "latestTemperature": Z_6_temp,
            "equipmentName": "MAC-2-1-2a_G",
            }
            questionnairess_data_Z_6 = temperature_Z_6
            questionnairess_headers = {"Content-Type": "application/json"}
            print("http://172.31.25.131:1880/equipmentControlForSeatRecommend")
            url = "http://172.31.25.131:1880/equipmentControlForSeatRecommend"
            res_Z_6 = requests.post(
                url, json=questionnairess_data_Z_6, headers=questionnairess_headers
            )
            res_Z_6 = res_Z_6.json()

            temperature_Z_7 = {
            "latestTemperature": Z_7_temp,
            "equipmentName": "MAC-2-1-2a_H",
            }
            questionnairess_data_Z_7 = temperature_Z_7
            questionnairess_headers = {"Content-Type": "application/json"}
            print("http://172.31.25.131:1880/equipmentControlForSeatRecommend")
            url = "http://172.31.25.131:1880/equipmentControlForSeatRecommend"
            res_Z_7 = requests.post(
                url, json=questionnairess_data_Z_7, headers=questionnairess_headers
            )
            res_Z_7 = res_Z_7.json()

            temperature_Z_8 = {
            "latestTemperature": Z_8_temp,
            "equipmentName": "MAC-2-1-2a_B",
            }
            questionnairess_data_Z_8 = temperature_Z_8
            questionnairess_headers = {"Content-Type": "application/json"}
            print("http://172.31.25.131:1880/equipmentControlForSeatRecommend")
            url = "http://172.31.25.131:1880/equipmentControlForSeatRecommend"
            res_Z_8 = requests.post(
                url, json=questionnairess_data_Z_8, headers=questionnairess_headers
            )
            res_Z_8 = res_Z_8.json()
        
        except:
            traceback.print_exc()
    except:
        traceback.print_exc()

if __name__ == "__main__":
    main()
    schedule.every(1).minutes.do(main)
    while True:
        schedule.run_pending()
        sleep(1)

