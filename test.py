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
    ["52A3026F", "52C41629"],
    ["52A3026F", "52C415CB"],
    ["52A3026F", "52C415FA"],
]

def request_data(base_serial, remote_serial, proxies=True):
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
        "remote-serial": [remote_serial],
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

# レスポンスデータから、欲しいデータに成形する
def remake_dic(response_):
    dic = {}
    for d in response_["devices"]:
        # センサ名とセンサ値のリストを取得
        dic.update({d["name"]: d["channel"]})
    return dic


def main():
    # num = len(list576)
    # count = 0
    # df576_co2 = pd.DataFrame()
    # df576_T = pd.DataFrame()
    # df576_H = pd.DataFrame()

    for n in list576:
        a = request_data(n[0], n[1], proxies=True)
        n = n + 1
        dff_c, dff_t, dff_h = dic_to_df_576(a)
        # df576_co2 = pd.concat([df576_co2, dff_c], axis=1)
        # df576_T = pd.concat([df576_T, dff_t], axis=1)
        # df576_H = pd.concat([df576_H, dff_h], axis=1)


if __name__ == "__main__":
    main()
    schedule.every(1).minutes.do(main)
    while True:
        schedule.run_pending()
        sleep(1)





