from flask import Flask, render_template, request
import requests, json
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib import patches
import datetime
import math
import tkinter as tk
import tkinter.messagebox as messagebox
import matplotlib
from io import BytesIO

matplotlib.use("Agg")

too_hot = False
hot = False
comfortable = False
cool = False
too_cool = False
zip = 10

password_defult = "aaaa"

# Flaskオブジェクトの生成
app = Flask(__name__)

# ルート( /device_register )へアクセスがあった時
# @app.route("/device_register", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def device_register():
    return render_template(
        "device_register.html",
    )

# control( /control )へアクセスがあった時
@app.route("/control", methods=["GET", "POST"])
def control():
    path = "/home/ec2-user/comfort_report_system_AWS/input/"
    df_device = pd.read_csv(path + "device_position.csv")
    df_device["serial"] = df_device["serial"].astype(str)

    if request.form.get("button") == "report":
        # 暑いを押した
        if request.form.get("hotorcold") == "TooHot":
            too_hot = True
            hot = False
            comfortable = False
            cool = False
            too_cool = False
            deviceID = request.form.get("hiddendeviceID")
            name = request.form.get("name")
            clo = request.form.get("clo_value")
            x = request.form.get("devicex")
            y = request.form.get("devicey")
            x = round(float(x))
            y = round(float(y))
            img = Image.open(
                "/home/ec2-user/comfort_report_system_AWS/static/images/temperature_distribution_" + deviceID + ".png"
            )
            w, h = img.size

            x_device = x
            y_device = y
            x_device = int(math.ceil(x_device / zip))
            y_device = int(math.ceil(y_device / zip))
            Contour_Diagram_np = np.zeros((76, 64), np.float64)
            df576 = pd.read_csv("/home/ec2-user/comfort_report_system_AWS/input/ondotori_data_df576.csv")
            df503 = pd.read_csv("/home/ec2-user/comfort_report_system_AWS/input/ondotori_data_df503.csv")
            df576["time"] = pd.to_datetime(df576["time"])
            df503["time"] = pd.to_datetime(df503["time"])
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
            Z = bilinear2(Contour_Diagram_np)
            temp = format(Z[y_device][x_device], ".1f")

            time = datetime.datetime.now()
            time = time.strftime("%Y-%m-%dT%H:%M:%S")
            time += "Z"
            temperature_questionnaire = {
                "answeredAt": time,
                "deviceId": deviceID,
                "personId": name,
                "answer": {
                    "clothingAmout": clo,
                    "tooCool": too_cool,
                    "cool": cool,
                    "comfortable": comfortable,
                    "hot": hot,
                    "tooHot": too_hot,
                },
            }

            # ノードレッドでの制御実行
            questionnairess_data = temperature_questionnaire
            questionnairess_headers = {"Content-Type": "application/json"}
            print("http://172.31.25.131:1880/sendQuestionnaires")
            url = "http://172.31.25.131:1880/sendQuestionnaires"
            res = requests.post(
                url, json=questionnairess_data, headers=questionnairess_headers
            )
            # res = res.json()
            # print(res)
            # print(type(res))
            # alert = res["message"]
            # print(alert)
            # if not alert:
            #     pass
            # else:
            #     # tk.Tk().withdraw()
            #     messagebox.showinfo("エラー", alert)
            too_hot = False

        # やや暑いを押した
        elif request.form.get("hotorcold") == "Hot":
            too_hot = False
            hot = True
            comfortable = False
            cool = False
            too_cool = False
            deviceID = request.form.get("hiddendeviceID")
            name = request.form.get("name")
            clo = request.form.get("clo_value")
            x = request.form.get("devicex")
            y = request.form.get("devicey")
            x = round(float(x))
            y = round(float(y))
            img = Image.open(
                "/home/ec2-user/comfort_report_system_AWS/static/images/temperature_distribution_" + deviceID + ".png"
            )
            w, h = img.size

            x_device = x
            y_device = y
            x_device = int(math.ceil(x_device / zip))
            y_device = int(math.ceil(y_device / zip))
            Contour_Diagram_np = np.zeros((76, 64), np.float64)
            df576 = pd.read_csv("/home/ec2-user/comfort_report_system_AWS/input/ondotori_data_df576.csv")
            df503 = pd.read_csv("/home/ec2-user/comfort_report_system_AWS/input/ondotori_data_df503.csv")
            df576["time"] = pd.to_datetime(df576["time"])
            df503["time"] = pd.to_datetime(df503["time"])
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
            Z = bilinear2(Contour_Diagram_np)
            temp = format(Z[y_device][x_device], ".1f")

            time = datetime.datetime.now()
            time = time.strftime("%Y-%m-%dT%H:%M:%S")
            time += "Z"
            temperature_questionnaire = {
                "answeredAt": time,
                "deviceId": deviceID,
                "personId": name,
                "answer": {
                    "clothingAmout": clo,
                    "tooCool": too_cool,
                    "cool": cool,
                    "comfortable": comfortable,
                    "hot": hot,
                    "tooHot": too_hot,
                },
            }
            # ノードレッドでの制御実行
            questionnairess_data = temperature_questionnaire
            questionnairess_headers = {"Content-Type": "application/json"}
            print("http://172.31.25.131:1880/sendQuestionnaires")
            url = "http://172.31.25.131:1880/sendQuestionnaires"
            res = requests.post(
                url, json=questionnairess_data, headers=questionnairess_headers
            )
            # res = res.json()
            # print(res)
            # print(type(res))
            # alert = res["message"]
            # print(alert)
            # if not alert:
            #     pass
            # else:
            #     # tk.Tk().withdraw()
            #     messagebox.showinfo("エラー", alert)
            hot = False
        
        # 快適を押した
        elif request.form.get("hotorcold") == "Comfortable":
                too_hot = False
                hot = False
                comfortable = True
                cool = False
                too_cool = False
                deviceID = request.form.get("hiddendeviceID")
                name = request.form.get("name")
                clo = request.form.get("clo_value")
                x = request.form.get("devicex")
                y = request.form.get("devicey")
                x = round(float(x))
                y = round(float(y))
                img = Image.open(
                    "/home/ec2-user/comfort_report_system_AWS/static/images/temperature_distribution_" + deviceID + ".png"
                )
                w, h = img.size

                x_device = x
                y_device = y
                x_device = int(math.ceil(x_device / zip))
                y_device = int(math.ceil(y_device / zip))
                Contour_Diagram_np = np.zeros((76, 64), np.float64)
                df576 = pd.read_csv("/home/ec2-user/comfort_report_system_AWS/input/ondotori_data_df576.csv")
                df503 = pd.read_csv("/home/ec2-user/comfort_report_system_AWS/input/ondotori_data_df503.csv")
                df576["time"] = pd.to_datetime(df576["time"])
                df503["time"] = pd.to_datetime(df503["time"])
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
                Z = bilinear2(Contour_Diagram_np)
                temp = format(Z[y_device][x_device], ".1f")

                time = datetime.datetime.now()
                time = time.strftime("%Y-%m-%dT%H:%M:%S")
                time += "Z"
                temperature_questionnaire = {
                    "answeredAt": time,
                    "deviceId": deviceID,
                    "personId": name,
                    "answer": {
                        "clothingAmout": clo,
                        "tooCool": too_cool,
                        "cool": cool,
                        "comfortable": comfortable,
                        "hot": hot,
                        "tooHot": too_hot,
                    },
                }

                # ノードレッドでの制御実行
                questionnairess_data = temperature_questionnaire
                questionnairess_headers = {"Content-Type": "application/json"}
                print("http://172.31.25.131:1880/sendQuestionnaires")
                url = "http://172.31.25.131:1880/sendQuestionnaires"
                res = requests.post(
                    url, json=questionnairess_data, headers=questionnairess_headers
                )
                # res = res.json()
                # print(res)
                # print(type(res))
                # alert = res["message"]
                # print(alert)
                # if not alert:
                #     pass
                # else:
                #     # tk.Tk().withdraw()
                #     messagebox.showinfo("エラー", alert)
                comfortable = False

        # やや寒いを押した
        elif request.form.get("hotorcold") == "Cold":
                too_hot = False
                hot = False
                comfortable = False
                cool = True
                too_cool = False
                deviceID = request.form.get("hiddendeviceID")
                name = request.form.get("name")
                clo = request.form.get("clo_value")
                x = request.form.get("devicex")
                y = request.form.get("devicey")
                x = round(float(x))
                y = round(float(y))
                img = Image.open(
                    "/home/ec2-user/comfort_report_system_AWS/static/images/temperature_distribution_" + deviceID + ".png"
                )
                w, h = img.size

                x_device = x
                y_device = y
                x_device = int(math.ceil(x_device / zip))
                y_device = int(math.ceil(y_device / zip))
                Contour_Diagram_np = np.zeros((76, 64), np.float64)
                df576 = pd.read_csv("/home/ec2-user/comfort_report_system_AWS/input/ondotori_data_df576.csv")
                df503 = pd.read_csv("/home/ec2-user/comfort_report_system_AWS/input/ondotori_data_df503.csv")
                df576["time"] = pd.to_datetime(df576["time"])
                df503["time"] = pd.to_datetime(df503["time"])
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
                Z = bilinear2(Contour_Diagram_np)
                temp = format(Z[y_device][x_device], ".1f")

                time = datetime.datetime.now()
                time = time.strftime("%Y-%m-%dT%H:%M:%S")
                time += "Z"
                temperature_questionnaire = {
                    "answeredAt": time,
                    "deviceId": deviceID,
                    "personId": name,
                    "answer": {
                        "clothingAmout": clo,
                        "tooCool": too_cool,
                        "cool": cool,
                        "comfortable": comfortable,
                        "hot": hot,
                        "tooHot": too_hot,
                    },
                }
                # ノードレッドでの制御実行
                questionnairess_data = temperature_questionnaire
                questionnairess_headers = {"Content-Type": "application/json"}
                print("http://172.31.25.131:1880/sendQuestionnaires")
                url = "http://172.31.25.131:1880/sendQuestionnaires"
                res = requests.post(
                    url, json=questionnairess_data, headers=questionnairess_headers
                )
                # res = res.json()
                # print(res)
                # print(type(res))
                # alert = res["message"]
                # print(alert)
                # if not alert:
                #     pass
                # else:
                #     # tk.Tk().withdraw()
                #     messagebox.showinfo("エラー", alert)
                cool = False
        
        # 寒いを押した
        elif request.form.get("hotorcold") == "TooCold":
            too_hot = False
            hot = False
            comfortable = False
            cool = False
            too_cool = True
            deviceID = request.form.get("hiddendeviceID")
            name = request.form.get("name")
            clo = request.form.get("clo_value")
            x = request.form.get("devicex")
            y = request.form.get("devicey")
            x = round(float(x))
            y = round(float(y))
            img = Image.open(
                "/home/ec2-user/comfort_report_system_AWS/static/images/temperature_distribution_" + deviceID + ".png"
            )
            w, h = img.size

            x_device = x
            y_device = y
            x_device = int(math.ceil(x_device / zip))
            y_device = int(math.ceil(y_device / zip))
            Contour_Diagram_np = np.zeros((76, 64), np.float64)
            df576 = pd.read_csv("/home/ec2-user/comfort_report_system_AWS/input/ondotori_data_df576.csv")
            df503 = pd.read_csv("/home/ec2-user/comfort_report_system_AWS/input/ondotori_data_df503.csv")
            df576["time"] = pd.to_datetime(df576["time"])
            df503["time"] = pd.to_datetime(df503["time"])
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
            Z = bilinear2(Contour_Diagram_np)
            temp = format(Z[y_device][x_device], ".1f") 

            time = datetime.datetime.now()
            time = time.strftime("%Y-%m-%dT%H:%M:%S")
            time += "Z"
            temperature_questionnaire = {
                "answeredAt": time,
                "deviceId": deviceID,
                "personId": name,
                "answer": {
                    "clothingAmout": clo,
                    "tooCool": too_cool,
                    "cool": cool,
                    "comfortable": comfortable,
                    "hot": hot,
                    "tooHot": too_hot,
                },
            }
            # ノードレッドでの制御実行
            questionnairess_data = temperature_questionnaire
            questionnairess_headers = {"Content-Type": "application/json"}
            print("http://172.31.25.131:1880/sendQuestionnaires")
            url = "http://172.31.25.131:1880/sendQuestionnaires"
            res = requests.post(
                url, json=questionnairess_data, headers=questionnairess_headers
            )
            # res = res.json()
            # print(res)
            # print(type(res))
            # alert = res["message"]
            # print(alert)
            # if not alert:
            #     pass
            # else:
            #     # tk.Tk().withdraw()
            #     messagebox.showinfo("エラー", alert)
            too_cool = False

        return render_template(
            "show_dist_img.html",
            deviceID=deviceID,
            name=name,
            clo=clo,
            width=w,
            height=h,
            x=x,
            y=y,
            temp=temp,
        )

    elif request.form.get("button") == "back":
        deviceID = request.form.get("hiddendeviceID")
        name = request.form.get("name")
        clo = request.form.get("clo_value")
        x = request.form.get("devicex")
        y = request.form.get("devicey")
        x = round(float(x))
        y = round(float(y))
        img = Image.open(
                "/home/ec2-user/comfort_report_system_AWS/static/images/temperature_distribution_" + deviceID + ".png"
            )
        w, h = img.size
        x_device = x
        y_device = y
        x_device = int(math.ceil(x_device / zip))
        y_device = int(math.ceil(y_device / zip))
        Contour_Diagram_np = np.zeros((76, 64), np.float64)
        df576 = pd.read_csv("/home/ec2-user/comfort_report_system_AWS/input/ondotori_data_df576.csv")
        df503 = pd.read_csv("/home/ec2-user/comfort_report_system_AWS/input/ondotori_data_df503.csv")
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
        Contour_Diagram_np = bilinear2(Contour_Diagram_np)
        temp = format(Contour_Diagram_np[y_device][x_device], ".1f")
        return render_template(
            "show_dist_img.html",
            deviceID=deviceID,
            name=name,
            clo=clo,
            width=w,
            height=h,
            x=x,
            y=y,
            temp=temp,
        )

    else:
        deviceID = request.form.get("deviceID")
        name1 = request.form.get("name")
        x = df_device[(df_device["serial"] == deviceID)]["x"].iloc[0]
        y = df_device[(df_device["serial"] == deviceID)]["y"].iloc[0]
        img = Image.open(
                "/home/ec2-user/comfort_report_system_AWS/static/images/temperature_distribution_" + deviceID + ".png"
            )
        w, h = img.size

        x_device = x
        y_device = y
        x_device = int(math.ceil(x_device / zip))
        y_device = int(math.ceil(y_device / zip))
        Contour_Diagram_np = np.zeros((76, 64), np.float64)
        df576 = pd.read_csv("/home/ec2-user/comfort_report_system_AWS/input/ondotori_data_df576.csv")
        df503 = pd.read_csv("/home/ec2-user/comfort_report_system_AWS/input/ondotori_data_df503.csv")
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
        Contour_Diagram_np = bilinear2(Contour_Diagram_np)
        temp = format(Contour_Diagram_np[y_device][x_device], ".1f")
        return render_template(
            "show_dist_img.html",
            deviceID=deviceID,
            name=name1,
            clo=0,
            width=w,
            height=h,
            x=x,
            y=y,
            temp=temp,
        )


# report( /report )へアクセスがあった時
@app.route("/report", methods=["GET", "POST"])
def report():
    # 暑いを押した
    if request.form.get("TooHot"):
        deviceID = request.form.get("hiddendeviceID")
        x = request.form.get("devicex")
        y = request.form.get("devicey")
        TooHot = request.form.get("TooHot")
        name = request.form.get("name")
        name1 = "自分のユーザー名を選択してください"
        if name == "a":
            name1 = "ダイキン1郎"
        elif name == "b":
            name1 = "ダイキン2郎"
        elif name == "c":
            name1 = "ダイキン3郎"
        elif name == "d":
            name1 = "ダイキン4郎"
        elif name == "e":
            name1 = "ダイキン5郎"
        elif name == "f":
            name1 = "ダイキン6郎"
        clo = request.form.get("clo_value")
        clo_list = ["", "", "", "", "", "", "", "", "", "", ""]
        clo_list[int(clo)] = "checked"
        return render_template(
            "show_dist_img2.html",
            deviceID=deviceID,
            name=name,
            name1=name1,
            clo=clo,
            hotorcold=TooHot,
            checked1=clo_list[1],
            checked2=clo_list[2],
            checked3=clo_list[3],
            checked4=clo_list[4],
            checked5=clo_list[5],
            checked6=clo_list[6],
            checked7=clo_list[7],
            checked8=clo_list[8],
            checked9=clo_list[9],
            checked10=clo_list[10],
            x=x,
            y=y,
        )
    
    # やや暑いを押した
    elif request.form.get("Hot"):
        deviceID = request.form.get("hiddendeviceID")
        x = request.form.get("devicex")
        y = request.form.get("devicey")
        Hot = request.form.get("Hot")
        name = request.form.get("name")
        name1 = "自分のユーザー名を選択してください"
        if name == "a":
            name1 = "ダイキン1郎"
        elif name == "b":
            name1 = "ダイキン2郎"
        elif name == "c":
            name1 = "ダイキン3郎"
        elif name == "d":
            name1 = "ダイキン4郎"
        elif name == "e":
            name1 = "ダイキン5郎"
        elif name == "f":
            name1 = "ダイキン6郎"
        clo = request.form.get("clo_value")
        clo_list = ["", "", "", "", "", "", "", "", "", "", ""]
        clo_list[int(clo)] = "checked"
        return render_template(
            "show_dist_img2.html",
            deviceID=deviceID,
            name=name,
            name1=name1,
            clo=clo,
            hotorcold=Hot,
            checked1=clo_list[1],
            checked2=clo_list[2],
            checked3=clo_list[3],
            checked4=clo_list[4],
            checked5=clo_list[5],
            checked6=clo_list[6],
            checked7=clo_list[7],
            checked8=clo_list[8],
            checked9=clo_list[9],
            checked10=clo_list[10],
            x=x,
            y=y,
        )
    
    #快適を押した 
    elif request.form.get("Comfortable"):
        deviceID = request.form.get("hiddendeviceID")
        x = request.form.get("devicex")
        y = request.form.get("devicey")
        Comfortable = request.form.get("Comfortable")
        name = request.form.get("name")
        name1 = "自分のユーザー名を選択してください"
        if name == "a":
            name1 = "ダイキン1郎"
        elif name == "b":
            name1 = "ダイキン2郎"
        elif name == "c":
            name1 = "ダイキン3郎"
        elif name == "d":
            name1 = "ダイキン4郎"
        elif name == "e":
            name1 = "ダイキン5郎"
        elif name == "f":
            name1 = "ダイキン6郎"
        clo = request.form.get("clo_value")
        clo_list = ["", "", "", "", "", "", "", "", "", "", ""]
        clo_list[int(clo)] = "checked"
        return render_template(
            "show_dist_img2.html",
            deviceID=deviceID,
            name=name,
            name1=name1,
            clo=clo,
            hotorcold=Comfortable,
            checked1=clo_list[1],
            checked2=clo_list[2],
            checked3=clo_list[3],
            checked4=clo_list[4],
            checked5=clo_list[5],
            checked6=clo_list[6],
            checked7=clo_list[7],
            checked8=clo_list[8],
            checked9=clo_list[9],
            checked10=clo_list[10],
            x=x,
            y=y,
        )

    # やや寒いを押した
    elif request.form.get("Cold"):
        deviceID = request.form.get("hiddendeviceID")
        x = request.form.get("devicex")
        y = request.form.get("devicey")
        Cold = request.form.get("Cold")
        name = request.form.get("name")
        name1 = "自分のユーザー名を選択してください"
        if name == "a":
            name1 = "ダイキン1郎"
        elif name == "b":
            name1 = "ダイキン2郎"
        elif name == "c":
            name1 = "ダイキン3郎"
        elif name == "d":
            name1 = "ダイキン4郎"
        elif name == "e":
            name1 = "ダイキン5郎"
        elif name == "f":
            name1 = "ダイキン6郎"
        clo = request.form.get("clo_value")
        clo_list = ["", "", "", "", "", "", "", "", "", "", ""]
        clo_list[int(clo)] = "checked"
        return render_template(
            "show_dist_img2.html",
            deviceID=deviceID,
            name=name,
            name1=name1,
            clo=clo,
            hotorcold=Cold,
            checked1=clo_list[1],
            checked2=clo_list[2],
            checked3=clo_list[3],
            checked4=clo_list[4],
            checked5=clo_list[5],
            checked6=clo_list[6],
            checked7=clo_list[7],
            checked8=clo_list[8],
            checked9=clo_list[9],
            checked10=clo_list[10],
            x=x,
            y=y,
        )
    
    # 寒いを押した
    elif request.form.get("TooCold"):
        deviceID = request.form.get("hiddendeviceID")
        x = request.form.get("devicex")
        y = request.form.get("devicey")
        TooCold = request.form.get("TooCold")
        name = request.form.get("name")
        name1 = "自分のユーザー名を選択してください"
        if name == "a":
            name1 = "ダイキン1郎"
        elif name == "b":
            name1 = "ダイキン2郎"
        elif name == "c":
            name1 = "ダイキン3郎"
        elif name == "d":
            name1 = "ダイキン4郎"
        elif name == "e":
            name1 = "ダイキン5郎"
        elif name == "f":
            name1 = "ダイキン6郎"
        clo = request.form.get("clo_value")
        clo_list = ["", "", "", "", "", "", "", "", "", "", ""]
        clo_list[int(clo)] = "checked"
        return render_template(
            "show_dist_img2.html",
            deviceID=deviceID,
            name=name,
            name1=name1,
            clo=clo,
            hotorcold=TooCold,
            checked1=clo_list[1],
            checked2=clo_list[2],
            checked3=clo_list[3],
            checked4=clo_list[4],
            checked5=clo_list[5],
            checked6=clo_list[6],
            checked7=clo_list[7],
            checked8=clo_list[8],
            checked9=clo_list[9],
            checked10=clo_list[10],
            x=x,
            y=y,
        )


def bilinear(xx, yy, df):
    """
    #     疎なデータを持つ配列に対しバイリニア補完を行う
    #     :param src: 入力配列
    #     :return: 補完後の配列
    #     参考URL(https://yamaken1343.hatenablog.jp/entry/2018/06/28/192639)
    #"""

    def search_near(x, y, df):
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

        try:
            # スライスされるため, indexに入る値はsrcのインデックスと互換性がないことに注意する
            index_x, index_y = np.array(df.iloc[:, 1]), np.array(df.iloc[:, 2])
            array_top4 = min_pear(index_x, index_y, x, y)
            return array_top4

        # データが見つからなくても止まらないようにする
        except:
            return None

    point = [xx, yy]  # クリックした位置 x,yが逆になっていない
    n4p = search_near(point[0], point[1], df)
    return n4p


def translate_to_equipmentID(d):
    c = d
    if d == "MAC-2-1-2a A":
        c = "a1fe7aa0-7a4a-11ec-b3c1-aa6ab95de3cd"
    elif d == "MAC-2-1-2a B":
        c = "a1f586d4-7a4a-11ec-b3c1-aa6ab95de3cd"
    elif d == "MAC-2-1-2a C":
        c = "a1f2052c-7a4a-11ec-b3c1-aa6ab95de3cd"
    elif d == "MAC-2-1-2a D":
        c = "02216ce0-355c-11ed-b9a3-3a77aff4ad92"
    elif d == "MAC-2-1-2a E":
        c = "02226762-355c-11ed-b9a3-3a77aff4ad92"
    elif d == "MAC-2-1-2a F":
        c = "022218de-355c-11ed-b9a3-3a77aff4ad92"
    elif d == "MAC-2-1-2a G":
        c = "0221c5c8-355c-11ed-b9a3-3a77aff4ad92"
    elif d == "MAC-2-1-2a H":
        c = "02211736-355c-11ed-b9a3-3a77aff4ad92"
    return c


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


def remake_dic(response_):
    dic = {}
    dic2 = {}
    for d in response_["devices"]:
        # センサ名とセンサ値のリストを取得
        dic.update({d["serial"]: d["channel"]})
        dic2.update({d["serial"]: datetime.datetime.fromtimestamp(int(d["unixtime"]))})
    return dic, dic2


def bilinear2(src):
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
                    / (-2.0 * 0.5 * 2)
                ),
                math.exp(
                    (np.linalg.norm((n4p[1] - idx) * (30 / 756))) ** 2
                    / (-2.0 * 0.5**2)
                ),
                math.exp(
                    (np.linalg.norm((n4p[2] - idx) * (30 / 756))) ** 2
                    / (-2.0 * 0.5**2)
                ),
                math.exp(
                    (np.linalg.norm((n4p[3] - idx) * (30 / 756))) ** 2
                    / (-2.0 * 0.5**2)
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


def operation_current_state(equipmentId, propertyPath, value):
    url = " https://3w1p12712a.execute-api.ap-northeast-1.amazonaws.com/prod/operation_current_equipment_states"
    # url = "https://gpf.dk-mejirodai.com/"

    param = json.dumps(
        {
            "equipmentId": equipmentId,
            "request_body": {
                "operations": [
                    {
                        "propertyPath": propertyPath,
                        "value": value,
                    }
                ],
            },
        },
    )
    print(param)


def operation_current_state2(equipmentId, propertyPath, value, proxies=True):
    url = " https://3w1p12712a.execute-api.ap-northeast-1.amazonaws.com/prod/operation_current_equipment_states"
    # url = "https://gpf.dk-mejirodai.com/"

    param = json.dumps(
        {
            "equipmentId": equipmentId,
            "request_body": {
                "operations": [
                    {
                        "propertyPath": propertyPath,
                        "value": value,
                    }
                ],
            },
        },
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


def translate(data2):
    data3 = data2
    if data2["OperatingMode_now"] == 0:
        data3["OperatingMode_now"] = "送風"
    elif data2["OperatingMode_now"] == 1:
        data3["OperatingMode_now"] = "暖房"
    elif data2["OperatingMode_now"] == 2:
        data3["OperatingMode_now"] = "冷房"
    elif data2["OperatingMode_now"] == 3:
        data3["OperatingMode_now"] = "自動"
    elif data2["OperatingMode_now"] == 4:
        data3["OperatingMode_now"] = "換気"
    elif data2["OperatingMode_now"] == 5:
        data3["OperatingMode_now"] = "dry"
    elif data2["OperatingMode_now"] == 6:
        data3["OperatingMode_now"] = "dependent"
    elif data2["OperatingMode_now"] == 8:
        data3["OperatingMode_now"] = "humidification"
    elif data2["OperatingMode_now"] == 9:
        data3["OperatingMode_now"] = "dry cool"

    if data2["CoolAirdirectionUpDown_now"] == 0:
        data3["CoolAirdirectionUpDown_now"] = "停止"
    elif data2["CoolAirdirectionUpDown_now"] == 1:
        data3["CoolAirdirectionUpDown_now"] = "P0"
    elif data2["CoolAirdirectionUpDown_now"] == 2:
        data3["CoolAirdirectionUpDown_now"] = "P1"
    elif data2["CoolAirdirectionUpDown_now"] == 3:
        data3["CoolAirdirectionUpDown_now"] = "P2"
    elif data2["CoolAirdirectionUpDown_now"] == 4:
        data3["CoolAirdirectionUpDown_now"] = "P3"
    elif data2["CoolAirdirectionUpDown_now"] == 5:
        data3["CoolAirdirectionUpDown_now"] = "P4"
    elif data2["CoolAirdirectionUpDown_now"] == 6:
        data3["CoolAirdirectionUpDown_now"] = "P5"
    elif data2["CoolAirdirectionUpDown_now"] == 7:
        data3["CoolAirdirectionUpDown_now"] = "P6"
    elif data2["CoolAirdirectionUpDown_now"] == 8:
        data3["CoolAirdirectionUpDown_now"] = "P7"
    elif data2["CoolAirdirectionUpDown_now"] == 9:
        data3["CoolAirdirectionUpDown_now"] = "P8"
    elif data2["CoolAirdirectionUpDown_now"] == 10:
        data3["CoolAirdirectionUpDown_now"] = "P9"
    elif data2["CoolAirdirectionUpDown_now"] == 11:
        data3["CoolAirdirectionUpDown_now"] = "P10"
    elif data2["CoolAirdirectionUpDown_now"] == 12:
        data3["CoolAirdirectionUpDown_now"] = "P11"
    elif data2["CoolAirdirectionUpDown_now"] == 13:
        data3["CoolAirdirectionUpDown_now"] = "P12"
    elif data2["CoolAirdirectionUpDown_now"] == 14:
        data3["CoolAirdirectionUpDown_now"] = "P13"
    elif data2["CoolAirdirectionUpDown_now"] == 15:
        data3["CoolAirdirectionUpDown_now"] = "スイング"
    elif data2["CoolAirdirectionUpDown_now"] == 16:
        data3["CoolAirdirectionUpDown_now"] = "自動"
    elif data2["CoolAirdirectionUpDown_now"] == 17:
        data3["CoolAirdirectionUpDown_now"] = "Reverse"
    elif data2["CoolAirdirectionUpDown_now"] == 18:
        data3["CoolAirdirectionUpDown_now"] = "Insensitive air flow"
    elif data2["CoolAirdirectionUpDown_now"] == 19:
        data3["CoolAirdirectionUpDown_now"] = "Nature wind"
    elif data2["CoolAirdirectionUpDown_now"] == 20:
        data3["CoolAirdirectionUpDown_now"] = "Circulating airflow"
    elif data2["CoolAirdirectionUpDown_now"] == 21:
        data3["CoolAirdirectionUpDown_now"] = "Indefine"
    elif data2["CoolAirdirectionUpDown_now"] == 22:
        data3["CoolAirdirectionUpDown_now"] = "Wide"
    elif data2["CoolAirdirectionUpDown_now"] == 23:
        data3["CoolAirdirectionUpDown_now"] = "Wind nice"
    elif data2["CoolAirdirectionUpDown_now"] == 24:
        data3["CoolAirdirectionUpDown_now"] = "Pclose"
    elif data2["CoolAirdirectionUpDown_now"] == 25:
        data3["CoolAirdirectionUpDown_now"] = "Floor heating airflow"

    if data2["CoolFanSpeed_now"] == 0:
        data3["CoolFanSpeed_now"] = "停止"
    elif data2["CoolFanSpeed_now"] == 1:
        data3["CoolFanSpeed_now"] = "LLL"
    elif data2["CoolFanSpeed_now"] == 2:
        data3["CoolFanSpeed_now"] = "LL"
    elif data2["CoolFanSpeed_now"] == 3:
        data3["CoolFanSpeed_now"] = "弱"
    elif data2["CoolFanSpeed_now"] == 4:
        data3["CoolFanSpeed_now"] = "LM"
    elif data2["CoolFanSpeed_now"] == 5:
        data3["CoolFanSpeed_now"] = "強"
    elif data2["CoolFanSpeed_now"] == 6:
        data3["CoolFanSpeed_now"] = "MH"
    elif data2["CoolFanSpeed_now"] == 7:
        data3["CoolFanSpeed_now"] = "急"
    elif data2["CoolFanSpeed_now"] == 8:
        data3["CoolFanSpeed_now"] = "HH"
    elif data2["CoolFanSpeed_now"] == 9:
        data3["CoolFanSpeed_now"] = "HHH"
    elif data2["CoolFanSpeed_now"] == 10:
        data3["CoolFanSpeed_now"] = "auto"
    elif data2["CoolFanSpeed_now"] == 11:
        data3["CoolFanSpeed_now"] = "quiet"

    if data2["HeatAirDirecionUpDown_now"] == 0:
        data3["HeatAirDirecionUpDown_now"] = "停止"
    elif data2["HeatAirDirecionUpDown_now"] == 1:
        data3["HeatAirDirecionUpDown_now"] = "P0"
    elif data2["HeatAirDirecionUpDown_now"] == 2:
        data3["HeatAirDirecionUpDown_now"] = "P1"
    elif data2["HeatAirDirecionUpDown_now"] == 3:
        data3["HeatAirDirecionUpDown_now"] = "P2"
    elif data2["HeatAirDirecionUpDown_now"] == 4:
        data3["HeatAirDirecionUpDown_now"] = "P3"
    elif data2["HeatAirDirecionUpDown_now"] == 5:
        data3["HeatAirDirecionUpDown_now"] = "P4"
    elif data2["HeatAirDirecionUpDown_now"] == 6:
        data3["HeatAirDirecionUpDown_now"] = "P5"
    elif data2["HeatAirDirecionUpDown_now"] == 7:
        data3["HeatAirDirecionUpDown_now"] = "P6"
    elif data2["HeatAirDirecionUpDown_now"] == 8:
        data3["HeatAirDirecionUpDown_now"] = "P7"
    elif data2["HeatAirDirecionUpDown_now"] == 9:
        data3["HeatAirDirecionUpDown_now"] = "P8"
    elif data2["HeatAirDirecionUpDown_now"] == 10:
        data3["HeatAirDirecionUpDown_now"] = "P9"
    elif data2["HeatAirDirecionUpDown_now"] == 11:
        data3["HeatAirDirecionUpDown_now"] = "P10"
    elif data2["HeatAirDirecionUpDown_now"] == 12:
        data3["HeatAirDirecionUpDown_now"] = "P11"
    elif data2["HeatAirDirecionUpDown_now"] == 13:
        data3["HeatAirDirecionUpDown_now"] = "P12"
    elif data2["HeatAirDirecionUpDown_now"] == 14:
        data3["HeatAirDirecionUpDown_now"] = "P13"
    elif data2["HeatAirDirecionUpDown_now"] == 15:
        data3["HeatAirDirecionUpDown_now"] = "スイング"
    elif data2["HeatAirDirecionUpDown_now"] == 16:
        data3["HeatAirDirecionUpDown_now"] = "自動"
    elif data2["HeatAirDirecionUpDown_now"] == 17:
        data3["HeatAirDirecionUpDown_now"] = "Reverse"
    elif data2["HeatAirDirecionUpDown_now"] == 18:
        data3["HeatAirDirecionUpDown_now"] = "Insensitive air flow"
    elif data2["HeatAirDirecionUpDown_now"] == 19:
        data3["HeatAirDirecionUpDown_now"] = "Nature wind"
    elif data2["HeatAirDirecionUpDown_now"] == 20:
        data3["HeatAirDirecionUpDown_now"] = "Circulating airflow"
    elif data2["HeatAirDirecionUpDown_now"] == 21:
        data3["HeatAirDirecionUpDown_now"] = "Indefine"
    elif data2["HeatAirDirecionUpDown_now"] == 22:
        data3["HeatAirDirecionUpDown_now"] = "Wide"
    elif data2["HeatAirDirecionUpDown_now"] == 23:
        data3["HeatAirDirecionUpDown_now"] = "Wind nice"
    elif data2["HeatAirDirecionUpDown_now"] == 24:
        data3["HeatAirDirecionUpDown_now"] = "Pclose"
    elif data2["HeatAirDirecionUpDown_now"] == 25:
        data3["HeatAirDirecionUpDown_now"] = "Floor heating airflow"

    if data2["HeatFanSpeed_now"] == 0:
        data3["HeatFanSpeed_now"] = "停止"
    elif data2["HeatFanSpeed_now"] == 1:
        data3["HeatFanSpeed_now"] = "LLL"
    elif data2["HeatFanSpeed_now"] == 2:
        data3["HeatFanSpeed_now"] = "LL"
    elif data2["HeatFanSpeed_now"] == 3:
        data3["HeatFanSpeed_now"] = "弱"
    elif data2["HeatFanSpeed_now"] == 4:
        data3["HeatFanSpeed_now"] = "LM"
    elif data2["HeatFanSpeed_now"] == 5:
        data3["HeatFanSpeed_now"] = "強"
    elif data2["HeatFanSpeed_now"] == 6:
        data3["HeatFanSpeed_now"] = "MH"
    elif data2["HeatFanSpeed_now"] == 7:
        data3["HeatFanSpeed_now"] = "急"
    elif data2["HeatFanSpeed_now"] == 8:
        data3["HeatFanSpeed_now"] = "HH"
    elif data2["HeatFanSpeed_now"] == 9:
        data3["HeatFanSpeed_now"] = "HHH"
    elif data2["HeatFanSpeed_now"] == 10:
        data3["HeatFanSpeed_now"] = "自動"
    elif data2["HeatFanSpeed_now"] == 11:
        data3["HeatFanSpeed_now"] = "quiet"

    if data2["OnOff_now"] == 0:
        data3["OnOff_now"] = "停止"
    elif data2["OnOff_now"] == 1:
        data3["OnOff_now"] = "運転"

    return data3


def translate_inverse_OperatingMode(a):
    b = a
    if a == "送風":
        b = 0
    elif a == "暖房":
        b = 1
    elif a == "冷房":
        b = 2
    elif a == "自動":
        b = 3
    elif a == "換気":
        b = 4
    return b


def translate_inverse_CoolAirdirectionUpDown(c):
    d = c
    if c == "停止":
        d = 0
    elif c == "P0":
        d = 1
    elif c == "P1":
        d = 2
    elif c == "P2":
        d = 3
    elif c == "P3":
        d = 4
    elif c == "P4":
        d = 5
    elif c == "スイング":
        d = 15
    elif c == "自動":
        d = 16
    return d


def translate_inverse_CoolFanSpeed(e):
    f = e
    if e == "停止":
        f = 0
    elif e == "弱":
        f = 3
    elif e == "強":
        f = 5
    elif e == "急":
        f = 7
    elif e == "自動":
        f = 10
    return f


def translate_inverse_HeatAirdirectionUpDown(n):
    m = n
    if n == "停止":
        m = 0
    elif n == "P0":
        m = 1
    elif n == "P1":
        m = 2
    elif n == "P2":
        m = 3
    elif n == "P3":
        m = 4
    elif n == "P4":
        m = 5
    elif n == "スイング":
        m = 15
    elif n == "自動":
        m = 16
    return m


def translate_inverse_HeatFanSpeed(p):
    q = p
    if p == "停止":
        q = 0
    elif p == "弱":
        q = 3
    elif p == "強":
        q = 5
    elif p == "急":
        q = 7
    elif p == "自動":
        q = 10
    return q


def translate_inverse_OnOff(j):
    h = j
    if j == "停止":
        h = 0
    elif j == "運転":
        h = 1
    return h

if __name__ == "__main__":
    # app.run()
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        # ssl_context=("server.crt", "server.key"),
    )
    # db.create_all()
