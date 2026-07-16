<template>
  <div class="overview">
    <!-- 统计卡片 -->
    <el-row :gutter="24">
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-number">{{ stats.total_restaurants }}</div>
          <div>餐厅总数</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-number">{{ stats.total_reviews }}</div>
          <div>评论总数</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card stat-card-3" shadow="hover">
          <div class="stat-number">{{ stats.avg_star ? stats.avg_star.toFixed(2) : '0' }}</div>
          <div>平均星级</div>
          <div class="stat-icon">⭐</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 时间范围选择器 -->
    <div class="controls-card">
      <div class="control-group">
        <label>📅 时间范围</label>
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
      <div class="hint-text">💡 改变时间范围 → 条形图、环形图、词云自动更新</div>
    </div>

    <!-- 图表行 -->
    <el-row :gutter="24" class="chart-row">
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="card-title">🏆 评论数量 TOP50 餐厅</div>
          <BarChart :data="barData" />
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="card-title">⭐ 餐厅星级分布（时间范围内）</div>
          <RingChart :data="ringData" />
        </div>
      </el-col>
    </el-row>

    <!-- 词云行 -->
    <el-row :gutter="24" class="chart-row">
      <el-col :span="24">
        <div class="chart-card full-width">
          <div class="card-title">☁️ 评论关键词词云</div>
          <WordCloud :data="wordData" />
        </div>
      </el-col>
    </el-row>

    <!-- 评论趋势折线图 -->
    <el-card class="chart-card">
      <div ref="trendChart" style="height: 400px; width: 100%;"></div>
    </el-card>

    <!-- 相关性热力图 + 散点图 -->
    <el-row :gutter="24" class="chart-row">
      <el-col :span="12">
        <div class="chart-card">
          <div class="card-title">📊 评分维度相关性热力图</div>
          <HeatmapChart :fields="corrFields" :data="corrData" />
        </div>
      </el-col>
      <el-col :span="12">
        <div class="chart-card">
          <div class="card-title">💰 人均消费 vs 星级（气泡大小=评论数）</div>
          <ScatterChart :data="scatterData" />
        </div>
      </el-col>
    </el-row>

    <!-- 新增：情感分析 -->
    <el-row :gutter="24" class="chart-row">
      <el-col :span="12">
        <div class="chart-card">
          <div class="card-title">😊 情感分布</div>
          <div ref="sentimentPieChart" style="width: 100%; height: 300px;"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="chart-card">
          <div class="card-title">📈 情感趋势</div>
          <div ref="sentimentTrendChart" style="width: 100%; height: 300px;"></div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { 
  getOverviewStats, 
  getReviewTrend, 
  getCommentCount, 
  getStarRatio, 
  getWordCloud, 
  getCorrelation, 
  getScatter,
  getSentimentData
} from '@/api'
import BarChart from '@/components/BarChart.vue'
import RingChart from '@/components/RingChart.vue'
import WordCloud from '@/components/WordCloud.vue'
import HeatmapChart from '@/components/HeatmapChart.vue'
import ScatterChart from '@/components/ScatterChart.vue'
import * as echarts from 'echarts'

export default {
  components: { BarChart, RingChart, WordCloud, HeatmapChart, ScatterChart },
  data() {
    return {
      dateRange: ['20150101', '20171031'],
      stats: { total_restaurants: 0, total_reviews: 0, avg_star: 0 },
      barData: [],
      ringData: [],
      wordData: [],
      trendData: [],
      corrFields: [],
      corrData: [],
      scatterData: [],
      sentimentData: { summary: { positive: 0, neutral: 0, negative: 0 }, trend: [] }
    }
  },
  async mounted() {
    await this.loadStats()
    await this.loadTrend()
    await this.loadCharts()
    await this.loadCorrelation()
    await this.loadScatter()
    await this.loadSentiment()
  },
  methods: {
    async loadStats() {
      const res = await getOverviewStats()
      this.stats = res.data
    },
    async loadTrend() {
      const res = await getReviewTrend()
      this.trendData = res.data
      this.renderTrend()
    },
    async loadCharts() {
      await this.loadBarChart()
      await this.loadRingChart()
      await this.loadWordCloud()
    },
    async loadBarChart() {
      const params = {
        start_date: this.dateRange[0],
        end_date: this.dateRange[1],
        top_n: 50
      }
      const res = await getCommentCount(params)
      this.barData = res.data
    },
    async loadRingChart() {
      const params = {
        restaurant_name: '全部',
        start_date: this.dateRange[0],
        end_date: this.dateRange[1]
      }
      const res = await getStarRatio(params)
      this.ringData = res.data
    },
    async loadWordCloud() {
      const params = {
        restaurant_name: '全部',
        start_date: this.dateRange[0],
        end_date: this.dateRange[1]
      }
      const res = await getWordCloud(params)
      this.wordData = res.data
    },
    async loadCorrelation() {
      const res = await getCorrelation()
      this.corrFields = res.data.fields
      this.corrData = res.data.data
    },
    async loadScatter() {
      const res = await getScatter()
      this.scatterData = res.data
    },
    async loadSentiment() {
      const params = {
        start: this.dateRange[0],
        end: this.dateRange[1]
      }
      try {
        const res = await getSentimentData(params)
        this.sentimentData = res.data
        this.renderSentimentCharts()
      } catch (error) {
        console.warn('情感数据加载失败:', error)
      }
    },
    renderSentimentCharts() {
      const { summary, trend } = this.sentimentData

      // 情感分布 - 环形图
      const pieChart = echarts.init(this.$refs.sentimentPieChart)
      pieChart.setOption({
        tooltip: { trigger: 'item' },
        legend: { orient: 'vertical', left: 'left' },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: true,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: { show: true, formatter: '{b}\n{d}%' },
          data: [
            { value: summary.positive || 0, name: '正面', itemStyle: { color: '#91cc75' } },
            { value: summary.neutral || 0, name: '中性', itemStyle: { color: '#fac858' } },
            { value: summary.negative || 0, name: '负面', itemStyle: { color: '#ee6666' } }
          ],
          emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.5)' } }
        }]
      })

      // 情感趋势 - 折线图
      const trendChart = echarts.init(this.$refs.sentimentTrendChart)
      if (trend && trend.length) {
        const months = trend.map(d => d.month)
        trendChart.setOption({
          tooltip: { trigger: 'axis' },
          legend: { data: ['正面', '中性', '负面'] },
          grid: {
            containLabel: true,
            left: 40,
            right: 20,
            top: 30,
            bottom: 30
          },
          xAxis: {
            type: 'category',
            data: months,
            boundaryGap: false
          },
          yAxis: {
            type: 'value',
            min: 0,
            splitLine: { show: true }
          },
          series: [
            {
              name: '正面',
              type: 'line',
              data: trend.map(d => d.positive),
              smooth: true,
              symbol: 'circle',
              symbolSize: 6,
              lineStyle: { width: 2 },
              areaStyle: { opacity: 0.1 },
              itemStyle: { color: '#91cc75' }
            },
            {
              name: '中性',
              type: 'line',
              data: trend.map(d => d.neutral),
              smooth: true,
              symbol: 'diamond',
              symbolSize: 6,
              lineStyle: { width: 2 },
              areaStyle: { opacity: 0.1 },
              itemStyle: { color: '#fac858' }
            },
            {
              name: '负面',
              type: 'line',
              data: trend.map(d => d.negative),
              smooth: true,
              symbol: 'triangle',
              symbolSize: 6,
              lineStyle: { width: 2 },
              areaStyle: { opacity: 0.1 },
              itemStyle: { color: '#ee6666' }
            }
          ]
        })
      } else {
        trendChart.setOption({
          title: { text: '暂无趋势数据', left: 'center', top: 'center' }
        })
      }
    },
    onDateChange() {
      this.loadBarChart()
      this.loadRingChart()
      this.loadWordCloud()
      this.loadSentiment()
    },
    renderTrend() {
      const chart = echarts.init(this.$refs.trendChart)
      chart.setOption({
        tooltip: { trigger: 'axis' },
        grid: {
          containLabel: true,
          left: 50,
          right: 20,
          top: 30,
          bottom: 30
        },
        xAxis: { type: 'category', data: this.trendData.map(d => d.year_month), name: '年月', boundaryGap: false },
        yAxis: { type: 'value', name: '评论数量', min: 0 },
        series: [{
          type: 'line',
          data: this.trendData.map(d => d.count),
          smooth: true,
          areaStyle: { opacity: 0.3 },
          lineStyle: { width: 3, color: '#5470c6' }
        }]
      })
    }
  }
}
</script>

<style scoped>
.overview {
  padding: 8px;
}
.controls-card {
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(8px);
  border-radius: 28px;
  padding: 20px 28px;
  margin: 24px 0 32px;
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
.stat-card {
  text-align: center;
  font-size: 1.2rem;
  background: linear-gradient(145deg, #ffffff, #f9fafb);
  border-radius: 32px;
}
.stat-number {
  font-size: 2.5rem;
  font-weight: bold;
  color: #3b82f6;
  margin-bottom: 8px;
}
.chart-row {
  margin-bottom: 32px;
}
.chart-card {
  background: white;
  border-radius: 28px;
  padding: 20px;
  box-shadow: 0 12px 28px rgba(0,0,0,0.08);
  transition: transform 0.2s ease;
  height: 100%;
}
.chart-card:hover {
  transform: translateY(-4px);
}
.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e2a36;
  padding-bottom: 12px;
  border-bottom: 2px solid #eaeef2;
  margin-bottom: 16px;
}
.full-width {
  width: 100%;
}
</style>