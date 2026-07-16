import { createRouter, createWebHistory } from 'vue-router'
import Overview from '../views/Overview.vue'
import Ranking from '../views/Ranking.vue'
import RestaurantDetail from '../views/RestaurantDetail.vue'
import Compare from '../views/Compare.vue'

const routes = [
  { path: '/', redirect: '/overview' },
  { path: '/overview', name: 'Overview', component: Overview },
  { path: '/ranking', name: 'Ranking', component: Ranking },
  { path: '/restaurant/:id', name: 'RestaurantDetail', component: RestaurantDetail, props: true },
  { path: '/compare', name: 'Compare', component: Compare },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router