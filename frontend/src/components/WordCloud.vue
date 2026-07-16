<template>
  <div ref="chart" style="width: 100%; height: 520px"></div>
</template>

<script>
import * as echarts from 'echarts'
import 'echarts-wordcloud'

export default {
  name: 'WordCloud',
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
      const option = {
        series: [{
          type: 'wordCloud',
          shape: 'circle',
          sizeRange: [30,100],
          rotationRange: [-45, 90],
          gridSize: 10,
          layoutAnimation: true,
          drawOutOfBound: false,
          textStyle: {
            fontFamily: 'sans-serif',
            fontWeight: 'bold',
            color: function () {
              const colors = ['#5470c6', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc']
              return colors[Math.floor(Math.random() * colors.length)]
            }
          },
          emphasis: { scale: 1.1 },
          data: this.data
        }]
      }
      chart.setOption(option)
    }
  }
}
</script>