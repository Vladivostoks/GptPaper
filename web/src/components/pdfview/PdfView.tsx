import { defineComponent, ref, onMounted, watch } from 'vue';
import type { Ref } from 'vue';
import * as pdfjsLib from 'pdfjs-dist';
// import * as pdfjsViewer from 'pdfjs-dist/web/pdf_viewer.mjs'
import type { PDFDocumentLoadingTask, 
              DocumentInitParameters, 
              RenderParameters} from 'pdfjs-dist/types/src/display/api';
import type { PDFDocumentProxy, 
              RenderTask, 
               } from 'pdfjs-dist';
import styles from './PdfView.module.styl'

// You might need to set the worker path
// pdfjsLib.GlobalWorkerOptions.workerSrc = 'pdfjs-dist/pdf.worker.mjs'

pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url
).href


console.log(styles)
async function CreateDoc(src:string):Promise<PDFDocumentProxy>{
    const CMAP_URL = "../../node_modules/pdfjs-dist/cmaps/";
    const param:DocumentInitParameters = {
      url: src,
      cMapUrl: CMAP_URL,
      cMapPacked: true,
      // enableXfa: ENABLE_XFA,

      // ✅ 关键加速参数
      disableAutoFetch: true,    // 禁用预加载（减少网络请求）
      disableStream: true,       // 禁用流式加载（提升解析速度）
      disableRange: true,       // 禁用范围请求（避免分段加载）
  
      // 🚀 性能优化参数
      useSystemFonts: false,     // 强制使用嵌入字体（避免字体加载延迟）
      useWasm: true,            // 启用 WASM 解码（默认已开启）
      verbosity: 0,             // 关闭调试日志（减少开销）
  
      // 🛡️ 稳定性参数
      isEvalSupported: false,    // 禁用 eval（提升安全性）
      stopAtErrors: false       // 尝试恢复错误（避免解析中断）
    }

    const task:PDFDocumentLoadingTask = pdfjsLib.getDocument(param)
    const doc:PDFDocumentProxy = await task.promise;
    return doc
}

async function RenderPage(canvas:Ref<HTMLCanvasElement>,
                          pdf: PDFDocumentProxy, 
                          pageNum: number,
                          scale:number):Promise<RenderTask|null>
{
    const page = await pdf.getPage(pageNum);
    const viewport = page.getViewport({ scale: scale });

    // 适配 HiDPI 屏幕
    const outputScale = window.devicePixelRatio || 1;
    const context = canvas.value.getContext('2d');
    if (!context) return null;

    // 设置 Canvas 尺寸
    canvas.value.width = Math.floor(viewport.width * outputScale);
    canvas.value.height = Math.floor(viewport.height * outputScale);
    canvas.value.style.width = `${Math.floor(viewport.width)}px`;
    canvas.value.style.height = `${Math.floor(viewport.height)}px`;

    // 渲染 PDF
    const renderContext:RenderParameters = {
        canvasContext: context,
        transform: outputScale !== 1 ? [outputScale, 0, 0, outputScale, 0, 0] : undefined,
        viewport: viewport,

        intent: 'display',        // 优化显示渲染管道
        annotationMode: 0         // 禁用注释渲染
    };

    try {
        const renderTask:RenderTask = page.render(renderContext);
        await renderTask.promise;

        return renderTask
    } catch (err) {
        console.error("Failed to render PDF page:", err);
        throw err;
    }
}

interface PdfViewerProps {
  src: string;  // PDF 文件路径
}

export default defineComponent({
  name: 'PdfViewer',
  setup(props: PdfViewerProps) {
    const canvasRef:Ref<HTMLCanvasElement|null> = ref<HTMLCanvasElement | null>(null);
    const pageNumber:Ref<number> = ref<number>(1);
    const TotalPagesNums = ref(0);
    const scale = ref(1.5);
    const loading = ref(false);

    // 加载 PDF 文档
    const loadPdf = async () => {
      loading.value = true;
      try {
        console.dir(props)
        const pdf:PDFDocumentProxy = await CreateDoc('/videostabilization_cvpr05.pdf')

        TotalPagesNums.value = pdf.numPages;
        await RenderPage(canvasRef as Ref<HTMLCanvasElement>, 
                         pdf, 
                         pageNumber.value, 
                         scale.value);
        loading.value = true
      } catch (err) {
        console.error('PDF 加载失败:', err);
      } finally {
        loading.value = false;
      }
    };

    // 翻页逻辑
    const prevPage = () => pageNumber.value > 1 && pageNumber.value--;
    const nextPage = () => pageNumber.value < TotalPagesNums.value && pageNumber.value++;

    // 监听页码/缩放变化
    watch([pageNumber, scale], loadPdf);

    // 初始化加载
    onMounted(loadPdf);

    return () => (
      <div class="pdf-viewer">
        {/* 控制栏 */}
        <div class="controls">
          <button 
            onClick={prevPage} 
            disabled={pageNumber.value <= 1}
          >
            上一页
          </button>
          <span>第 {pageNumber.value} 页 / 共 {TotalPagesNums.value} 页</span>
          <button 
            onClick={nextPage} 
            disabled={pageNumber.value >= TotalPagesNums.value}
          >
            下一页
          </button>
          <input 
            type="range" 
            v-model={scale.value}
            min="0.5"
            max="3"
            step="0.1"
            onChange={loadPdf}
          />
          <span>缩放: {scale.value}x</span>
        </div>

        {/* PDF 渲染区域 */}
        <div class="canvas-container">
          <canvas ref={canvasRef} class={styles['pdf-canvas']} />
        </div>

        {/* 加载状态 */}
        {loading.value && <div class="loading">加载中...</div>}
      </div>
    );
  }
});