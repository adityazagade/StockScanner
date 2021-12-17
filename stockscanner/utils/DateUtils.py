def get_df_between_dates(df, start_date, end_date):
    mask = (df['Date'] >= start_date.strftime("%d-%b-%Y")) & (df['Date'] < (end_date).strftime("%d-%b-%Y"))
    return df.loc[mask]