<template>
  <div ref="chart" style="width: 100%; height: 450px"></div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'ScatterChart',
  props: {
    data: Array
  },
  watch: {
    data: { deep: true, handler() { this.renderChart() } }
  },
  mounted() {
    this.renderChart()
  },
  methods: {
    renderChart() {
      if (!this.$refs.chart) return
      let chart = echarts.init(this.$refs.chart)

      const scatterData = this.data.map(item => ({
        value: [item.cost, item.star, item.review_count],
        name: item.name
      }))

      const option = {
        title: { text: '人均消费 vs 星级（气泡大小=评论数）', left: 'center' },
        tooltip: {
          trigger: 'item',
          formatter: function(params) {
            const data = params.data
            const name = data.name
            const cost = data.value[0]
            const star = data.value[1]
            const reviewCount = data.value[2]
            return `${name}<br/>人均消费: ${cost !== undefined && cost !== null ? cost.toFixed(2) : '—'} 元<br/>星级: ${star !== undefined && star !== null ? star.toFixed(2) : '—'}<br/>评论数: ${reviewCount || 0}`
          }
        },
        xAxis: { 
          type: 'value', 
          name: '人均消费 (元)', 
          min: 0, 
          max: 2400,        // 取消300限制，改为2400
          nameLocation: 'middle', 
          nameGap: 30 
        },
        yAxis: { type: 'value', name: '星级', min: 3, max: 5 },
        // 添加横轴滚动条（dataZoom）
        dataZoom: [{
          type: 'slider',
          xAxisIndex: 0,
          start: 0,
          end: 100,
          bottom: 10,
          handleSize: 20,
          zoomLock: false
        }],
        series: [{
          type: 'scatter',
          data: scatterData,
          symbolSize: function(val) {
            return Math.min(40, 12 + Math.sqrt(val[2]) / 10)
          },
          itemStyle: { color: '#5470c6', opacity: 0.7 },
          label: { show: false },
          emphasis: { scale: 1.2 }
        }]
      }
      chart.setOption(option)
    }
  }
}
</script>