import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

// 原有接口
export const getCommentCount = (params) => api.get('/comment-count/', { params })
export const getStarRatio = (params) => api.get('/star-ratio/', { params })
export const getWordCloud = (params) => api.get('/wordcloud/', { params })
export const getRestaurantNames = () => api.get('/restaurant-names/')

// 新增接口
export const getOverviewStats = () => api.get('/overview-stats/')
export const getReviewTrend = () => api.get('/review-trend/')
export const getRestaurantRanking = (params) => api.get('/restaurant-ranking/', { params })
export const getRestaurantDetail = (id, params) => api.get(`/restaurant/${id}/`, { params })
export const getCompareData = (data) => api.post('/compare/', data)
export const getCompareTrend = (data) => api.post('/compare-trend/', data)

export const getCorrelation = () => api.get('/correlation/')
export const getScatter = () => api.get('/scatter/')

export const getCompareBoxplot = (data) => api.post('/compare-boxplot/', data)



export const getSentimentData = (params) => api.get('/analysis/sentiment/', { params })
export const getTopicData = (params) => api.get('/analysis/topic/', { params })
export const getClusteringData = (params) => api.get('/analysis/clustering/', { params })


export const apiInstance = api;