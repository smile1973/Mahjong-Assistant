# 日麻助手 - Mahjong Assistant

## 專案簡介
這是一個基於 Python 的雀魂（Majsoul）麻將遊戲即時助手工具。透過攔截和分析 WebSocket 通訊，實時分析手牌情況，提供最佳出牌建議和進張機率計算。

## 主要功能
- 實時監測雀魂遊戲進程
- 自動分析手牌聽牌狀態
- 計算各張牌的進張機率
- 提供吃碰槓等操作建議
- 顯示寶牌和剩餘牌數資訊

## 系統需求
- Python 3.7+
- Chrome 瀏覽器
- ChromeDriver
- WSL (Windows Subsystem for Linux) 或 Linux/macOS 環境

## 依賴套件
```
selenium
mitmproxy
protobuf
```

## 建置流程

### 1. 安裝必要套件

```bash
# 安裝 Python 套件
pip install selenium mitmproxy protobuf

# 下載 ChromeDriver
# 將 chromedriver 放置在專案目錄下
```

### 2. 設置代理

```bash
# 確保 8080 端口未被佔用
netstat -an | grep 8080

# 如果被佔用，需要先停止佔用的程序或修改程式碼中的端口
```

### 3. 安裝 mitmproxy 憑證

#### 方法一：透過瀏覽器安裝（推薦）

1. 啟動 mitmproxy：
```bash
mitmdump
```

2. 設定瀏覽器代理：
   - 打開 Chrome 設定 → 進階 → 系統 → 開啟電腦的代理設定
   - 或直接加`--proxy-server=http://127.0.0.1:8080`在應用程式 → 內容 → 目標後
   - 設定 HTTP/HTTPS 代理為 `127.0.0.1:8080`

3. 在瀏覽器中訪問 http://mitm.it

4. 下載並安裝對應的憑證（選擇您的作業系統）

#### 方法二：手動安裝憑證（Windows + WSL）

1. 在 WSL 中生成憑證：
```bash
# 首次運行 mitmproxy 會自動生成憑證
mitmdump

# 複製憑證到 Windows
cp ~/.mitmproxy/mitmproxy-ca-cert.p12 /mnt/c/Users/{您的用戶名}/Desktop/
```

2. 在 Windows 中安裝憑證：
   - 雙擊憑證檔案
   - 選擇「目前使用者」
   - 密碼欄留空
   - 選擇「將所有憑證放入下列存放區」→「受信任的根憑證授權單位」

3. Chrome 額外設定：
   - 在 Chrome 網址列輸入 `chrome://settings/security`
   - 點擊「管理憑證」
   - 確認 mitmproxy 憑證已安裝在「受信任的根憑證授權單位」

### 4. 設定專案

1. 確保 `chromedriver.exe` 位於專案根目錄

2. 確認所有相關檔案存在：
   - `main.py`
   - `analyze.py`
   - `proto/liqi_pb2.py`

3. 測試運行：
```bash
python main.py
```

### 5. 使用方法

1. 啟動程式：
```bash
mitmdump -s main.py
```

2. 設定瀏覽器代理（如果尚未設定）：
   - Chrome：設定 → 進階 → 系統 → 代理設定
   - 設定 HTTP/HTTPS 代理為 `127.0.0.1:8888`

3. 開啟雀魂網站：
   - 國際版：https://mahjongsoul.com/
   - 日服：https://game.mahjongsoul.com/

4. 登入並進入遊戲

5. 程式會自動偵測遊戲狀態並在終端機顯示分析結果

## 輸出說明

程式會輸出以下資訊：
- 當前手牌狀態（向聽數）
- 推薦打出的牌
- 可能的進張及其機率
- 可執行的操作（吃、碰、槓、和牌）

範例輸出：
```
聽牌
打 3m 摸 1m4m7m 進牌機率: 8.571%
打 6m 摸 4m7m 進牌機率: 5.714%
==========
```

## 注意事項

1. **僅供學習使用**：本工具僅供學習和研究麻將策略使用，請勿用於不當用途

2. **隱私安全**：使用時請注意網路安全，不要在公共網路環境下使用

3. **憑證安全**：mitmproxy 憑證安裝後會允許該程式解密 HTTPS 流量，使用完畢後建議移除

4. **瀏覽器設定**：使用完畢後記得將瀏覽器代理設定改回原始狀態

5. **版權聲明**：雀魂是 Yostar 的註冊商標，本專案與官方無關

## 故障排除

### 憑證錯誤
如果出現憑證錯誤，請確認：
- mitmproxy 憑證已正確安裝
- Chrome 已重新啟動
- 嘗試在 Chrome 設定中清除 SSL 狀態

### 連線問題
- 確認代理設定正確（127.0.0.1:8080）
- 檢查防火牆是否阻擋連線
- 確認 mitmproxy 正在運行

### WebSocket 連線失敗
- 可能是遊戲協議更新，需要更新 proto 文件
- 確認網路連線穩定

## 開發相關

### 專案結構
```
.
├── main.py           # 主程式，包含 WebSocket 監聽邏輯
├── analyze.py        # 協議分析模組
└── proto/           # Protocol Buffer 定義
    └── liqi_pb2.py  # 雀魂協議定義
```

### 技術架構
- **mitmproxy**: 作為中間人代理攔截 WebSocket 通訊
- **Selenium**: 自動化瀏覽天鳳網站進行牌型分析
- **Protocol Buffers**: 解析雀魂的遊戲協議

## 授權
本專案僅供個人學習使用，請遵守相關服務條款。
