<template>
  <div id="app">
    <el-container class="layout-container">
      <el-aside width="250px" class="sidebar">
        <div class="logo">🍜 食数洞察</div>
        <el-menu
          router
          :default-active="$route.path"
          background-color="#1e2a36"
          text-color="#bfc9d4"
          active-text-color="#ffffff"
        >
          <el-menu-item index="/overview">
            <el-icon><PieChart /></el-icon>
            <span>数据总览</span>
          </el-menu-item>
          <el-menu-item index="/ranking">
            <el-icon><Trophy /></el-icon>
            <span>餐厅排行</span>
          </el-menu-item>
          <el-menu-item index="/compare">
            <el-icon><Connection /></el-icon>
            <span>对比分析</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="header">
          <h2>广州粤菜餐厅大数据平台</h2>
          <div class="user-info">欢迎使用</div>
        </el-header>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { PieChart, Trophy, Connection } from '@element-plus/icons-vue'

export default {
  name: 'App',
  components: { PieChart, Trophy, Connection }
}
</script>

<style>
/* 样式保持不变，可沿用原有样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
#app {
  font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}
.layout-container {
  height: 100%;
}
.sidebar {
  background-color: #1e2a36;
  color: white;
  box-shadow: 2px 0 12px rgba(0,0,0,0.1);
  overflow-y: auto;
}
.logo {
  font-size: 1.4rem;
  font-weight: bold;
  padding: 24px 20px;
  text-align: center;
  border-bottom: 1px solid #2d3e4b;
  margin-bottom: 20px;
}
.el-menu {
  border-right: none;
}
.header {
  background: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  padding: 0 24px;
}
.user-info {
  color: #5a6e7c;
}
.el-main {
  background: #f5f7fa;
  padding: 24px;
  overflow-y: auto;
}

/* 仅增大侧边栏菜单字体大小 */
.sidebar .el-menu-item {
  font-size: 20px;
}
</style>