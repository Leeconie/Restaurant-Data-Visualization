<template>
  <div ref="chart" style="width: 100%; height: 400px"></div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'HeatmapChart',
  props: {
    fields: Array,
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

      // 转换数据格式为 [xIndex, yIndex, value]
      const seriesData = []
      for (let i = 0; i < this.fields.length; i++) {
        for (let j = 0; j < this.fields.length; j++) {
          seriesData.push([j, i, this.data[i][j]])
        }
      }

      const option = {
        title: { text: '评分维度相关性热力图', left: 'center' },
        tooltip: {
          trigger: 'item',
          // 自定义提示框：只显示维度名称和相关系数
          formatter: function(params) {
            const xIdx = params.data[0]
            const yIdx = params.data[1]
            const value = params.data[2]
            const xName = this.fields[xIdx]
            const yName = this.fields[yIdx]
            return `${xName} vs ${yName}<br/>相关系数: ${value}`
          }.bind(this)
        },
        xAxis: {
          type: 'category',
          data: this.fields,
          name: '维度',
          axisLabel: { rotate: 30 }
        },
        yAxis: {
          type: 'category',
          data: this.fields,
          name: '维度'
        },
        visualMap: {
          min: -1,
          max: 1,
          calculable: true,
          inRange: { color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026'] },
          outOfRange: { color: ['#999'] }
        },
        series: [{
          type: 'heatmap',
          data: seriesData,
          label: {
            show: true,
            formatter: function(params) {
              // 只显示相关系数值，保留4位小数
              return params.data[2].toFixed(4)
            }
          },
          emphasis: { itemStyle: { shadowBlur: 10 } }
        }]
      }
      chart.setOption(option)
    }
  }
}
</script>