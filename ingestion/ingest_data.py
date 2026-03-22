import argparse
import pandas as pd
from sqlalchemy import create_engine
from tqdm import tqdm

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    csv_path = params.csv_path

    engine=create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}')

    df_iter = pd.read_csv(csv_path, iterator=True, chunksize=100000)

    first = True

    for df_chunk in tqdm(df_iter):
        if first:
            df_chunk.head(0).to_sql(
                name=table_name,
                con=engine,
                if_exists='replace'
            )
            first = False
        
        df_chunk.to_sql(
            name=table_name,
            con=engine,
            if_exists='append'
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--user', required=True)
    parser.add_argument('--password', required=True)
    parser.add_argument('--host', required=True)
    parser.add_argument('--port', required=True)
    parser.add_argument('--db', required=True)
    parser.add_argument('--table_name', required=True)
    parser.add_argument('--csv_path', required=True)

    args = parser.parse_args()

    main(args)