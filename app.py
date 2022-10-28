from datetime import datetime
import pandas as pd

MINUTES_IN_A_YEAR = 525600  # number of minutes in a year

pd.set_option("display.max_columns", 12)
pd.set_option("display.width", 1000)


def print_group(grouped: pd.DataFrame.groupby):
    for i, x in grouped:
        print(x)


def process(df):
    df[["Symbol", "Settlement", "Strike", "C/P"]] = df["option_symbol"].str.split(
        "-", expand=True
    )
    df.drop("option_symbol", inplace=True, axis=1)
    df = df[["Symbol", "Settlement", "Strike", "C/P", "ask1", "bid1", "mark_price"]]
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


def cal_f_value(df: pd.DataFrame) -> pd.DataFrame:
    df["strike_temp"] = df["Strike"]
    grouped = df.groupby(["Symbol", "Settlement", "Strike"], sort=False)
    df["F"] = (
        grouped["mark_price"].diff().abs().fillna(method="bfill").add(df["Strike"])
    )

    return df


def select_k0(df: pd.DataFrame) -> pd.DataFrame:
    df["K0"] = False
    df.loc[df[df["Strike"] < df["F"]].groupby(["Symbol", "Settlement", "C/P"]).head(1).index, "K0"] = True
    return df


# remove illiquid strikes
def select_strikes(df: pd.DataFrame) -> pd.DataFrame:
    df["min_b/a"] = df.apply(lambda x: min(x.bid1, x.ask1), axis=1)
    df["min_b/a_diff"] = df.groupby(["Symbol", "Settlement", "C/P"], sort=False)[
        ["min_b/a"]
    ].diff()

    df_call = df[df["C/P"] == "C"]
    df_put = df[df["C/P"] == "P"]

    df_put = df_put[
        df_put.groupby(["Symbol", "Settlement"], sort=False)["min_b/a_diff"].transform(
            lambda x: x.ne(0).cumprod().astype(bool)
        )
    ]
    df_call = df_call.sort_values(
        by=["Symbol", "Settlement", "Strike"], ascending=[True, True, False]
    )
    df_call = df_call[
        df_call.groupby(["Symbol", "Settlement"], sort=False)["min_b/a_diff"].transform(
            lambda x: x.ne(0).cumprod().astype(bool)
        )
    ]

    df = pd.concat([df_call, df_put], axis=0)
    df = df[df["min_b/a"] > 0]
    df.drop(["min_b/a", "min_b/a_diff"], inplace=True, axis=1)
    df.sort_values(["Symbol", "Settlement", "Strike"], ascending=True, inplace=True)
    return df


# TODO
def cal_midprice(df: pd.DataFrame) -> pd.DataFrame:

    df["MidPrice"] = df["bid1"].add(df["ask1"]).div(2)

    items = df.loc[df["K0"]].groupby(["Symbol", "Settlement", "Strike"])

    df.loc[items.index, "MidPrice"] = items["mark_price"].sum().div(2)

    return df


def main():
    date1 = datetime.strptime("20221005", "%Y%m%d")
    file_path = "./data/sample/01.csv"

    df = pd.read_csv(file_path)
    # print("Raw data :\n", df)

    df = process(df)
    # print("Processed data :\n", df)

    df = filter_data(df, date1)
    # print("Selected data by the given date :\n", df)

    df = cal_f_value(df)
    # print("Calculate F value :\n", df)

    df = select_k0(df)

    # df = select_strikes(df)
    # print("Select Strike by removing low liquidity strikes :\n", df)

    # df = cal_midprice(df)
    # print("Calculated mid price of all strikes :\n", df)


if __name__ == "__main__":
    main()
