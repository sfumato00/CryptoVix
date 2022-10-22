from datetime import datetime
import pandas as pd

MINUTES_IN_A_YEAR = 525600  # number of minutes in a year


def process(df):
    # df = df.sort_values(by="option_symbol", ascending=True)
    df[["Symbol", "Settlement", "Strike", "Call/Put"]] = df["option_symbol"].str.split(
        "-", expand=True
    )

    df["Settlement"] = "20" + df["Settlement"].astype(str)
    df["Settlement"] = pd.to_datetime(df["Settlement"], format="%Y%m%d")
    df["Strike"] = df["Strike"].astype(float)
    df["strike"] = df["Strike"]
    # df = df.sort_values(by="strike", ascending=True)
    return df


def filter_data(df: pd.DataFrame, curr_date=datetime.now()):
    ret = df.copy()

    # T window
    ret = ret.loc[
        ((ret["Settlement"] - curr_date).dt.days >= 23)
        & ((ret["Settlement"] - curr_date).dt.days <= 37)
    ]

    # 0 bid/ask
    # ret = ret.loc[(ret["bid1"] > 0) & (ret["ask1"] > 0)]

    # remove all
    return ret.sort_values(["strike"], ascending=True)


def cal_t_value():
    pass


def cal_f_value(groups) -> float:

    # print("Call :\n", groups.first())
    # print("Put :\n", groups.nth(1))

    f_values = (
        groups.first()["strike"]
        + groups.first()["mark_price"]
        - groups.nth(1)["mark_price"]
    )
    return f_values


def main():

    date1 = datetime.strptime("20221005", "%Y%m%d")
    file_path = "./data/sample/01.csv"

    df = pd.read_csv(file_path)
    # print("Raw data :\n", df)

    df = process(df)
    # print("Processed data :\n", df)

    t_df = filter_data(df, date1)
    # print("Selected data by the given date :\n", t_df)

    groups = t_df.groupby(["Symbol", "Settlement", "Strike"], group_keys=False)
    print("Group :\n")
    for key, item in groups:
        print(item)

    f_values = cal_f_value(groups)
    print("F values : \n", f_values)


if __name__ == "__main__":
    main()
