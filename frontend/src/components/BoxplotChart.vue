<template>
  <div ref="chart" style="width: 100%; height: 450px"></div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'BoxplotChart',
  props: {
    data: {
      type: Object,
      default: () => ({ categories: [], series: [] })
    }
  },
  watch: {
    data: { deep: true, handler() { this.renderChart() } }
  },
  mounted() {
    this.renderChart()
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize)
  },
  methods: {
    handleResize() {
      const chart = echarts.getInstanceByDom(this.$refs.chart)
      if (chart) chart.resize()
    },
    renderChart() {
      if (!this.$refs.chart) return
      const old = echarts.getInstanceByDom(this.$refs.chart)
      if (old) old.dispose()
      const chart = echarts.init(this.$refs.chart)

      if (!this.data.categories || !this.data.categories.length || !this.data.series || !this.data.series.length) {
        chart.setOption({ 
          title: { text: '暂无数据', left: 'center', top: 'center' }, 
          series: [] 
        })
        return
      }

      // 1. 提取唯一店名（去重）
      const allShops = this.data.categories.map(cat => cat.split('-')[0])
      const uniqueShops = [...new Set(allShops)] // 去重，得到 ["纯再餐厅(光明广场店)", "焖胜品味(珠江新城店)"]

      // 2. 计算每个店名对应的x轴位置（用于对齐箱线图）
      const shopIndexMap = {}
      uniqueShops.forEach((shop, idx) => {
        shopIndexMap[shop] = idx
      })

      const legendData = this.data.series.map(s => s.name)
      const seriesList = []

      this.data.series.forEach((ser) => {
        // 3. 重新组织数据：按店名分组，保持箱线图位置不变
        const newData = this.data.categories.map((cat, i) => {
          const shop = cat.split('-')[0]
          return {
            name: shop,
            value: ser.data[i], // 保留原箱线数据
            itemStyle: ser.itemStyle
          }
        })

        seriesList.push({
          name: ser.name,
          type: 'boxplot',
          data: newData,
          boxWidth: 20,
          itemStyle: {
            color: ser.color,
            borderColor: '#2c3e50',
            borderWidth: 1,
            outlier: {
              color: ser.color,
              borderWidth: 0,
              symbolSize: 8,
              symbol: 'circle'
            }
          },
          tooltip: {
            formatter: params => `${ser.name}<br/>${params.name}<br/>最小值: ${params.value[0]}<br/>下四分位: ${params.value[1]}<br/>中位数: ${params.value[2]}<br/>上四分位: ${params.value[3]}<br/>最大值: ${params.value[4]}`,
            appendToBody: true,
            position: function(point, params, dom, rect, size) {
              let y = point[1] + 15
              if (y + size.contentSize[1] > window.innerHeight) {
                y = point[1] - size.contentSize[1] - 10
              }
              return [point[0] + 10, y]
            }
          }
        })
      })

      const option = {
        title: { 
          text: '各餐厅评分维度分布对比', 
          left: 'center',
          subtext: '箱体表示中间50%评分，横线为中位数，红:综合,绿:口味,蓝:环境,橙:服务'
        },
        tooltip: { trigger: 'item' },
        legend: { 
          data: legendData, 
          left: 'left' 
        },
        xAxis: {
          type: 'category',
          data: uniqueShops, // 只显示唯一店名
          name: '餐厅',
          axisLabel: { 
            rotate: 45, 
            fontSize: 10, 
            interval: 0 
          }
        },
        yAxis: { 
          type: 'value', 
          name: '评分（1-5）', 
          min: 1, 
          max: 5, 
          axisLabel: { formatter: (v) => v.toFixed(1) } 
        },
        series: seriesList,
        grid: { 
          containLabel: true, 
          top: 100 
        }
      }
      
      chart.setOption(option)
    }
  }
}
</script>