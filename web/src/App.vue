<script setup lang="ts">
// import Talk from './components/Talk.vue'
import PdfViewer from './components/pdfview/PdfView'

const DEFAULT_URL: string = "/videostabilization_cvpr05.pdf" // 2. 修改路径格式

</script>

<template>
  <PdfViewer src="/videostabilization_cvpr05.pdf" /> <!-- 3. 修正属性绑定语法 -->
</template>

<style scoped>
/* 可以留空或添加样式 */
</style>