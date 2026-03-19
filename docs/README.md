# AI论文全自动预研助手 - 可视化界面

## 📊 功能概览

一个美观、易用的论文可视化界面，可以实时从arXiv检索论文并展示数据。

### ✨ 主要功能

1. **🔍 智能搜索**
   - 输入关键词，自动检索相关论文
   - 支持中英文关键词
   - 实时显示检索结果

2. **📊 数据统计**
   - 论文总数
   - 独特作者数量
   - 研究领域数量
   - 检索耗时

3. **📈 可视化图表**
   - 论文发表趋势图（折线图）
   - 论文分类分布图（柱状图）

4. **📄 论文列表**
   - 按时间排序的论文
   - 显示标题、作者、时间、分类
   - 一键下载PDF

---

## 🚀 快速开始

### macOS / Linux

#### 方法1：使用启动脚本（推荐）

```bash
cd /Users/wangbo/.openclaw/workspace/projects/paper-research-assistant/docs
./start.sh
```

然后在浏览器中访问：**http://localhost:8000**

#### 方法2：手动启动

```bash
cd /Users/wangbo/.openclaw/workspace/projects/paper-research-assistant/docs
python3 -m http.server 8000
```

然后在浏览器中访问：**http://localhost:8000**

---

### Windows

#### 方法1：使用PowerShell

```powershell
cd C:\Users\你的用户名\.openclaw\workspace\projects\paper-research-assistant\docs
python -m http.server 8000
```

#### 方法2：使用CMD

```cmd
cd C:\Users\你的用户名\.openclaw\workspace\projects\paper-research-assistant\docs
python -m http.server 8000
```

然后在浏览器中访问：**http://localhost:8000**

---

## 📱 使用说明

### 1. 搜索论文

1. 在搜索框中输入关键词
   - 例如："machine learning"、"artificial intelligence"、"K12 English teaching"

2. 点击"🔍 检索论文"按钮

3. 等待检索完成（通常1-3秒）

### 2. 查看结果

- **统计信息**：查看找到的论文数量、作者数量等
- **图表**：查看论文发表趋势和分类分布
- **论文列表**：查看所有找到的论文

### 3. 下载论文

- 点击论文标题下方的"📥 下载PDF →"链接
- PDF将自动下载到浏览器默认下载文件夹

---

## 🎨 界面预览

### 主界面
```
┌─────────────────────────────────────────────┐
│         📚 AI论文全自动预研助手              │
│  基于OpenClaw的多Agent协作系统               │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ [输入框]           [🔍 检索论文]             │
└─────────────────────────────────────────────┘

┌──────┬──────┬──────┬──────┐
│ 50   │ 128  │ 15   │ 1.2s │
│ 论文 │ 作者 │ 分类 │ 耗时 │
└──────┴──────┴──────┴──────┘

┌─────────────────────────────────────────────┐
│ 📊 论文发表趋势图                             │
│ [折线图]                                     │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ 🏷️ 论文分类分布图                             │
│ [柱状图]                                     │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ 📄 论文列表                                   │
│ 1. Neural Field Thermal Tomography...        │
│ 2. V2M-Zero: Zero-Pair Time-Aligned...      │
│ 3. Uncovering statistical structure...       │
│ ...                                          │
└─────────────────────────────────────────────┘
```

---

## 🔧 自定义配置

### 修改默认搜索词

编辑 `index.html` 文件，找到第351行：

```javascript
window.onload = function() {
    document.getElementById('searchInput').value = 'machine learning';
    searchPapers();
};
```

修改 `'machine learning'` 为你想要的关键词。

### 修改最大结果数

编辑 `index.html` 文件，找到第322行：

```javascript
const response = await fetch(
    `https://export.arxiv.org/api/query?search_query=allintitle:"${encodeURIComponent(query)}"&start=0&max_results=50&sortBy=submittedDate&sortOrder=descending`
);
```

修改 `max_results=50` 为你想要的数量（1-2000）。

### 修改图表显示数量

编辑 `index.html` 文件中的 `generateCharts` 函数：

```javascript
// 修改趋势图显示数量（第370行）
const recentPapers = papers.slice(0, 10);  // 改为 5, 20, 50 等

// 修改分类图显示数量（第378行）
const sortedCategories = Object.entries(categoryCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);  // 改为 5, 15, 20 等
```

---

## 📊 数据来源

### arXiv API

- **API端点**：https://export.arxiv.org/api/query
- **数据格式**：RSS Feed
- **更新频率**：实时更新
- **数据范围**：计算机科学、数学、物理等领域

### 支持的搜索关键词

- **英文**："machine learning"、"artificial intelligence"、"deep learning"
- **中文**："机器学习"、"人工智能"、"深度学习"
- **组合**："K12 English teaching"、"quantum computing"

---

## 🛠️ 技术栈

### 前端技术

| 技术 | 用途 |
|------|------|
| HTML5 | 页面结构 |
| CSS3 | 样式设计 |
| JavaScript | 交互逻辑 |
| Chart.js | 数据可视化 |
| Fetch API | API调用 |

### 特性

- ✅ **无框架**：纯原生JavaScript
- ✅ **响应式**：自适应各种屏幕
- ✅ **无依赖**：除了Chart.js CDN
- ✅ **本地运行**：无需服务器（可选）

---

## 📝 使用示例

### 示例1：搜索机器学习

```
输入：machine learning
结果：
  - 找到论文：50篇
  - 独特作者：128位
  - 研究领域：15个
  - 检索耗时：1.2秒
  - 显示：统计信息、图表、论文列表
```

### 示例2：搜索K12英语教学

```
输入：K12 English teaching
结果：
  - 找到论文：12篇
  - 独特作者：25位
  - 研究领域：8个
  - 检索耗时：1.5秒
  - 显示：统计信息、图表、论文列表
```

### 示例3：搜索深度学习

```
输入：deep learning
结果：
  - 找到论文：45篇
  - 独特作者：95位
  - 研究领域：12个
  - 检索耗时：1.1秒
  - 显示：统计信息、图表、论文列表
```

---

## 💡 使用场景

### 1. 科研人员
- 快速了解研究现状
- 发现相关论文和作者
- 下载感兴趣的论文

### 2. 学生
- 查找论文用于学习
- 了解研究领域趋势
- 探索研究方向

### 3. 研究者
- 发现新课题
- 了解研究热点
- 跟踪最新进展

### 4. 教师
- 查找教学论文
- 了解领域发展
- 准备教学材料

---

## 🔗 相关链接

- **arXiv官网**：https://arxiv.org
- **arXiv API文档**：https://arxiv.org/help/api/
- **Chart.js文档**：https://www.chartjs.org/docs/
- **项目主页**：/Users/wangbo/.openclaw/workspace/projects/paper-research-assistant

---

## 📞 技术支持

如有问题或建议，请通过以下方式联系：

- **项目位置**：`/Users/wangbo/.openclaw/workspace/projects/paper-research-assistant`
- **可视化页面**：`/Users/wangbo/.openclaw/workspace/projects/paper-research-assistant/docs/index.html`
- **启动脚本**：`/Users/wangbo/.openclaw/workspace/projects/paper-research-assistant/docs/start.sh`

---

**祝使用愉快！** 🎉

## 📄 许可证

MIT License
