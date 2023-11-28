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
# 警告の非表示化
import warnings
warnings.simplefilter('ignore')

list576 = [
    # 机上面22個
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
    # 吸込み6個
    ["58580816", "52C415E0"],
    ["58580816", "52C415DD"],
    ["58580816", "52C415F9"],
]

list576_add = [
    ["52A3026F", "52C41629"],
    ["52A3026F", "52C415CB"],
    ["52A3026F", "52C415FA"],
]

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


def remake_dic(response_):
    dic = {}
    dic2 = {}
    for d in response_["devices"]:
        # センサ名とセンサ値のリストを取得
        dic.update({d["serial"]: d["channel"]})
        dic2.update({d["serial"]: datetime.datetime.fromtimestamp(int(d["unixtime"]))})
    return dic, dic2


def main():
    try:
        dt_now = datetime.datetime.now()
        dt_2min_before = dt_now - datetime.timedelta(minutes=1)
        dt_3min_before = dt_now - datetime.timedelta(minutes=2)
        df576 = pd.DataFrame(columns=["time", "serial", "CO2", "temp", "humid"])
        df576_add = pd.DataFrame(columns=["time", "serial", "CO2", "temp", "humid"])

        try:
            a = request_data("58580816", proxies=True)
            b = request_data_add("52A3026F", proxies=True)
        except:
            a = request_data("58580816", proxies=False)
            b = request_data_add("52A3026F", proxies=False)
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

        for n in list576_add:
            try:
                dc_add = dict_c_add[n[1]]
                dd_add = dict_d_add[n[1]]

                dff_c_add = pd.DataFrame(
                    [
                        [
                            dd_add,
                            n[1],
                            float(dc_add[0]["value"]),
                            float(dc_add[1]["value"]),
                            float(dc_add[2]["value"]),
                        ]
                    ],
                    columns=["time", "serial", "CO2", "temp", "humid"],
                )
                df576_add = pd.concat([df576_add, dff_c_add], axis=0)
            except:
                # traceback.print_exc()
                pass

        df576.iloc[
            df576.time < df576.time.max() - datetime.timedelta(minutes=1), [2, 3, 4]
        ] = np.nan
        df576 = df576.dropna()

        df576_add.iloc[
            df576_add.time < df576_add.time.max() - datetime.timedelta(minutes=1), [2, 3, 4]
        ] = np.nan
        df576_add = df576_add.dropna()

        df_add = pd.concat([df576, df576_add])
        CO2_ave = df_add['CO2'].mean()
        print(CO2_ave)

        # ノードレッドでの制御実行
        CO2 = {
            "latestCO2": CO2_ave,
        }
        headers = {"Content-Type": "application/json"}
        print("http://172.31.25.131:1880/CO2Control")
        url = "http://172.31.25.131:1880/CO2Control"
        CO2_res= requests.post(
            url, json=CO2, headers=headers
        )
        CO2_res= CO2_res.json()
    except:
        traceback.print_exc()


if __name__ == "__main__":
    main()
    schedule.every(5).minutes.do(main)
    while True:
        schedule.run_pending()
        sleep(1)

