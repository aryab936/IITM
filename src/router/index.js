import Vue from 'vue';
import VueRouter from 'vue-router';
import NumericalLogs from '../views/NumericalLogs.vue';
import FailedLogin from "../views/FailedLogin";
import numericalUpdate from "../views/numericalUpdate";
import numericalAdd from "../views/numericalAdd";
import BooleanLogs from "../views/booleanLogs.vue";
import LoginView from "../views/Login.vue";
import booleanAdd from "../views/booleanAdd";
import booleanUpdate from "../views/booleanUpdate";
import timeDurationAdd from "../views/timeDurationAdd";
import timeDurationLogs from "../views/TimeDurationLogs";
import timeDurationUpdate from "../views/timeDurationUpdate";
import MultipleChoiceLogs from "../views/MultiChoiceLogs.vue";
import multiChoiceAdd from "../views/multipleChoiceAdd.vue";
import multiChoiceUpdate from "../views/multiChoiceUpdate";
import DashBoard from "../views/DashBoard.vue";
import dashboardAdd from "../views/DashboardAdd";
import addOptions from "../views/addOptions";
import dashboardUpdate from "../views/DashboardUpdate";
import dashboardMultiUpdate from "../views/dashboardMultiUpdate";
import ForgotPassword from "../views/forgotPassword";
import NewUser from "../views/newUser";
Vue.use(VueRouter)




const routes = [
  {
    path: '/numericalLogs',
    name: "NumericLogs",
    component: NumericalLogs
  },
  {
    path:'/login',
    name: "LoginView",
    component : LoginView
  },
  {
    path:"/",
    name:"LoginHome",
    component : LoginView
  },
  {
    path:"/failedLogin",
    name:"FailedLogin",
    component: FailedLogin
  },
  {
    path:"/numericalUpdate",
    name:"numericalUpdate",
    component: numericalUpdate
  },
  {
    path:"/numericalAdd",
    name:"numercialAdd",
    component:numericalAdd
  },
  {
    path:"/booleanLogs",
    name:"BooleanLogs",
    component: BooleanLogs
  },
  {
    path:"/booleanAdd",
    name:"booleanAdd",
    component: booleanAdd
  },
  {
    path:"/booleanUpdate",
    name:"booleanUpdate",
    component: booleanUpdate
  },
  {
    path:"/timeDurationAdd",
    name:"timeDurationAdd",
    component : timeDurationAdd
  },
  {
    path:"/timeDurationLogs",
    name:"timeDurationLogs",
    component: timeDurationLogs
  },
  {
    path:"/timeDurationUpdate",
    name:"timeDurationUpdate",
    component: timeDurationUpdate
  },
  {
    path:"/multiChoiceLogs",
    name:"multiChoiceLogs",
    component:MultipleChoiceLogs
  },
  {
    path:"/multiChoiceAdd",
    name:"multiChoiceAdd",
    component:multiChoiceAdd
  },
  {
    path:"/multiChoiceUpdate",
    name:"multiChoiceUpdate",
    component:multiChoiceUpdate
  },
  {
    path:"/dashboard",
    name:"Dashboard",
    component:DashBoard
  },
  {
    path:"/dashboardAdd",
    name:"dashboardAdd",
    component:dashboardAdd
  },
  {
    path:"/addOptions",
    name:"addOptions",
    component:addOptions
  },
  {
    path:"/dashboardUpdate",
    name:"dashboardUpdate",
    component:dashboardUpdate
  },
  {
    path:"/dashboardMultiUpdate",
    name:"dashboardMultiUpdate",
    component:dashboardMultiUpdate
  },
  {
    path:"/forgotPassword",
    name:"forgotPassword",
    component:ForgotPassword
  },
  {
    path:"/newUser",
    name:"NewUser",
    component: NewUser
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})


export default router 

