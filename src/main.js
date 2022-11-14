import Vue from 'vue';
import App from './App.vue';
import router from './router';
import "bootstrap/dist/css/bootstrap.css";
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'
import Vuex from "vuex";
import loggedinUser from "./store/loggedinUser.js"
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);


// Import Bootstrap and BootstrapVue CSS files (order is important)
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import './registerServiceWorker'

// Make BootstrapVue available throughout your project
Vue.use(BootstrapVue)
// Optionally install the BootstrapVue icon components plugin
Vue.use(IconsPlugin)
Vue.use(Vuex)

Vue.config.productionTip = false
const store = new Vuex.Store({
  modules:{
    loggedinUser
  }
});

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')

export {store};
export {Chart}