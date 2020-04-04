#!/usr/bin/python3
import pandas as pd


def test_func():
    #df = pd.read_excel('covid_oc.xlsx', 'Sheet1', index_col=0)
    df = pd.read_excel('covid_oc.xlsx', 'Sheet1')
    df2 = df.drop([df.index[0]])
    df3 = df2.drop(['Cum C', 'Cum D'], axis=1)
    #print(df3)
    date_list = df3['Date'].tolist()
    #print(date_list)
    df3['UltDied'] = 0
    for i,v in df3.iterrows():
        if v["Deaths"]:
            #print(f"idx {i} val {v}")
            #dt = df3.loc[df3.index==i].index.values[0]
            dt = v['Date']
            dt2 = dt - pd.Timedelta(days=19)
            #print(type(dt))
            print(dt2)
            if dt2 in date_list:
                df3.at[df3.loc[df3['Date']==dt2].index, 'UltDied'] = v["Deaths"]
            else:
                # add row of zeros except positive value in 'UltDied'
                add_row_dict = { 'Date' : dt2, 'Confirmed' : 0, 'Deaths' : 0,  'UltDied' : v["Deaths"] }
                new_row = pd.DataFrame(data=add_row_dict, index=[0])
                df3 = df3.append(new_row, ignore_index=True)

    df4 = df3.sort_values(by=['Date'])
    df4['CumConf'] = df4.groupby('Date')['Confirmed'].transform(pd.Series.cumsum)
    df4['PotRec'] = df4['Confirmed'] - df4['UltDied'] 
    print(df4)

if __name__ == '__main__':
    test_func()
