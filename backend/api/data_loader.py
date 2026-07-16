import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'

_shops_df = None
_reviews_df = None

def load_data():
    global _shops_df, _reviews_df
    if _shops_df is not None and _reviews_df is not None:
        return _shops_df, _reviews_df
    
    shops_path = DATA_DIR / 'shops.csv'
    reviews_path = DATA_DIR / 'reviews.csv'
    
    print(f"[INFO] 正在从 {shops_path} 加载店铺数据...")
    shops = pd.read_csv(shops_path, dtype={'item_id': str}, encoding='utf-8-sig')
    print(f"[INFO] 加载店铺数据完成，共 {len(shops)} 条")
    
    print(f"[INFO] 正在从 {reviews_path} 加载评论数据...")
    reviews = pd.read_csv(reviews_path, dtype={'item_id': str, 'data_id': str}, encoding='utf-8-sig')
    reviews['times'] = reviews['times'].astype(str)
    reviews.dropna(subset=['review'], inplace=True)
    print(f"[INFO] 加载评论数据完成，共 {len(reviews)} 条")
    
    _shops_df = shops
    _reviews_df = reviews
    return _shops_df, _reviews_df

def get_data():
    return load_data()