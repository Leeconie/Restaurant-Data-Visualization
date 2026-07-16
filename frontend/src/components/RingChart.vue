<template>
  <div ref="chart" style="width: 100%; height: 420px"></div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'RingChart',
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
      const total = this.data.reduce((sum, item) => sum + item.value, 0)
      const option = {
        tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c}家)' },
        legend: { orient: 'vertical', left: 'left', data: this.data.map(d => `${d.star}星`) },
        series: [{
          type: 'pie',
          radius: ['45%', '70%'],
          avoidLabelOverlap: false,
          label: { show: true, formatter: '{b}: {d}%', position: 'outside' },
          emphasis: { scale: true, label: { show: true } },
          data: this.data.map(item => ({ name: `${item.star}星`, value: item.value })),
          color: ['#ff6b6b', '#feca57', '#48dbfb', '#1dd1a1', '#5f27cd', '#ff9ff3']
        }],
        graphic: [{
          type: 'text',
          left: 'center',
          top: 'center',
          style: { text: `${total}家`, fill: '#333', fontSize: 20, fontWeight: 'bold' },
          z: 100
        }]
      }
      chart.setOption(option)
    }
  }
}
</script>