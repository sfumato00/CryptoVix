from datetime import datetime
import pandas as pd

MINUTES_IN_A_YEAR = 525600  # number of minutes in a year

pd.set_option('display.max_columns', 12)
pd.set_option('display.width', 1000)


def process(df):
    df[["Symbol", "Settlement", "Strike", "C/P"]] = df["option_symbol"].str.split(
        "-", expand=True
    )
    df.drop("option_symbol", inplace=True, axis=1)
    df = df[
        ["Symbol", "Settlement", "Strike", "C/P", "ask1", "bid1", "mark_price"]
    ]
    df["Settlement"] = "20" + df["Settlement"].astype(str)
    df["Settlement"] = pd.to_datetime(df["Settlement"], format="%Y%m%d")
    df["Strike"] = df["Strike"].astype(float)
    return df


def filter_data(df: pd.DataFrame, curr_date=datetime.now()):
    ret = df

    # T window
    ret = ret.loc[
        ((ret["Settlement"] - curr_date).dt.days >= 23)
        & ((ret["Settlement"] - curr_date).dt.days <= 37)
        ]

    return ret.sort_values(["Symbol", "Settlement", "Strike"], ascending=True)


def cal_t_value():
    pass


def cal_f_value(groups) -> float:
    # print("Call :\n", groups.first())
    # print("Put :\n", groups.nth(1))

    f_values = (
            groups.first()["strike"]
            + abs(groups.first()["mark_price"]
                  - groups.nth(1)["mark_price"])
    )
    return f_values


# remove illiquid strikes
def select_strikes(df: pd.DataFrame) -> pd.DataFrame:
    df["min_b/a"] = df.apply(lambda x: min(x.bid1, x.ask1), axis=1)
    df["min_b/a_diff"] = df.groupby(["Symbol", "Settlement", "C/P"], sort=False)[["min_b/a"]].diff()

    df_call = df[df["C/P"] == "C"]
    df_put = df[df["C/P"] == "P"]
    df_put = df_put[df_put.groupby(["Symbol", "Settlement"], sort=False)["min_b/a_diff"].transform(
        lambda x: x.ne(0).cumprod().astype(bool))]
    df_call = df_call.sort_values(by=["Symbol", "Settlement", "Strike"], ascending=[True, True, False])
    df_call = df_call[df_call.groupby(["Symbol", "Settlement"], sort=False)["min_b/a_diff"].transform(
        lambda x: x.ne(0).cumprod().astype(bool))]
    print(df_call)
    df = pd.concat([df_call, df_put], axis=0)

    # remove 0 bid/ask strikes
    df = df[df["min_b/a"] > 0]
    df.sort_values(["Symbol", "Settlement", "Strike"], ascending=True, inplace=True)
    print(df)
    return df


def main():
    date1 = datetime.strptime("20221005", "%Y%m%d")
    file_path = "./data/sample/01.csv"

    df = pd.read_csv(file_path)
    # print("Raw data :\n", df)

    df = process(df)
    # print("Processed data :\n", df)

    df = filter_data(df, date1)
    print("Selected data by the given date :\n", df)

    df = select_strikes(df)
    # print("df :\n", df)

    # groups = df.groupby(["Symbol", "Settlement", "C/P"], sort=False)
    # print("Group :\n")
    # for key, item in groups:
    #     print(item)

    df.drop(["min_b/a", "min_b/a_diff"], inplace=True, axis=1)
    print("df :\n", df)


if __name__ == "__main__":
    main()
