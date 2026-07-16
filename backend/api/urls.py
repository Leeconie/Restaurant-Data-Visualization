from django.urls import path
from . import views

urlpatterns = [
    path('comment-count/', views.comment_count_api),
    path('star-ratio/', views.star_ratio_api),
    path('wordcloud/', views.wordcloud_api),
    path('restaurant-names/', views.restaurant_names_api),
    path('overview-stats/', views.overview_stats_api),
    path('review-trend/', views.review_trend_api),
    path('restaurant-ranking/', views.restaurant_ranking_api),
    path('restaurant/<str:restaurant_id>/', views.restaurant_detail_api),
    path('compare/', views.compare_api),
    path('compare-trend/', views.compare_trend_api),
    path('correlation/', views.correlation_api),
    path('scatter/', views.scatter_api),
    path('compare-boxplot/', views.compare_boxplot_api),
    
    path('analysis/sentiment/', views.sentiment_analysis, name='sentiment_analysis'),
    path('analysis/topics/', views.topic_model, name='topic_model'),
    path('analysis/clustering/', views.clustering, name='clustering'),
]