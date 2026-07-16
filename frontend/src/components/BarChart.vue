<template>
  <div ref="chart" style="width: 100%; height: 550px"></div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'BarChart',
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
      const types = this.data.map(item => item.name)
      const counts = this.data.map(item => item.count)

      const option = {
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}<br/>评论数: {c}' },
        grid: {
          left: '25%',      // 为左侧垂直滚动条和长标签留出足够空间
          right: '5%',
          top: 20,
          bottom: '12%',
          containLabel: true
        },
        xAxis: {
          type: 'value',
          name: '评论数量',
          nameLocation: 'middle',
          nameGap: 35,
          nameTextStyle: { fontSize: 12, fontWeight: 'bold' }
        },
        yAxis: {
          type: 'category',
          data: types,
          name: '餐厅名称',
          nameLocation: 'middle',
          nameGap: 200,          // 增加名称与轴线的距离，避免与滚动条重叠
          nameRotate: 90, 
          nameTextStyle: { fontSize: 12, fontWeight: 'bold' },
          axisLabel: { fontSize: 11, fontWeight: 500, rotate: 0 },
          axisLine: { show: false },
          axisTick: { show: false },
          inverse: true          // 评论数多的在上方
        },
        // 垂直滚动条（放置在图表左侧并居中）
        dataZoom: [{
          type: 'slider',
          yAxisIndex: 0,          // 作用于 y 轴
          show: true,
          orient: 'vertical',      // 垂直方向
          left: '2%',              // 距离左侧 2% 的位置（可根据需要微调）
          top: '20%',              // 垂直居中 (上下各留 20%)
          bottom: '20%',
          filterMode: 'filter',
          handleSize: 30,
          width: 12,               // 滚动条宽度
          borderWidth: 0,
          fillerColor: 'rgba(84,112,198,0.2)',
          backgroundColor: '#f0f0f0'
        }],
        series: [{
          type: 'bar',
          data: counts,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#5470c6' },
              { offset: 1, color: '#91cc75' }
            ]),
            borderRadius: [0, 8, 8, 0]
          },
          label: { show: true, position: 'right', fontWeight: 'bold', fontSize: 11 }
        }]
      }
      chart.setOption(option)
    }
  }
}
</script>