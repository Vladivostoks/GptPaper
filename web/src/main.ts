import { createApp } from 'vue'

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import TDesign from 'tdesign-vue-next';
import TDesignChat from '@tdesign-vue-next/chat'; // 引入chat组件
import '@tdesign-vue-next/chat/es/style/index.css'; // 引入chat组件的少量全局样式变量

import './style.css'
import App from './App.vue'



createApp(App)
.use(ElementPlus)
.use(TDesign)
.use(TDesignChat)
.mount('#app')
