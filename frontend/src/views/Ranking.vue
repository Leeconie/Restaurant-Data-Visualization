<template>
  <div class="ranking">
    <div class="toolbar">
      <el-select v-model="sortBy" @change="loadRanking" placeholder="排序依据">
        <el-option label="评论数" value="review_count" />
        <el-option label="星级" value="star" />
        <el-option label="人均消费" value="cost" />
      </el-select>

      <!-- 搜索框 + 搜索按钮 -->
      <div class="search-wrapper">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索餐厅名称"
          clearable
          style="width: 200px;"
          @keyup.enter="doSearch"
        />
        <el-button type="primary" @click="doSearch">搜索</el-button>
      </div>

      <!-- 快速标签（多选组合） -->
      <div class="quick-tags">
        <el-button
          size="small"
          :type="activeFilters.starHigh ? 'primary' : 'default'"
          @click="toggleFilter('starHigh')"
        >
          4.5星以上
        </el-button>
        <el-button
          size="small"
          :type="activeFilters.costLow ? 'primary' : 'default'"
          @click="toggleFilter('costLow')"
        >
          人均<100
        </el-button>
        <el-button
          size="small"
          :type="activeFilters.reviewHigh ? 'primary' : 'default'"
          @click="toggleFilter('reviewHigh')"
        >
          评论>1000
        </el-button>
      </div>

      <!-- 高级筛选按钮 -->
      <el-button type="primary" plain @click="openAdvancedFilter">
        🔍 高级筛选
      </el-button>
    </div>

    <!-- 高级筛选弹窗 -->
    <el-dialog
      title="高级筛选"
      v-model="showAdvancedFilter"
      width="400px"
      destroy-on-close
      @opened="initTempFilters"
    >
      <div class="filter-section">
        <div class="filter-label">星级</div>
        <el-checkbox-group v-model="tempStars">
          <el-checkbox label="3">3星</el-checkbox>
          <el-checkbox label="4">4星</el-checkbox>
          <el-checkbox label="5">5星</el-checkbox>
        </el-checkbox-group>
        <div class="filter-note">* 勾选多个条件时取并集（满足任一星级区间）</div>
      </div>

      <div class="filter-section">
        <div class="filter-label">人均消费（元）</div>
        <div class="cost-range">
          <el-input-number
            v-model="tempMinCost"
            :min="0"
            :step="10"
            placeholder="最低"
            controls-position="right"
            style="width: 120px;"
          />
          <span> - </span>
          <el-input-number
            v-model="tempMaxCost"
            :min="0"
            :step="10"
            placeholder="最高"
            controls-position="right"
            style="width: 120px;"
          />
        </div>
      </div>

      <template #footer>
        <el-button @click="resetTempFilters">重置</el-button>
        <el-button type="primary" @click="applyAdvancedFilter">应用筛选</el-button>
      </template>
    </el-dialog>

    <el-table :data="displayList" stripe style="width: 100%; margin-top: 20px;">
      <el-table-column type="index" label="排名" width="80" />
      <el-table-column prop="name" label="餐厅名称" min-width="180" />
      <el-table-column prop="review_count" label="评论数" sortable />
      <el-table-column prop="star" label="星级" sortable>
        <template #default="{ row }">{{ row.star ? row.star.toFixed(2) : '—' }}</template>
      </el-table-column>
      <el-table-column prop="cost" label="人均消费 (¥)" sortable>
        <template #default="{ row }">{{ row.cost ? row.cost.toFixed(2) : '—' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button type="primary" link @click="goDetail(row.item_id)">查看详情</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import { getRestaurantRanking } from '@/api'

export default {
  data() {
    return {
      sortBy: 'review_count',
      searchKeyword: '',          // 搜索关键词
      activeFilters: {            // 快速标签状态
        starHigh: false,          // 4.5星以上
        costLow: false,           // 人均<100
        reviewHigh: false         // 评论>1000
      },
      fullList: [],               // 原始数据（排序后）
      displayList: [],            // 最终显示（经过所有筛选）

      // 高级筛选弹窗
      showAdvancedFilter: false,
      tempStars: [],              // 临时星级选择
      tempMinCost: null,
      tempMaxCost: null,
      // 实际生效的高级筛选条件
      advancedStars: [],
      advancedMinCost: null,
      advancedMaxCost: null
    }
  },
  mounted() {
    this.loadRanking()
  },
  methods: {
    async loadRanking() {
      const res = await getRestaurantRanking({ sort_by: this.sortBy })
      this.fullList = res.data
      this.filterRanking()
    },
    // 综合筛选（包含搜索、快速标签、高级筛选）
    filterRanking() {
      let filtered = [...this.fullList]

      // 1. 搜索关键词（餐厅名称包含）
      if (this.searchKeyword) {
        filtered = filtered.filter(item => item.name.includes(this.searchKeyword))
      }

      // 2. 快速标签
      if (this.activeFilters.starHigh) {
        filtered = filtered.filter(item => item.star !== null && item.star >= 4.5)
      }
      if (this.activeFilters.costLow) {
        filtered = filtered.filter(item => item.cost !== null && item.cost < 100)
      }
      if (this.activeFilters.reviewHigh) {
        filtered = filtered.filter(item => item.review_count !== null && item.review_count > 1000)
      }

      // 3. 高级筛选：星级（多选并集，支持区间）
      if (this.advancedStars.length > 0) {
        filtered = filtered.filter(item => {
          const star = item.star
          if (star === null) return false
          let match = false
          // 3星区间：3 <= star < 4
          if (this.advancedStars.includes('3') && star >= 3 && star < 4) match = true
          // 4星区间：4 <= star < 5
          if (this.advancedStars.includes('4') && star >= 4 && star < 5) match = true
          // 5星：star === 5
          if (this.advancedStars.includes('5') && star === 5) match = true
          return match
        })
      }

      // 4. 高级筛选：人均消费区间
      if (this.advancedMinCost !== null) {
        filtered = filtered.filter(item => item.cost !== null && item.cost >= this.advancedMinCost)
      }
      if (this.advancedMaxCost !== null) {
        filtered = filtered.filter(item => item.cost !== null && item.cost <= this.advancedMaxCost)
      }

      this.displayList = filtered
    },

    // 搜索按钮触发
    doSearch() {
      this.filterRanking()
    },

    // 快速标签切换
    toggleFilter(filterName) {
      this.activeFilters[filterName] = !this.activeFilters[filterName]
      this.filterRanking()
    },

    // 打开高级筛选弹窗
    openAdvancedFilter() {
      this.showAdvancedFilter = true
    },
    // 弹窗打开时，用当前有效高级筛选条件初始化临时变量
    initTempFilters() {
      this.tempStars = [...this.advancedStars]
      this.tempMinCost = this.advancedMinCost
      this.tempMaxCost = this.advancedMaxCost
    },
    // 重置临时筛选条件（弹窗内）
    resetTempFilters() {
      this.tempStars = []
      this.tempMinCost = null
      this.tempMaxCost = null
    },
    // 应用高级筛选
    applyAdvancedFilter() {
      this.advancedStars = [...this.tempStars]
      this.advancedMinCost = this.tempMinCost
      this.advancedMaxCost = this.tempMaxCost
      this.showAdvancedFilter = false
      this.filterRanking()
    },

    goDetail(id) {
      this.$router.push(`/restaurant/${id}`)
    }
  },
  watch: {
    sortBy() {
      this.loadRanking()
    }
  }
}
</script>

<style scoped>
.ranking {
  padding: 8px;
}
.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}
.search-wrapper {
  display: flex;
  gap: 8px;
  align-items: center;
}
.quick-tags {
  display: flex;
  gap: 8px;
}
.filter-section {
  margin-bottom: 20px;
}
.filter-label {
  font-weight: bold;
  margin-bottom: 10px;
  font-size: 14px;
  color: #2c3e50;
}
.filter-note {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}
.cost-range {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>