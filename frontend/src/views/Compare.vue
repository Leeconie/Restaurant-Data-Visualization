<template>
  <div class="compare">
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
      <div class="hint-text">💡 改变时间范围 → 所有图表自动更新</div>
    </div>

    <!-- 餐厅选择 + 确认按钮 -->
    <div class="selector">
      <el-select
        v-model="selectedIds"
        multiple
        filterable
        placeholder="选择要对比的餐厅（至少2家）"
        clearable
        style="flex: 1;"
      >
        <el-option
          v-for="r in allRestaurants"
          :key="r.item_id"
          :label="r.name"
          :value="r.item_id"
        />
      </el-select>
      <el-button type="primary" @click="fetchAllData" :loading="loading" style="margin-left: 16px;">
        {{ loading ? '加载中...' : '确认对比' }}
      </el-button>
    </div>

    <!-- 提示信息 -->
    <div v-if="selectedIds.length < 2 && !loading" class="empty-hint">
      ⚠️ 请至少选择两家餐厅，然后点击“确认对比”
    </div>

    <!-- 雷达图 + 总评论数条形图 -->
    <el-row :gutter="24" class="chart-row" v-if="compareResult.length > 0">
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <div class="card-title">📊 评分维度雷达图</div>
          <div ref="radarContainer" style="height: 450px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <div class="card-title">📊 总评论数对比</div>
          <div ref="barContainer" style="height: 450px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 月度趋势折线图 -->
    <el-row :gutter="24" class="chart-row" v-if="trendData.length > 0">
      <el-col :span="24">
        <el-card class="chart-card full-width" shadow="hover">
          <div class="card-title">📈 评论数量月度趋势</div>
          <div ref="lineContainer" style="height: 450px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 多维度箱线图 -->
    <el-row :gutter="24" class="chart-row" v-if="groupBoxplotData.categories && groupBoxplotData.categories.length">
      <el-col :span="24">
        <el-card class="chart-card full-width" shadow="hover">
          <div class="card-title">📊 评分维度分布对比（箱线图）</div>
          <div class="boxplot-note">箱体表示中间50%评分，横线为中位数，红:综合,绿:口味,蓝:环境,橙:服务</div>
          <BoxplotChart :data="groupBoxplotData" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { getRestaurantRanking, getCompareData, getCompareTrend, getCompareBoxplot } from '@/api'
import BoxplotChart from '@/components/BoxplotChart.vue'
import * as echarts from 'echarts'

export default {
  components: { BoxplotChart },
  data() {
    return {
      dateRange: ['20150101', '20171031'],
      allRestaurants: [],
      selectedIds: [],
      loading: false,
      compareResult: [],
      trendData: [],
      groupBoxplotData: { categories: [], series: [] }
    }
  },
  async mounted() {
    await this.loadRestaurants()
  },
  methods: {
    async loadRestaurants() {
      const res = await getRestaurantRanking({ sort_by: 'review_count' })
      this.allRestaurants = res.data
    },
    async fetchAllData() {
      if (this.selectedIds.length < 2) {
        this.$message.warning('请至少选择两家餐厅')
        return
      }
      this.loading = true
      try {
        await Promise.all([
          this.fetchRadarData(),
          this.fetchTrendData(),
          this.fetchBoxplotData()
        ])
      } catch (err) {
        console.error(err)
        this.$message.error('加载数据失败')
      } finally {
        this.loading = false
      }
    },
    async fetchRadarData() {
      const params = {
        ids: this.selectedIds,
        start_date: this.dateRange[0],
        end_date: this.dateRange[1]
      }
      const res = await getCompareData(params)
      this.compareResult = res.data
      this.$nextTick(() => this.renderRadar())
    },
    async fetchTrendData() {
      const params = {
        ids: this.selectedIds,
        start_date: this.dateRange[0],
        end_date: this.dateRange[1]
      }
      const res = await getCompareTrend(params)
      this.trendData = res.data.monthly
      // 确保 totalData 存在后再渲染条形图
      if (res.data.total && res.data.total.length) {
        this.$nextTick(() => {
          this.renderBarChart(res.data.total)
          this.renderLineChart()
        })
      } else {
        console.warn('totalData 为空，条形图暂不渲染')
      }
    },
    async fetchBoxplotData() {
      const params = {
        ids: this.selectedIds,
        start_date: this.dateRange[0],
        end_date: this.dateRange[1]
      }
      const res = await getCompareBoxplot(params)

      const categories = []
      const seriesMap = {
        rating_score: { name: '综合评分', data: [], color: '#ee6666' },
        score_taste: { name: '口味', data: [], color: '#91cc75' },
        score_environment: { name: '环境', data: [], color: '#5470c6' },
        score_service: { name: '服务', data: [], color: '#fac858' }
      }

      for (let id of this.selectedIds) {
        const item = res.data[id]
        if (!item) continue
        const baseName = item.name
        const dimOrder = ['rating_score', 'score_taste', 'score_environment', 'score_service']
        for (let dim of dimOrder) {
          const dimData = item[dim]
          const label = `${baseName}-${seriesMap[dim].name}`
          categories.push(label)
          if (dimData && dimData.box_data) {
            seriesMap[dim].data.push(dimData.box_data)
          } else {
            seriesMap[dim].data.push([0, 0, 0, 0, 0])
          }
        }
      }

      const series = Object.values(seriesMap).map(s => ({
        name: s.name,
        data: s.data,
        color: s.color
      }))

      this.groupBoxplotData = { categories, series }
    },
    onDateChange() {
      if (this.selectedIds.length >= 2) {
        this.fetchAllData()
      }
    },
    renderRadar() {
      if (!this.$refs.radarContainer) return
      const old = echarts.getInstanceByDom(this.$refs.radarContainer)
      if (old) old.dispose()
      const chart = echarts.init(this.$refs.radarContainer)
      const maxReviews = Math.max(...this.compareResult.map(r => r.review_count || 0), 1)
      const option = {
        title: { text: '评分维度对比', left: 'center' },
        tooltip: {},
        radar: {
          indicator: [
            { name: '口味', max: 5 },
            { name: '环境', max: 5 },
            { name: '服务', max: 5 },
            { name: '综合星级', max: 5 },
            { name: '评论数量', max: maxReviews }
          ]
        },
        series: [{
          type: 'radar',
          data: this.compareResult.map(r => ({
            value: [
              r.score_taste || 0,
              r.score_environment || 0,
              r.score_service || 0,
              r.star || 0,
              r.review_count || 0
            ],
            name: r.name
          })),
          areaStyle: { opacity: 0.1 }
        }]
      }
      chart.setOption(option)
    },
    renderBarChart(totalData) {
      // 增加容器存在性检查和重试机制
      if (!this.$refs.barContainer) {
        console.warn('barContainer 不存在，延迟重试')
        setTimeout(() => this.renderBarChart(totalData), 100)
        return
      }
      if (!totalData || totalData.length === 0) {
        console.warn('totalData 为空，跳过条形图渲染')
        return
      }
      const old = echarts.getInstanceByDom(this.$refs.barContainer)
      if (old) old.dispose()
      const chart = echarts.init(this.$refs.barContainer)
      const names = totalData.map(item => item.name)
      const counts = totalData.map(item => item.count)
      // 多色配色数组，自动循环取用
      const colorList = ['#5470c6','#ee6666','#91cc75','#fac858','#73c0de','#3ba272','#fc8452','#9a60b4']
      const barData = counts.map((val, idx) => ({
        value: val,
        itemStyle: {
          color: colorList[idx % colorList.length],
          borderRadius: [8, 8, 0, 0]
        }
      }))
      const option = {
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}<br/>评论数: {c}' },
        xAxis: { type: 'category', data: names, name: '餐厅', axisLabel: { rotate: 30 } },
        yAxis: { type: 'value', name: '评论数量' },
        series: [{
          type: 'bar',
          data: barData,
          label: { show: true, position: 'top' }
        }]
      }
      chart.setOption(option)
    },
    renderLineChart() {
      if (!this.$refs.lineContainer) return
      const old = echarts.getInstanceByDom(this.$refs.lineContainer)
      if (old) old.dispose()
      const chart = echarts.init(this.$refs.lineContainer)
      const months = [...new Set(this.trendData.map(d => d.year_month))].sort()
      const seriesMap = new Map()
      this.trendData.forEach(item => {
        if (!seriesMap.has(item.name)) {
          seriesMap.set(item.name, [])
        }
        seriesMap.get(item.name).push({ month: item.year_month, count: item.count })
      })
      const series = []
      for (let [name, data] of seriesMap.entries()) {
        const fullData = months.map(month => {
          const found = data.find(d => d.month === month)
          return found ? found.count : 0
        })
        series.push({
          name: name,
          type: 'line',
          data: fullData,
          smooth: true,
          symbol: 'circle',
          symbolSize: 6
        })
      }
      const option = {
        title: { text: '月度评论趋势', left: 'center' },
        tooltip: { trigger: 'axis' },
        legend: { top: 30 },
        xAxis: { type: 'category', data: months, name: '年月' },
        yAxis: { type: 'value', name: '评论数' },
        series: series
      }
      chart.setOption(option)
    }
  }
}
</script>

<style scoped>
.compare { padding: 16px; }
.controls-card { background: white; border-radius: 28px; padding: 20px 28px; margin-bottom: 24px; display: flex; flex-wrap: wrap; align-items: flex-end; gap: 32px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.control-group { display: flex; flex-direction: column; gap: 8px; }
.control-group label { font-weight: 600; font-size: 0.85rem; color: #2c3e50; }
.hint-text { margin-left: auto; font-size: 0.8rem; color: #7f8c8d; background: #ecf0f1; padding: 6px 12px; border-radius: 40px; }
.selector { background: white; padding: 20px; border-radius: 28px; display: flex; align-items: center; flex-wrap: wrap; margin-bottom: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.empty-hint { text-align: center; margin-top: 50px; color: #999; }
.chart-row { margin-bottom: 24px; }
.chart-card { border-radius: 28px; height: 100%; }
.card-title { font-size: 1.2rem; font-weight: 600; color: #1e2a36; padding-bottom: 12px; margin-bottom: 16px; border-bottom: 2px solid #eaeef2; }
.full-width { width: 100%; }
.boxplot-note { font-size: 0.8rem; color: #7f8c8d; margin-bottom: 16px; text-align: center; }
</style>