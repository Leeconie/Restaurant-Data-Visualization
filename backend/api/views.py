from rest_framework.decorators import api_view
from rest_framework.response import Response
from .data_processor import (
    get_comment_count, get_star_ratio, get_wordcloud, get_restaurant_names,
    get_overview_stats, get_review_trend, get_restaurant_ranking, get_restaurant_detail,
    get_compare_data, get_compare_trend, get_compare_boxplot, get_sentiment_analysis, get_topic_model, get_clustering
)

from .data_loader import get_data
import pandas as pd
from django.http import JsonResponse

@api_view(['GET'])
def comment_count_api(request):
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')
    top_n = request.GET.get('top_n')
    if top_n is not None:
        top_n = int(top_n)
    data = get_comment_count(start_date=start, end_date=end, top_n=top_n)
    return Response(data)

@api_view(['GET'])
def star_ratio_api(request):
    restaurant = request.GET.get('restaurant_name', '全部')
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')
    data = get_star_ratio(restaurant_name=restaurant, start_date=start, end_date=end)
    return Response(data)

@api_view(['GET'])
def wordcloud_api(request):
    restaurant = request.GET.get('restaurant_name', '全部')
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')
    data = get_wordcloud(restaurant_name=restaurant, start_date=start, end_date=end)
    return Response(data)

@api_view(['GET'])
def restaurant_names_api(request):
    data = get_restaurant_names()
    return Response(data)

@api_view(['GET'])
def overview_stats_api(request):
    data = get_overview_stats()
    return Response(data)

@api_view(['GET'])
def review_trend_api(request):
    data = get_review_trend()
    return Response(data)

@api_view(['GET'])
def restaurant_ranking_api(request):
    sort_by = request.GET.get('sort_by', 'review_count')
    data = get_restaurant_ranking(sort_by)
    return Response(data)

@api_view(['GET'])
def restaurant_detail_api(request, restaurant_id):
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')
    data = get_restaurant_detail(restaurant_id, start_date=start, end_date=end)
    return Response(data)

@api_view(['POST'])
def compare_api(request):
    ids = request.data.get('ids', [])
    start = request.data.get('start_date')
    end = request.data.get('end_date')
    data = get_compare_data(ids, start_date=start, end_date=end)
    return Response(data)

@api_view(['POST'])
def compare_trend_api(request):
    ids = request.data.get('ids', [])
    start = request.data.get('start_date')
    end = request.data.get('end_date')
    data = get_compare_trend(ids, start_date=start, end_date=end)
    return Response(data)

@api_view(['GET'])
def correlation_api(request):
    """评分维度相关性热力图数据 - 基于评论数前50的餐厅"""
    shops, _ = get_data()
    # 按评论数降序排序，取前50
    top_shops = shops.sort_values('review_count', ascending=False).head(50)
    df_corr = top_shops[['star', 'score_taste', 'score_environment', 'score_service']].dropna()
    corr_matrix = df_corr.corr().round(4)
    fields = corr_matrix.columns.tolist()
    data = corr_matrix.values.tolist()
    return Response({'fields': fields, 'data': data})

@api_view(['GET'])
def scatter_api(request):
    """人均消费 vs 星级 散点图数据（气泡大小=评论数）- 基于评论数前50且人均消费<=300的餐厅"""
    shops, _ = get_data()
    top_shops = shops.sort_values('review_count', ascending=False).head(50)
    df = top_shops[['name', 'star', 'cost', 'review_count']].dropna(subset=['cost', 'star'])
    # 过滤掉人均消费超过300的餐厅
    # df = df[df['cost'] <= 300]
    result = df.to_dict(orient='records')
    return Response(result)

@api_view(['POST'])
def compare_boxplot_api(request):
    ids = request.data.get('ids', [])
    start = request.data.get('start_date')
    end = request.data.get('end_date')
    data = get_compare_boxplot(ids, start_date=start, end_date=end)
    return Response(data)


@api_view(['GET'])
def sentiment_analysis(request):
    restaurant = request.GET.get('restaurant')
    start = request.GET.get('start')
    end = request.GET.get('end')
    data = get_sentiment_analysis(restaurant_name=restaurant, start_date=start, end_date=end)
    return Response(data)   # 改为 Response

@api_view(['GET'])
def topic_model(request):
    restaurant = request.GET.get('restaurant')
    start = request.GET.get('start')
    end = request.GET.get('end')
    data = get_topic_model(restaurant_name=restaurant, start_date=start, end_date=end)
    return Response(data)

@api_view(['GET'])
def clustering(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    data = get_clustering(start_date=start, end_date=end)
    return Response(data)