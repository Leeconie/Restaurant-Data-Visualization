# 广州粤菜餐厅大数据平台

一个基于 Django 后端和 Vue 3 前端的餐厅数据可视化平台，提供全面的餐厅数据统计、排行和对比分析功能。

## 功能特性

### 数据总览
- 餐厅数量、总评论数等核心指标统计
- 评论趋势时间序列图表
- 评分维度相关性热力图
- 人均消费与星级关系散点图
- 关键词词云可视化

### 餐厅排行
- 按评论数、评分等多维度排序
- 各餐厅星级分布环形图
- 详细信息卡片展示

### 对比分析
- 支持选择多个餐厅进行对比
- 各维度评分对比柱状图
- 时间趋势对比折线图
- 评分分布箱线图

### 数据分析
- 情感分析
- 主题模型
- 聚类分析

## 技术栈

### 后端
- **框架**: Django 4.2
- **API**: Django REST Framework
- **数据处理**: Pandas, NumPy
- **自然语言处理**: jieba
- **机器学习**: scikit-learn (隐含)

### 前端
- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **UI 组件库**: Element Plus
- **图表库**: ECharts 5, ECharts WordCloud
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP 客户端**: Axios

## 项目结构

```
Restaurant-Data-Visualization/
├── backend/                 # Django 后端
│   ├── api/                # API 应用
│   │   ├── views.py        # 视图函数
│   │   ├── data_processor.py  # 数据处理模块
│   │   └── data_loader.py  # 数据加载模块
│   ├── backend/            # 项目配置
│   └── data/               # 数据文件
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── components/     # 图表组件
│   │   ├── views/          # 页面视图
│   │   ├── stores/         # Pinia 状态管理
│   │   └── router/         # 路由配置
│   └── package.json
└── requirements.txt        # Python 依赖
```

## 快速开始

### 环境要求

- Python >= 3.9
- Node.js >= 20.19.0

### 后端启动

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r ../requirements.txt

# 数据库迁移
python manage.py migrate

# 启动开发服务器
python manage.py runserver
```

后端服务将在 http://localhost:8000 启动

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

前端开发服务器将在 http://localhost:5173 启动

## 主要 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/overview_stats/` | GET | 获取总览统计数据 |
| `/api/review_trend/` | GET | 获取评论趋势 |
| `/api/restaurant_ranking/` | GET | 获取餐厅排行 |
| `/api/restaurant_detail/{id}/` | GET | 获取餐厅详情 |
| `/api/compare/` | POST | 对比多个餐厅 |
| `/api/wordcloud/` | GET | 获取词云数据 |
| `/api/correlation/` | GET | 获取相关性热力图数据 |
| `/api/scatter/` | GET | 获取散点图数据 |
| `/api/sentiment/` | GET | 情感分析 |
| `/api/topic/` | GET | 主题模型 |
| `/api/clustering/` | GET | 聚类分析 |

## 数据说明

项目包含两份主要数据文件：
- `shops.csv`: 餐厅基本信息（名称、星级、人均消费等）
- `reviews.csv`: 用户评论数据

## 开发建议

### IDE 配置
- **前端**: VS Code + Vue (Official) 插件
- **浏览器**: Chrome/Edge + Vue.js Devtools

### 代码规范
- 前端遵循 Vue 3 官方风格指南
- 后端遵循 Django REST Framework 最佳实践

## 许可证

MIT License
