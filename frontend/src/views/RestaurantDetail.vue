<template>
  <div class="detail-container" v-loading="loading">
    <!-- 返回按钮 -->
    <div class="back-btn">
      <el-button type="primary" plain @click="$router.back()">
        ← 返回餐厅列表
      </el-button>
    </div>

    <!-- 餐厅基本信息卡片（渐变头部） -->
    <el-card class="info-card" shadow="hover">
      <div class="card-header">
        <h2>{{ info.name }}</h2>
        <div class="rating-badge">
          <span class="star">⭐ {{ info.star ? info.star.toFixed(2) : '—' }}</span>
        </div>
      </div>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="人均消费">¥{{ info.cost ? info.cost.toFixed(2) : '—' }}</el-descriptions-item>
        <el-descriptions-item label="评论总数">{{ reviewCount }}</el-descriptions-item>
        <el-descriptions-item label="口味评分">{{ info.score_taste ? info.score_taste.toFixed(2) : '—' }}</el-descriptions-item>
        <el-descriptions-item label="环境评分">{{ info.score_environment ? info.score_environment.toFixed(2) : '—' }}</el-descriptions-item>
        <el-descriptions-item label="服务评分">{{ info.score_service ? info.score_service.toFixed(2) : '—' }}</el-descriptions-item>
      </el-descriptions>
      <!-- 装饰小图标 -->
      <div class="card-decoration">🍜</div>
    </el-card>

    <!-- 时间范围选择器（美化） -->
    <div class="controls-card">
      <div class="control-group">
        <label>📅 评论时间范围</label>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYYMMDD"
          value-format="YYYYMMDD"
          @change="onDateChange"
          :clearable="false"
        />
      </div>
      <div class="hint-text">💡 改变时间范围 → 趋势图和词云自动更新</div>
    </div>

    <!-- 图表区域（增加色彩和阴影） -->
    <el-row :gutter="24" class="chart-row">
      <el-col :span="14">
        <el-card class="chart-card" shadow="hover">
          <div class="card-title">📈 评论数量趋势</div>
          <div ref="trendChart" style="height: 350px;"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card class="chart-card" shadow="hover">
          <div class="card-title">📊 评分维度雷达图</div>
          <div ref="radarChart" style="height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="24" class="chart-row">
      <el-col :span="24">
        <el-card class="chart-card full-width" shadow="hover">
          <div class="card-title">☁️ 评论关键词词云</div>
          <div ref="wordCloudChart" style="height: 480px;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { getRestaurantDetail } from '@/api'
import * as echarts from 'echarts'
import 'echarts-wordcloud'

export default {
  props: ['id'],
  data() {
    return {
      loading: true,
      info: {},
      reviewCount: 0,
      trendData: [],
      wordData: [],
      dateRange: ['20150101', '20171031']
    }
  },
  async mounted() {
    await this.loadDetail()
    this.loading = false
    this.renderCharts()
  },
  methods: {
    async loadDetail() {
      const params = {
        start_date: this.dateRange[0],
        end_date: this.dateRange[1]
      }
      const res = await getRestaurantDetail(this.id, params)
      this.info = res.data.info
      this.trendData = res.data.trend
      this.wordData = res.data.wordcloud
      this.reviewCount = res.data.review_count
    },
    async onDateChange() {
      this.loading = true
      await this.loadDetail()
      this.loading = false
      this.renderCharts()
    },
    renderCharts() {
      // 趋势图（使用渐变色面积）
      const trendChart = echarts.init(this.$refs.trendChart)
      trendChart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: this.trendData.map(d => d.year_month), name: '年月', axisLine: { lineStyle: { color: '#667eea' } } },
        yAxis: { type: 'value', name: '评论数', axisLine: { lineStyle: { color: '#667eea' } } },
        series: [{
          type: 'line',
          data: this.trendData.map(d => d.count),
          smooth: true,
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(102,126,234,0.6)' },
              { offset: 1, color: 'rgba(118,75,162,0.1)' }
            ])
          },
          lineStyle: { width: 3, color: '#667eea' },
          symbol: 'circle',
          symbolSize: 6,
          itemStyle: { color: '#764ba2' }
        }]
      })

      // 雷达图（彩色填充）
      const radarChart = echarts.init(this.$refs.radarChart)
      radarChart.setOption({
        tooltip: {},
        radar: {
          indicator: [
            { name: '口味', max: 5 },
            { name: '环境', max: 5 },
            { name: '服务', max: 5 },
            { name: '综合', max: 5 }
          ],
          shape: 'circle',
          name: { textStyle: { fontSize: 12, fontWeight: 'bold', color: '#2c3e50' } },
          splitArea: { areaStyle: { color: ['rgba(102,126,234,0.1)', 'rgba(118,75,162,0.1)'] } }
        },
        series: [{
          type: 'radar',
          data: [{
            value: [
              this.info.score_taste || 0,
              this.info.score_environment || 0,
              this.info.score_service || 0,
              this.info.star || 0
            ],
            name: this.info.name
          }],
          areaStyle: { color: 'rgba(102,126,234,0.4)' },
          lineStyle: { color: '#667eea', width: 2 },
          itemStyle: { color: '#764ba2', borderWidth: 2, borderColor: '#fff' }
        }]
      })

      // 词云（丰富颜色）
      const wc = echarts.init(this.$refs.wordCloudChart)
      wc.setOption({
        series: [{
          type: 'wordCloud',
          shape: 'circle',
          sizeRange: [16, 70],
          rotationRange: [-45, 90],
          gridSize: 10,
          layoutAnimation: true,
          textStyle: {
            fontFamily: 'sans-serif',
            fontWeight: 'bold',
            color: function () {
              const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', '#fa709a', '#fee140', '#43e97b', '#38f9d7']
              return colors[Math.floor(Math.random() * colors.length)]
            }
          },
          emphasis: { scale: 1.1, textStyle: { shadowBlur: 10, shadowColor: '#333' } },
          data: this.wordData
        }]
      })
    }
  }
}
</script>

<style scoped>
.detail-container {
  padding: 8px;
  max-width: 1400px;
  margin: 0 auto;
}
.back-btn {
  margin-bottom: 20px;
}
.info-card {
  border-radius: var(--border-radius-xl, 28px);
  margin-bottom: 24px;
  background: linear-gradient(145deg, #ffffff, #f8fafc);
  position: relative;
  overflow: hidden;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.card-header h2 {
  font-size: 1.8rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  margin: 0;
}
.rating-badge {
  background: linear-gradient(135deg, #f093fb, #f5576c);
  padding: 6px 16px;
  border-radius: 40px;
  color: white;
  font-weight: bold;
}
.rating-badge .star {
  font-size: 1.1rem;
}
.card-decoration {
  position: absolute;
  bottom: 10px;
  right: 20px;
  font-size: 4rem;
  opacity: 0.1;
  pointer-events: none;
}
.controls-card {
  background: white;
  border-radius: var(--border-radius-xl, 28px);
  padding: 20px 28px;
  margin-bottom: 24px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.05);
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 32px;
}
.control-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.control-group label {
  font-weight: 600;
  font-size: 0.85rem;
  color: #2c3e50;
}
.hint-text {
  margin-left: auto;
  font-size: 0.8rem;
  color: #7f8c8d;
  background: #ecf0f1;
  padding: 6px 12px;
  border-radius: 40px;
}
.chart-row {
  margin-bottom: 24px;
}
.chart-card {
  border-radius: var(--border-radius-xl, 28px);
  height: 100%;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  background: white;
}
.chart-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 32px rgba(0,0,0,0.1);
}
.card-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1e2a36;
  padding-bottom: 12px;
  margin-bottom: 16px;
  border-bottom: 2px solid #eaeef2;
  position: relative;
}
.card-title::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 60px;
  height: 3px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 3px;
}
.full-width {
  width: 100%;
}
</style>