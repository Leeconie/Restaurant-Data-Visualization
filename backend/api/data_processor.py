import pandas as pd
import jieba.analyse
from .data_loader import get_data
import math
import random          # 新增导入，用于随机采样

def clean_nan_in_dict(obj):
    if isinstance(obj, dict):
        return {k: clean_nan_in_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan_in_dict(i) for i in obj]
    elif isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    else:
        return obj

def get_comment_count(start_date=None, end_date=None, top_n=50):
    shops, reviews = get_data()
    merged = pd.merge(reviews, shops[['item_id', 'name']], on='item_id', how='left')
    if start_date:
        merged = merged[merged['times'] >= start_date]
    if end_date:
        merged = merged[merged['times'] <= end_date]
    count_df = merged.groupby('name').size().reset_index(name='count')
    count_df = count_df.sort_values('count', ascending=False)
    if top_n and isinstance(top_n, int) and top_n > 0:
        count_df = count_df.head(top_n)
    result = count_df.to_dict(orient='records')
    for r in result:
        r['count'] = int(r['count'])
    return result

def get_star_level(score):
    """根据原始星级分数返回等级（1-5），划分标准： [1,2)->1, [2,3)->2, [3,4)->3, [4,5)->4, [5]->5 """
    if pd.isna(score):
        return None
    if score == 5.0:
        return 5
    elif 4.0 <= score < 5.0:
        return 4
    elif 3.0 <= score < 4.0:
        return 3
    elif 2.0 <= score < 3.0:
        return 2
    elif 1.0 <= score < 2.0:
        return 1
    else:
        return None  # 超出范围的值视为无效

def get_star_ratio(restaurant_name=None, start_date=None, end_date=None):
    shops, reviews = get_data()
    if restaurant_name and restaurant_name != '全部':
        shop = shops[shops['name'] == restaurant_name]
        if shop.empty:
            return []
        star_val = shop.iloc[0]['star']
        star_level = get_star_level(star_val)
        if star_level is None:
            return []
        return [{'star': star_level, 'value': 1, 'percent': 100}]

    # 按时间范围过滤餐厅（仅保留有评论的餐厅）
    if start_date or end_date:
        filtered_reviews = reviews.copy()
        if start_date:
            filtered_reviews = filtered_reviews[filtered_reviews['times'] >= start_date]
        if end_date:
            filtered_reviews = filtered_reviews[filtered_reviews['times'] <= end_date]
        active_shop_ids = filtered_reviews['item_id'].unique()
        shops = shops[shops['item_id'].isin(active_shop_ids)]

    # 为每个餐厅计算星级等级（使用上述分段规则）
    star_levels = shops['star'].apply(get_star_level)
    # 过滤掉无效等级（None）
    star_levels = star_levels.dropna()
    star_counts = star_levels.value_counts().sort_index()
    total = star_counts.sum()
    if total == 0:
        return []

    ratio = [{'star': int(star), 'value': int(cnt), 'percent': round(cnt/total*100, 2)}
             for star, cnt in star_counts.items()]
    return ratio

def get_wordcloud(restaurant_name=None, start_date=None, end_date=None, top_k=50, max_samples=5000):
    """
    生成词云数据，支持时间范围和餐厅筛选，并对评论进行随机采样（最多 max_samples 条）以提升性能。
    """
    shops, reviews = get_data()
    merged = pd.merge(reviews, shops[['item_id', 'name']], on='item_id', how='left')
    if restaurant_name and restaurant_name != '全部':
        merged = merged[merged['name'] == restaurant_name]
    # 时间筛选
    if start_date:
        merged = merged[merged['times'] >= start_date]
    if end_date:
        merged = merged[merged['times'] <= end_date]
    if merged.empty:
        return []

    # 随机采样（仅当评论数超过 max_samples 时）
    total_count = len(merged)
    if total_count > max_samples:
        sample_indices = random.sample(range(total_count), max_samples)
        merged = merged.iloc[sample_indices]
        # 可选：在 Django 终端打印日志（调试用，可删除）
        print(f"[INFO] 词云采样: 从 {total_count} 条评论中随机抽取 {max_samples} 条进行分析")

    all_text = ' '.join(merged['review'].tolist())
    keywords = jieba.analyse.extract_tags(all_text, topK=top_k, withWeight=True)
    result = [{'name': kw, 'value': int(w*100)} for kw, w in keywords]
    return result

def get_restaurant_names():
    shops, _ = get_data()
    return ['全部'] + sorted(shops['name'].tolist())

def get_overview_stats():
    shops, reviews = get_data()
    total_restaurants = len(shops)
    total_reviews = len(reviews)
    avg_star = round(shops['star'].mean(), 2)
    sample_reviews = reviews['review'].head(10000)
    all_text = ' '.join(sample_reviews.tolist())
    keywords = jieba.analyse.extract_tags(all_text, topK=5)
    return {
        'total_restaurants': total_restaurants,
        'total_reviews': total_reviews,
        'avg_star': avg_star,
        'top_keywords': keywords
    }

def get_review_trend():
    _, reviews = get_data()
    reviews['year_month'] = reviews['times'].str[:6]
    trend = reviews.groupby('year_month').size().reset_index(name='count')
    trend = trend.sort_values('year_month')
    result = trend.to_dict(orient='records')
    for r in result:
        r['count'] = int(r['count'])
    return result

def get_restaurant_ranking(sort_by):
    shops, _ = get_data()
    if sort_by not in shops.columns:
        sort_by = 'review_count'
    cols = ['item_id', 'name', 'star', 'cost', 'review_count',
            'score_taste', 'score_environment', 'score_service']
    df = shops[cols].copy()
    df = df.where(pd.notnull(df), None)
    df = df.sort_values(sort_by, ascending=False)
    result = df.to_dict(orient='records')
    for r in result:
        if r.get('cost') is not None and not isinstance(r['cost'], (int, float)):
            r['cost'] = None
        if r.get('review_count') is not None:
            r['review_count'] = int(r['review_count'])
        if r.get('star') is not None:
            r['star'] = round(r['star'], 1)
    return clean_nan_in_dict(result)

def get_restaurant_detail(restaurant_id, start_date=None, end_date=None):
    shops, reviews = get_data()
    shop = shops[shops['item_id'] == restaurant_id]
    if shop.empty:
        return {'error': 'not found'}
    info = shop.iloc[0].to_dict()

    # 筛选时间范围内的评论
    revs = reviews[reviews['item_id'] == restaurant_id].copy()
    if start_date:
        revs = revs[revs['times'] >= start_date]
    if end_date:
        revs = revs[revs['times'] <= end_date]

    # 计算时间段内的平均评分（如果无评论则使用全局平均值或 None）
    if len(revs) > 0:
        avg_rating = revs['rating_score'].mean() if 'rating_score' in revs else None
        avg_taste = revs['score_taste'].mean() if 'score_taste' in revs else None
        avg_env = revs['score_environment'].mean() if 'score_environment' in revs else None
        avg_service = revs['score_service'].mean() if 'score_service' in revs else None
        # 覆盖 info 中的对应字段（综合星级优先使用 rating_score 平均值，若无则使用店铺星级）
        if avg_rating is not None:
            info['star'] = round(avg_rating, 2)
        if avg_taste is not None:
            info['score_taste'] = round(avg_taste, 2)
        if avg_env is not None:
            info['score_environment'] = round(avg_env, 2)
        if avg_service is not None:
            info['score_service'] = round(avg_service, 2)
    else:
        # 无评论时，将评分置为 None 或保留原值，但建议置为 None 表示无数据
        info['star'] = None
        info['score_taste'] = None
        info['score_environment'] = None
        info['score_service'] = None

    # 其他数据（趋势、词云）继续使用过滤后的 revs
    revs['year_month'] = revs['times'].str[:6]
    trend = revs.groupby('year_month').size().reset_index(name='count')
    trend = trend.sort_values('year_month')
    all_text = ' '.join(revs['review'].tolist())
    keywords = jieba.analyse.extract_tags(all_text, topK=50, withWeight=True)
    wordcloud = [{'name': kw, 'value': int(w*100)} for kw, w in keywords]

    # 清理 NaN
    info = {k: (None if (isinstance(v, float) and (math.isnan(v) or math.isinf(v))) else v) for k, v in info.items()}
    return {
        'info': info,
        'trend': trend.to_dict(orient='records'),
        'wordcloud': wordcloud,
        'review_count': int(len(revs))
    }

def get_compare_data(ids, start_date=None, end_date=None):
    shops, reviews = get_data()
    ids = [str(i) for i in ids]
    # 筛选出选中餐厅的评论
    filtered = reviews[reviews['item_id'].isin(ids)].copy()
    # 如果没有评论数据，直接返回空列表
    if filtered.empty:
        return []
    # 确保 times 列为字符串，避免类型比较错误
    filtered['times'] = filtered['times'].astype(str)
    if start_date:
        filtered = filtered[filtered['times'] >= start_date]
    if end_date:
        filtered = filtered[filtered['times'] <= end_date]

    result = []
    for shop_id in ids:
        shop = shops[shops['item_id'] == shop_id]
        if shop.empty:
            continue
        shop_info = shop.iloc[0].to_dict()
        revs = filtered[filtered['item_id'] == shop_id]
        if len(revs) > 0:
            avg_rating = revs['rating_score'].mean() if 'rating_score' in revs else None
            avg_taste = revs['score_taste'].mean() if 'score_taste' in revs else None
            avg_env = revs['score_environment'].mean() if 'score_environment' in revs else None
            avg_service = revs['score_service'].mean() if 'score_service' in revs else None
            shop_info['star'] = round(avg_rating, 2) if avg_rating is not None else None
            shop_info['score_taste'] = round(avg_taste, 2) if avg_taste is not None else None
            shop_info['score_environment'] = round(avg_env, 2) if avg_env is not None else None
            shop_info['score_service'] = round(avg_service, 2) if avg_service is not None else None
            shop_info['review_count'] = len(revs)
        else:
            shop_info['review_count'] = 0
            shop_info['star'] = None
            shop_info['score_taste'] = None
            shop_info['score_environment'] = None
            shop_info['score_service'] = None
        result.append({
            'item_id': shop_id,
            'name': shop_info['name'],
            'star': shop_info['star'],
            'cost': shop_info['cost'],
            'review_count': shop_info['review_count'],
            'score_taste': shop_info['score_taste'],
            'score_environment': shop_info['score_environment'],
            'score_service': shop_info['score_service']
        })
    return clean_nan_in_dict(result)

def get_compare_trend(ids, start_date=None, end_date=None):
    shops, reviews = get_data()
    ids = [str(i) for i in ids]
    filtered = reviews[reviews['item_id'].isin(ids)].copy()
    if filtered.empty:
        return {'total': [], 'monthly': []}
    # 确保 times 列为字符串
    filtered['times'] = filtered['times'].astype(str)
    if start_date:
        filtered = filtered[filtered['times'] >= start_date]
    if end_date:
        filtered = filtered[filtered['times'] <= end_date]
    if filtered.empty:
        return {'total': [], 'monthly': []}
    
    total_counts = filtered.groupby('item_id').size().reset_index(name='count')
    name_map = shops.set_index('item_id')['name'].to_dict()
    total_counts['name'] = total_counts['item_id'].map(name_map)
    total_data = total_counts[['name', 'count']].to_dict(orient='records')
    
    filtered['year_month'] = filtered['times'].str[:6]
    monthly = filtered.groupby(['item_id', 'year_month']).size().reset_index(name='count')
    monthly['name'] = monthly['item_id'].map(name_map)
    trend_data = monthly[['name', 'year_month', 'count']].to_dict(orient='records')
    
    return {'total': total_data, 'monthly': trend_data}

def get_compare_boxplot(ids, start_date=None, end_date=None):
    shops, reviews = get_data()
    ids = [str(i) for i in ids]
    reviews['item_id'] = reviews['item_id'].astype(str)
    filtered = reviews[reviews['item_id'].isin(ids)].copy()
    if start_date:
        filtered = filtered[filtered['times'] >= start_date]
    if end_date:
        filtered = filtered[filtered['times'] <= end_date]

    name_map = shops.set_index('item_id')['name'].to_dict()
    result = {}
    score_columns = {
        'rating_score': '综合评分',
        'score_taste': '口味',
        'score_environment': '环境',
        'score_service': '服务'
    }
    for rid in ids:
        revs = filtered[filtered['item_id'] == rid]
        item_result = {'name': name_map.get(rid, rid)}
        for col, label in score_columns.items():
            scores = revs[col].dropna().tolist()
            if not scores:
                item_result[col] = {'raw_data': [], 'error': 'no data'}
                continue
            # 返回原始评分数据（列表）
            item_result[col] = {
                'raw_data': scores,
                'box_data': [min(scores), 
                             sorted(scores)[int(len(scores)*0.25)], 
                             sorted(scores)[len(scores)//2], 
                             sorted(scores)[int(len(scores)*0.75)], 
                             max(scores)],
                'outliers': []  # 前端将使用 raw_data 自动计算离群点
            }
        result[rid] = item_result
    return result

# ============ 数据分析功能 ============

def get_sentiment_analysis(restaurant_name=None, start_date=None, end_date=None):
    """
    情感分析：统计正面/中性/负面评论数量、趋势、各餐厅正面占比。
    使用简单的基于规则或预训练模型，这里仅示意结构。
    """
    shops, reviews = get_data()
    # 合并评论和餐厅信息
    merged = pd.merge(reviews, shops[['item_id', 'name']], on='item_id', how='left')
    if restaurant_name and restaurant_name != '全部':
        merged = merged[merged['name'] == restaurant_name]
    if start_date:
        merged = merged[merged['times'] >= start_date]
    if end_date:
        merged = merged[merged['times'] <= end_date]

    if merged.empty:
        return {'summary': {'positive':0,'neutral':0,'negative':0}, 'trend': [], 'compare': []}

    # 模拟情感打分（实际需用模型）
    # 这里假设评论中"好"、"赞"等词为正面，可用简单规则或调用 jieba 情感分析。
    # 为演示，随机生成（实际应替换为真实情感计算）
    import random
    random.seed(42)
    sentiments = []
    for _ in range(len(merged)):
        r = random.random()
        if r < 0.7:
            sentiments.append('positive')
        elif r < 0.85:
            sentiments.append('neutral')
        else:
            sentiments.append('negative')
    merged['sentiment'] = sentiments

    # 汇总
    summary = merged['sentiment'].value_counts().to_dict()
    summary = {
        'positive': summary.get('positive', 0),
        'neutral': summary.get('neutral', 0),
        'negative': summary.get('negative', 0)
    }

    # 趋势（按月）
    merged['year_month'] = merged['times'].str[:6]
    trend_df = merged.groupby(['year_month', 'sentiment']).size().unstack(fill_value=0)
    trend = []
    for month, row in trend_df.iterrows():
        trend.append({
            'month': month,
            'positive': int(row.get('positive', 0)),
            'neutral': int(row.get('neutral', 0)),
            'negative': int(row.get('negative', 0))
        })
    trend = sorted(trend, key=lambda x: x['month'])

    # 各餐厅正面占比
    compare = []
    if not restaurant_name or restaurant_name == '全部':
        restaurant_sent = merged.groupby(['name', 'sentiment']).size().unstack(fill_value=0)
        for name, row in restaurant_sent.iterrows():
            total = row.sum()
            pos_ratio = row.get('positive', 0) / total if total > 0 else 0
            compare.append({'name': name, 'positive_ratio': round(pos_ratio, 4)})
        compare = sorted(compare, key=lambda x: -x['positive_ratio'])[:10]  # 取前10
    else:
        # 单餐厅不展示对比
        pass

    return {'summary': summary, 'trend': trend, 'compare': compare}


def get_topic_model(restaurant_name=None, start_date=None, end_date=None, num_topics=5):
    """
    主题模型：使用LDA提取评论主题。
    同样需要实际训练，这里用模拟数据。
    """
    # 实际应调用 jieba.analyse 或 gensim LDA
    # 为快速演示，返回固定示例
    # 您可以替换为真实 LDA 训练代码
    topics = [
        {'id': 0, 'keywords': ['服务', '热情', '周到', '态度'], 'weight': 0.25},
        {'id': 1, 'keywords': ['价格', '实惠', '性价比', '便宜'], 'weight': 0.20},
        {'id': 2, 'keywords': ['口味', '好吃', '味道', '鲜美'], 'weight': 0.30},
        {'id': 3, 'keywords': ['环境', '装修', '干净', '舒适'], 'weight': 0.15},
        {'id': 4, 'keywords': ['等待', '排队', '慢', '久'], 'weight': 0.10}
    ]
    # 模拟趋势（按月）
    trend = [
        {'month': '2024-01', 'topic_0': 0.2, 'topic_1': 0.25, 'topic_2': 0.35, 'topic_3': 0.1, 'topic_4': 0.1},
        {'month': '2024-02', 'topic_0': 0.22, 'topic_1': 0.23, 'topic_2': 0.33, 'topic_3': 0.12, 'topic_4': 0.1},
        {'month': '2024-03', 'topic_0': 0.25, 'topic_1': 0.2, 'topic_2': 0.3, 'topic_3': 0.15, 'topic_4': 0.1},
        {'month': '2024-04', 'topic_0': 0.27, 'topic_1': 0.18, 'topic_2': 0.28, 'topic_3': 0.17, 'topic_4': 0.1},
        {'month': '2024-05', 'topic_0': 0.3, 'topic_1': 0.15, 'topic_2': 0.25, 'topic_3': 0.2, 'topic_4': 0.1}
    ]
    return {'topics': topics, 'topic_trend': trend}


def get_clustering(restaurant_name=None, start_date=None, end_date=None):
    """
    餐厅聚类：基于特征（人均消费、星级、评论数、各维度评分）进行K-Means。
    返回聚类结果、散点图数据（PCA降维）等。
    """
    shops, reviews = get_data()
    # 选择特征列
    feature_cols = ['cost', 'star', 'review_count', 'score_taste', 'score_environment', 'score_service']
    df = shops[['item_id', 'name'] + feature_cols].copy()
    # 填充缺失值
    df.fillna(0, inplace=True)

    # 仅保留有评论的餐厅（可调整）
    if start_date or end_date:
        filtered_reviews = reviews.copy()
        if start_date:
            filtered_reviews = filtered_reviews[filtered_reviews['times'] >= start_date]
        if end_date:
            filtered_reviews = filtered_reviews[filtered_reviews['times'] <= end_date]
        active_ids = filtered_reviews['item_id'].unique()
        df = df[df['item_id'].isin(active_ids)]

    if len(df) < 3:
        return {'clusters': [], 'scatter_data': []}

    # 标准化
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans

    X = df[feature_cols].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 聚类
    k = min(4, len(df))  # 动态确定簇数
    kmeans = KMeans(n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(X_scaled)

    # PCA降维
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)

    # 构建返回数据
    clusters_dict = {}
    for i, label in enumerate(labels):
        row = df.iloc[i]
        name = row['name']
        if label not in clusters_dict:
            clusters_dict[label] = {'size': 0, 'restaurants': [], 'center': {feat: 0 for feat in feature_cols}}
        clusters_dict[label]['size'] += 1
        clusters_dict[label]['restaurants'].append(name)
        for feat in feature_cols:
            clusters_dict[label]['center'][feat] += row[feat]

    # 计算簇中心平均值
    clusters = []
    color_palette = ['#5470c6', '#fac858', '#ee6666', '#73c0de', '#3ba272']
    for label, data in clusters_dict.items():
        size = data['size']
        center = {feat: round(data['center'][feat] / size, 2) for feat in feature_cols}
        clusters.append({
            'cluster_id': label,
            'size': size,
            'center': center,
            'restaurants': data['restaurants'],
            'color': color_palette[label % len(color_palette)]
        })

    # 散点数据
    scatter_data = []
    for i, row in df.iterrows():
        scatter_data.append({
            'x': round(X_pca[i][0], 4),
            'y': round(X_pca[i][1], 4),
            'name': row['name'],
            'cluster': int(labels[i])
        })

    return {'clusters': clusters, 'scatter_data': scatter_data}