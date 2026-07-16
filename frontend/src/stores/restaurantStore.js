import { defineStore } from 'pinia'

export const useRestaurantStore = defineStore('restaurant', {
  state: () => ({
    allRestaurants: [],      // 所有餐厅列表 [{item_id, name, star, cost, review_count}]
    currentRestaurant: null
  }),
  actions: {
    setAllRestaurants(list) {
      this.allRestaurants = list
    },
    setCurrentRestaurant(rest) {
      this.currentRestaurant = rest
    }
  }
})