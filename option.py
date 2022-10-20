from abc import abstractmethod
from datetime import datetime

import pandas as pd


class AbstractDataFrame(object):
    def __init__(self, df):
        self.df = df.copy()

    @abstractmethod
    def process(self):
        pass

    @abstractmethod
    def get_t_data(self, date):
        pass
    



class SampleData01(AbstractDataFrame):

    def process(self):
        df = self.df
        df[["symbol", "date", "strike", "Call/Put"]] = df["option_symbol"].str.split(
            "-", expand=True
        )

        df["date"] = '20' + df['date'].astype(str)
        df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")

    def get_t_data(self, date):

        # def is_t_valid(curr: datetime, fut: datetime) -> bool:
        #     print(curr, fut)
        #     delta = fut - curr
        #     return 23 <= delta.days <= 37

        def filter_t(row, d: datetime) -> bool:
            delta = d - row['date']
            return 23 <= delta.days <= 37

        df = self.df
        return df.apply(lambda row: filter_t(row, date), axis=1, )




file_path = "./data/sample/01.csv"
df = pd.read_csv(file_path)

mdf = SampleData01(df)
mdf.process()
print(mdf.df.head())

curr_datetime = datetime.strptime("20220920", '%Y%m%d')
print(curr_datetime)


df2 = mdf.get_t_data(curr_datetime)
print(df2)
