# Slow Rich — 投影片設計記錄

## 封面底色三選項（ep01）

預覽圖：`cover_option1.png` / `cover_option2.png` / `cover_option3.png`
獨立預覽 HTML：`cover_option1.html` / `cover_option2.html` / `cover_option3.html`

| 選項 | 名稱 | 漸層色（中間色） | 漸層色（兩端） | 特色 |
|------|------|----------------|----------------|------|
| 1 | 深海軍藍 | `#0d1b35` | `#080f1f` | 與 logo 海軍藍最接近，專業感強 |
| 2 | 純黑底帶藍調 | `#0a1628` | `#050a12` | 最深最暗，對比最強烈，YouTube 縮圖感 |
| 3 | 深藍偏紫 | `#0e1540` | `#06091a` | 偏藍紫色調，高端金融感 |

### CSS 寫法

```css
/* 選項 1：深海軍藍 */
background: linear-gradient(150deg, #080f1f 0%, #0d1b35 55%, #080f1f 100%);

/* 選項 2：純黑底帶藍調 */
background: linear-gradient(150deg, #050a12 0%, #0a1628 55%, #050a12 100%);

/* 選項 3：深藍偏紫 */
background: linear-gradient(150deg, #06091a 0%, #0e1540 55%, #06091a 100%);
```

---

## 品牌色（全系列共用）

| 用途 | 色碼 | 名稱 |
|------|------|------|
| 主色（六邊形底）| `#1B3A6B` | 海軍藍 |
| 輔色（分隔線）| `#2E5FA3` | 皇家藍 |
| 內六邊形邊框 | `#4A7FD4` | 淡藍 |
| 金色強調 | `#D4AF37` | 香檳金 |
| 危險 / 強調紅 | `#ff5555` | 亮紅（封面標題用）|

---

## 字體 / 字重即時選擇 HUD（Debug 用）

在需要比較不同字體或字重時，可在 HTML 加入以下程式碼，確認後移除。

### 步驟 1：給目標文字元素加 id

```html
<div id="logo-zh" style="...">慢富</div>
```

### 步驟 2：在 `</body>` 前加入 HUD + 字體載入

先在 `<head>` 加入 Google Fonts（需要用到的字體）：

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@100;200;300;400&family=Noto+Serif+TC:wght@200;300;400&display=swap">
```

然後在 `</body>` 前加入：

```html
<!-- ══ 字體 / 字重調整 HUD（確認後移除）══ -->
<div id="fw-hud" style="position:fixed;bottom:16px;right:16px;z-index:9999;background:rgba(0,0,0,0.88);color:#D4AF37;font-family:monospace;font-size:13px;padding:14px 18px;border-radius:10px;border:1px solid rgba(212,175,55,0.55);line-height:2.2;user-select:none;min-width:220px;">
  <div style="margin-bottom:6px;color:#fff;font-weight:700;">文字 字體選擇</div>
  <label style="display:block;cursor:pointer;">
    <input type="radio" name="logo-font" value="'Noto Serif TC', serif" style="accent-color:#D4AF37;">
    &nbsp;Noto Serif TC（宋體）
  </label>
  <label style="display:block;cursor:pointer;">
    <input type="radio" name="logo-font" value="'Noto Sans TC', sans-serif" style="accent-color:#D4AF37;">
    &nbsp;Noto Sans TC（黑體）
  </label>
  <label style="display:block;cursor:pointer;">
    <input type="radio" name="logo-font" value="-apple-system,'PingFang TC',sans-serif" checked style="accent-color:#D4AF37;">
    &nbsp;PingFang TC（目前）
  </label>
  <div style="margin-top:8px;border-top:1px solid rgba(212,175,55,0.3);padding-top:8px;">
    字重 &nbsp;<span id="fw-val" style="color:#fff;font-weight:700;">400</span><br>
    <input id="fw-slider" type="range" min="100" max="900" step="100" value="400"
      style="width:190px;accent-color:#D4AF37;cursor:pointer;">
  </div>
</div>
<script>
(function(){
  var slider  = document.getElementById('fw-slider');
  var valSpan = document.getElementById('fw-val');
  var target  = document.getElementById('logo-zh');
  function apply(){
    var checked = document.querySelector('input[name="logo-font"]:checked');
    if (checked) target.style.fontFamily = checked.value;
    target.style.fontWeight = slider.value;
    valSpan.textContent = slider.value;
  }
  slider.addEventListener('input', apply);
  document.querySelectorAll('input[name="logo-font"]').forEach(function(r){
    r.addEventListener('change', apply);
  });
})();
</script>
```

### 使用方式

1. 瀏覽器開啟 HTML
2. 右下角 HUD 點選字體 radio button 即時切換
3. 拖動 slider 調整字重（100–900）
4. 確認後將字體 + 字重寫入正式 CSS，移除 HUD 和 Google Fonts link

### 目前定案（logo 慢富）

- 字體：PingFang TC
- 字重：300
- 字號：26px
- 顏色：#D4AF37

---

## SVG 元素透明度調整 HUD（Debug 用）

需要即時調整 SVG 元素透明度時使用。以 logo 分格線為例。

### 步驟 1：給目標元素加 id

```html
<line id="spoke1" ... opacity="0.3"/>
<line id="spoke2" ... opacity="0.3"/>
<line id="spoke3" ... opacity="0.3"/>
<path id="innerhex" ... opacity="0.3"/>
```

### 步驟 2：在 `</body>` 前加入 HUD

```html
<!-- ══ 透明度 HUD（確認後移除）══ -->
<div style="position:fixed;bottom:16px;right:16px;z-index:9999;background:rgba(0,0,0,0.88);color:#D4AF37;font-family:monospace;font-size:13px;padding:14px 18px;border-radius:10px;border:1px solid rgba(212,175,55,0.55);line-height:2.2;user-select:none;min-width:220px;">
  透明度 &nbsp;<span id="op-val" style="color:#fff;font-weight:700;">0.30</span><br>
  <input id="op-slider" type="range" min="0" max="100" step="1" value="30"
    style="width:190px;accent-color:#D4AF37;cursor:pointer;">
</div>
<script>
(function(){
  var slider  = document.getElementById('op-slider');
  var valSpan = document.getElementById('op-val');
  var targets = ['spoke1','spoke2','spoke3','innerhex'].map(function(id){
    return document.getElementById(id);
  });
  slider.addEventListener('input', function(){
    var op = (slider.value / 100).toFixed(2);
    targets.forEach(function(el){ if(el) el.setAttribute('opacity', op); });
    valSpan.textContent = op;
  });
})();
</script>
```

### 使用方式

1. 瀏覽器開啟 HTML，右下角出現 slider
2. 拖動調整 0.00（隱藏）～ 1.00（完全不透明）
3. 確認數值後寫入各元素的 `opacity` 屬性，移除 HUD

### 目前定案（logo 分格線 + 內六邊形）

- 原始值：1.0（無設定）
- 定案值：0.3

---

## 元素定位輔助工具（Debug 用）

在需要微調絕對定位元素時，可在 HTML 加入以下兩段程式碼，確認位置後移除。

### 步驟 1：給目標元素加 id

```html
<div id="cover-logo" style="position:absolute;top:15px;right:85px;...">
```

### 步驟 2：在 `</body>` 前加入 HUD + 拖曳腳本

```html
<!-- ══ 定位輔助模式（確認後移除）══ -->
<div id="coord-hud" style="position:fixed;bottom:16px;right:16px;z-index:9999;background:rgba(0,0,0,0.88);color:#D4AF37;font-family:monospace;font-size:13px;padding:10px 16px;border-radius:8px;border:1px solid rgba(212,175,55,0.55);line-height:2;pointer-events:none;">
  滑鼠 &nbsp;<span id="hud-mouse" style="color:#fff;">x: —,  y: —</span><br>
  Logo &nbsp;<span id="hud-logo" style="color:#fff;">—</span>
</div>
<script>
(function () {
  function toSlide(clientX, clientY) {
    var sec = document.querySelector('section.cover-slide');
    if (!sec) return { x: 0, y: 0 };
    var r = sec.getBoundingClientRect();
    return {
      x: Math.round((clientX - r.left) / r.width  * 1100),
      y: Math.round((clientY - r.top)  / r.height * 650)
    };
  }
  document.addEventListener('mousemove', function (e) {
    var p = toSlide(e.clientX, e.clientY);
    document.getElementById('hud-mouse').textContent = 'x: ' + p.x + ',  y: ' + p.y;
  });
  var logo = document.getElementById('cover-logo');
  if (!logo) return;
  logo.style.cursor = 'grab';
  logo.style.userSelect = 'none';
  var dragging = false, startCX, startCY, startTop, startRight;
  logo.addEventListener('mousedown', function (e) {
    e.preventDefault();
    dragging = true;
    logo.style.cursor = 'grabbing';
    startCX = e.clientX; startCY = e.clientY;
    startTop = parseInt(logo.style.top); startRight = parseInt(logo.style.right);
  });
  document.addEventListener('mousemove', function (e) {
    if (!dragging) return;
    var sec = document.querySelector('section.cover-slide');
    var r = sec.getBoundingClientRect();
    var sc = r.width / 1100;
    var newTop   = Math.round(startTop   + (e.clientY - startCY) / sc);
    var newRight = Math.round(startRight - (e.clientX - startCX) / sc);
    logo.style.top = newTop + 'px'; logo.style.right = newRight + 'px';
    var lr = logo.getBoundingClientRect();
    document.getElementById('hud-logo').textContent =
      'top:' + newTop + '  right:' + newRight +
      '   →   左上角 x:' + Math.round((lr.left - r.left) / sc) +
      '  y:' + Math.round((lr.top - r.top) / sc);
  });
  document.addEventListener('mouseup', function () {
    if (!dragging) return;
    dragging = false; logo.style.cursor = 'grab';
    var sec = document.querySelector('section.cover-slide');
    var r = sec.getBoundingClientRect();
    var sc = r.width / 1100;
    var lr = logo.getBoundingClientRect();
    document.getElementById('hud-logo').textContent =
      '✓  top:' + logo.style.top + '  right:' + logo.style.right +
      '   →   左上角 x:' + Math.round((lr.left - r.left) / sc) +
      '  y:' + Math.round((lr.top - r.top) / sc);
  });
})();
</script>
```

### 使用方式

1. 在瀏覽器開啟 HTML
2. 滑鼠移動 → 右下角 HUD 顯示游標在 1100×650 座標系的 x,y（適合定位 SVG path 節點）
3. 直接拖動 Logo → 放開後顯示新的 `top` / `right` CSS 值和左上角 x,y
4. 確認位置後，將 CSS 值寫入正式程式碼，並移除 HUD + script

### 注意

- `toSlide()` 的座標系基準是 `section.cover-slide`，投影片縮放時仍準確
- 若要追蹤其他元素，將 `getElementById('cover-logo')` 改為對應的 id 即可
- SVG 折線節點無法直接拖曳，用滑鼠 hover 讀取 x,y 後告知 Claude 修改

---

---

## 內容製作流程（影片發布）

### Phase 1 — 準備（先做完再開錄）

1. 投影片定稿（HTML 確認無誤）
2. 寫好旁白稿（每張投影片要說什麼，先寫稿再錄比較不會 NG）
3. 確定開場音樂

### Phase 2 — 錄製（核心資產）

1. 錄「主體投影片」：螢幕錄影 + 同步旁白（這段是所有產出的母帶）
2. 錄「開場介紹」（30 秒～1 分鐘，說明本集主題）
3. 錄「結尾」（訂閱、下集預告等）

### Phase 3 — 剪輯（一次剪，多版本輸出）

| 產出 | 組合方式 |
|------|---------|
| YouTube 完整版 | 開場音樂 + 開場介紹 + 主體投影片 + 結尾 |
| Reels 短影音 | 從主體投影片截取 30～60 秒精華片段 |
| Apple Podcast | 直接擷取 YouTube 完整版的音訊軌 |
| FB 文章 | 從旁白稿改寫成文字，貼上 YouTube 連結 |

**建議**：旁白稿是最省力的槓桿，寫好稿後錄音、FB 文章、Podcast 描述都可以直接用。Reels 精華片段建議在剪完 YouTube 版後再挑，比較知道哪段最吸引人。

---

## 開場台詞

每集影片固定開場結構：**問題鉤子 → 自我介紹 → 本集預告**

### 1. 問題鉤子（5–10 秒，每集客製）

先拋一個觀眾心裡有過的問題，例如：
- EP06：「你有沒有覺得，現在好像不是進場的好時機？等跌下來再買？」

### 2. 自我介紹（約 15 秒，固定）

> 歡迎來到 Slow Rich，我是科技宅爸。我喜歡用數據說話，在台股和美股我都是指數化投資人。這個頻道，就是把投資書上的方法，用台股和美股的數據重新驗證一遍。

### 3. 本集預告（10 秒，每集客製）

說明今天要講什麼、看完可以得到什麼，例如：
- EP06：「今天我們來看數據——錯過幾天，結果有多慘。」

---

## 10 集投影片清單

建議觀看順序如下。EP01/02 必看，其餘各集獨立但按此順序脈絡最完整。

| 集數 | 主題 | Notion | HTML | index.html 資料來源 |
|------|------|--------|------|---------------------|
| EP01 | Why invest？為什麼要投資？ | 有 | 完成 | — |
| EP02 | 指數化投資是什麼？ | 有 | 待做 | — |
| EP03 | 巴菲特雪球理論（複利的威力）| 有 | 待做 | — |
| EP04 | 預期報酬率與波動（滾動報酬率）| 有 | 待做 | `#sec-rolling` |
| EP05 | 為什麼不要選股（成分股分析）| 有 | 待做 | `analysis_data.js` |
| EP06 | 為什麼不要猜測高低點 | 有 | 待做 | `#sec-missing-days` |
| EP07 | 投資試算（6%/8%/10%）| 有 | 待做 | `#sec-simulator` |
| EP08 | 退休提領法則（3%/4%）| 有 | 待做 | `#sec-withdrawal` |
| EP09 | 股債配置回測 | 有 | 待做 | `#sec-bond` |
| EP10 | 內扣費用率對投資的影響 | 有 | 待做 | `#sec-expenserate` |

### 製作節奏

1. 在 Notion 對應集數的子分頁寫下你想說的內容（自由格式）
2. 告訴 Claude「EPxx 可以開始了」
3. Claude 讀 Notion → 討論確認投影片結構 → 生成 HTML（沿用 EP01 品牌風格）
4. 本機預覽確認 → push 到 stock_info public repo

### 設計原則

- 所有集數沿用 EP01 的品牌設計（封面折線、配色、字型）
- HTML 檔案命名：`ep01_why_invest.html`、`ep02_xxx.html` ...
- 每集 push 後可在手機預覽：`https://alvin5468.github.io/stock_info/ppt/epXX_xxx.html`

---

## 資料來源與待處理項目

### EP05 — 0050 成分股分析資料（analysis_data.js）

| 項目 | 內容 |
|------|------|
| 來源檔案 | `stock_price_2003_to_2026.xlsx` |
| 資料截止日 | **2026/04/28**（抓取當天股價） |
| 涵蓋範圍 | 0050 歷史全部 108 支成分股（現任 + 已離開）|
| 報酬率計算 | 各股入選 0050 當年年初股價 → 2026/04/28 收盤價，純價差（未含配息）|
| 0050 報酬率 | 869.8%（2003 年初 37.1 元 → 2026/04/28；**含配息再投入總報酬**）|
| 注意 | 個股為純價差、0050 為總報酬，兩者基礎不同，嚴格比較時請留意 |

下次更新時，重新執行 `scripts/init_entry_prices.py`，並將 Excel 更名為對應日期版本。

---

### EP04 — VT 歷史資料延長（待做）

目前 `data_vt.js` 僅有 2009–2024 年資料（VT ETF 成立於 2008 年），未涵蓋 2000–2002 網路泡沫。

**計劃做法：**
1. 用 `yfinance` 抓 ACWI（iShares MSCI ACWI ETF）2008 年至今股價
2. 從 MSCI 官網下載 MSCI ACWI 指數 1988 年後的歷史數據
3. 拼接兩段資料，得到 1988–今的完整回測
4. 重新計算各持有年限的滾動報酬率，更新 `ep04_return_reality.html` p8 的圖表與結論

完成後「3 年以上持有」的結論可能需要修正，建議改以「10 年以上」為持有門檻的說法更穩健。

---

## 相關檔案

| 檔案 | 說明 |
|------|------|
| `ep01_why_invest.html` | EP01 投影片主檔（reveal.js 5.1.0）|
| `logo/README.md` | Logo 設計版本記錄（Turtle Golden 系列）|
| `logo/logo_1_turtle-golden_4.html` | 目前使用的 Logo（海軍藍版）|
