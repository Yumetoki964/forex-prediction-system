# デザインシステム定義書

## 基本情報
- プロジェクト名: Forex Prediction System
- テーマ名: プロフェッショナル・トレーディング（ダークモード）
- 作成日: 2025-08-23
- バージョン: 1.0.0

## デザインコンセプト

Bloomberg Terminal風のプロフェッショナルダークモードデザイン。長時間の取引監視に最適化された目に優しい環境を提供し、高密度情報表示によってトレーダーが必要とする全ての情報を効率的にアクセスできるよう設計されています。

深いダークブルーを基調としたカラーパレットは、ブルーライトを軽減しながらも重要な情報を明確に際立たせ、プロトレーダーが求める視認性とプロフェッショナル感を両立しています。

## カラーパレット

### プライマリカラー
```css
--primary: #00d4ff;           /* メインアクセントカラー - シアンブルー */
--primary-dark: #0099cc;      /* プライマリ暗色 - ホバー・アクティブ状態 */
--primary-light: #33ddff;     /* プライマリ明色 - 強調表示 */
```

### セカンダリカラー
```css
--secondary: #1a1f2e;         /* メイン背景色 - 深いダークブルー */
--secondary-light: #2d3748;   /* セクション背景 - グレーブルー */
--secondary-lighter: #4a5568; /* カード背景 - ライトグレーブルー */
```

### ニュートラルカラー
```css
--background: #0f1419;        /* 最背景色 - 極暗ブルーブラック */
--surface: #1a1f2e;          /* サーフェス背景 - 深いダークブルー */
--surface-elevated: #2d3748; /* 浮上サーフェス - グレーブルー */
--border: #4a5568;           /* ボーダー色 - ライトグレーブルー */
--divider: #2d3748;          /* 区切り線 - セクション背景色 */
```

### セマンティックカラー
```css
--success: #00ff88;          /* 成功・利益・買いシグナル */
--success-bg: rgba(0, 255, 136, 0.1); /* 成功背景色 */
--warning: #fbbf24;          /* 警告・注意・中立シグナル */
--warning-bg: rgba(251, 191, 36, 0.1); /* 警告背景色 */
--error: #ef4444;            /* エラー・損失・売りシグナル */
--error-bg: rgba(239, 68, 68, 0.1); /* エラー背景色 */
--text-primary: #e6e8eb;     /* メインテキスト - オフホワイト */
--text-secondary: #9ca3af;   /* セカンダリテキスト - ライトグレー */
--text-muted: #6b7280;       /* 補助テキスト - グレー */
```

## タイポグラフィ

### フォントファミリー
```css
--font-primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'SF Pro Display', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
--font-numeric: 'Courier New', 'SF Mono', Monaco, Menlo, 'Consolas', monospace;
--font-code: 'Fira Code', 'Courier New', Monaco, Menlo, 'Consolas', monospace;
```

### フォントサイズ
```css
--text-xs: 0.75rem;      /* 12px - 補助情報・キャプション */
--text-sm: 0.875rem;     /* 14px - セカンダリテキスト */
--text-base: 1rem;       /* 16px - 基本テキスト */
--text-lg: 1.125rem;     /* 18px - 大きめテキスト */
--text-xl: 1.25rem;      /* 20px - 小見出し */
--text-2xl: 1.5rem;      /* 24px - 中見出し・重要数値 */
--text-3xl: 2rem;        /* 32px - 大見出し・メイン数値 */
--text-4xl: 2.5rem;      /* 40px - 特大表示・現在レート */
--text-5xl: 3rem;        /* 48px - 超特大表示 */
```

### 行間とフォントウェイト
```css
--leading-tight: 1.25;   /* タイトル用 */
--leading-normal: 1.5;   /* 本文用 */
--leading-relaxed: 1.75; /* 読みやすさ重視 */

--font-normal: 400;      /* 通常テキスト */
--font-medium: 500;      /* やや強調 */
--font-semibold: 600;    /* 中強調 */
--font-bold: 700;        /* 強調 */
```

## スペーシング

```css
--spacing-xs: 0.25rem;   /* 4px - 極小間隔 */
--spacing-sm: 0.5rem;    /* 8px - 小間隔 */
--spacing-md: 1rem;      /* 16px - 標準間隔 */
--spacing-lg: 1.5rem;    /* 24px - 大間隔 */
--spacing-xl: 2rem;      /* 32px - 特大間隔 */
--spacing-2xl: 3rem;     /* 48px - 超特大間隔 */
--spacing-3xl: 4rem;     /* 64px - セクション間隔 */
```

## UI要素スタイル

### ボタン
```css
/* プライマリボタン */
.btn-primary {
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: var(--background);
  border: none;
  border-radius: 8px;
  padding: var(--spacing-md) var(--spacing-lg);
  font-family: var(--font-primary);
  font-weight: var(--font-semibold);
  font-size: var(--text-base);
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background: linear-gradient(135deg, var(--primary-light), var(--primary));
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3);
}

/* セカンダリボタン */
.btn-secondary {
  background: var(--surface-elevated);
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: var(--spacing-md) var(--spacing-lg);
  font-family: var(--font-primary);
  font-weight: var(--font-medium);
  font-size: var(--text-base);
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: var(--border);
  border-color: var(--primary);
}
```

### カード
```css
.card {
  background: linear-gradient(135deg, var(--surface-elevated), var(--border));
  border-radius: 12px;
  padding: var(--spacing-lg);
  border: 1px solid var(--border);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

.card-header {
  color: var(--primary);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  margin-bottom: var(--spacing-sm);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.card-value {
  color: var(--text-primary);
  font-family: var(--font-numeric);
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  margin-bottom: var(--spacing-xs);
}

.card-meta {
  color: var(--text-secondary);
  font-size: var(--text-xs);
}
```

### フォーム要素
```css
.form-group {
  margin-bottom: var(--spacing-lg);
}

.form-label {
  display: block;
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  margin-bottom: var(--spacing-xs);
}

.form-input {
  width: 100%;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: var(--spacing-md);
  color: var(--text-primary);
  font-family: var(--font-primary);
  font-size: var(--text-base);
  transition: all 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.2);
}

.form-select {
  background: var(--surface) url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%239ca3af' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e") no-repeat right var(--spacing-md) center;
  background-size: 1em 1em;
  appearance: none;
  padding-right: calc(var(--spacing-lg) + 1em);
}
```

### アラート
```css
.alert {
  border-radius: 8px;
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  font-size: var(--text-sm);
  border-left: 4px solid;
}

.alert-success {
  background: var(--success-bg);
  border-left-color: var(--success);
  color: var(--success);
}

.alert-warning {
  background: var(--warning-bg);
  border-left-color: var(--warning);
  color: var(--warning);
}

.alert-error {
  background: var(--error-bg);
  border-left-color: var(--error);
  color: var(--error);
}
```

### ナビゲーション要素
```css
.nav-header {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: var(--spacing-md) var(--spacing-lg);
}

.nav-brand {
  color: var(--primary);
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
}

.nav-menu {
  display: flex;
  list-style: none;
  gap: var(--spacing-lg);
  margin: 0;
  padding: 0;
}

.nav-item {
  color: var(--text-secondary);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: var(--font-medium);
}

.nav-item:hover {
  color: var(--text-primary);
  background: var(--surface-elevated);
}

.nav-item.active {
  color: var(--primary);
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
}
```

### サイドバー要素
```css
.sidebar {
  background: var(--surface);
  border-right: 1px solid var(--border);
  width: 280px;
  height: 100vh;
  padding: var(--spacing-lg);
  overflow-y: auto;
}

.sidebar-menu {
  list-style: none;
  margin: 0;
  padding: 0;
}

.menu-section {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: var(--spacing-lg) var(--spacing-md) var(--spacing-sm);
}

.menu-item {
  color: var(--text-secondary);
  padding: var(--spacing-sm) var(--spacing-md);
  margin-bottom: var(--spacing-xs);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.menu-item:hover {
  color: var(--text-primary);
  background: var(--surface-elevated);
}

.menu-item.active {
  color: var(--primary);
  background: rgba(0, 212, 255, 0.1);
  border-left: 3px solid var(--primary);
}

.menu-icon {
  width: 18px;
  height: 18px;
  opacity: 0.7;
}
```

## レイアウト

### コンテナ
```css
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 var(--spacing-lg);
}

.container-fluid {
  width: 100%;
  padding: 0 var(--spacing-lg);
}

.main-layout {
  display: flex;
  min-height: 100vh;
  background: var(--background);
}

.content-area {
  flex: 1;
  padding: var(--spacing-lg);
  overflow: auto;
}
```

### グリッドシステム
```css
.grid {
  display: grid;
  gap: var(--spacing-lg);
}

.grid-cols-1 { grid-template-columns: repeat(1, minmax(0, 1fr)); }
.grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.grid-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }

.col-span-1 { grid-column: span 1; }
.col-span-2 { grid-column: span 2; }
.col-span-3 { grid-column: span 3; }
.col-span-4 { grid-column: span 4; }

/* 自動調整グリッド */
.grid-auto-fit {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.grid-auto-fill {
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}
```

## ナビゲーション構造

### グローバルナビゲーション
レイアウトパターン: サイドバー型（管理画面系に最適化）

構成要素:
- プライマリメニュー: 予測ダッシュボード、詳細分析、バックテスト
- セカンダリメニュー: データ管理、予測設定、データソース管理
- ユーザーメニュー: アカウント設定、ログアウト

### サイドバー仕様
展開/折りたたみ:
- デフォルト状態: 展開表示（280px幅）
- モバイル時: オーバーレイ表示
- アイコン+ラベル表示で視認性を確保

階層構造:
- 最大階層数: 2階層まで
- グルーピング: 機能別セクション分け
- アクティブ状態: 左ボーダーと背景色で明示

### レスポンシブ戦略
ブレークポイント:
- モバイル（〜768px）: サイドバー折りたたみ、オーバーレイ表示
- タブレット（769px〜1024px）: 縮小サイドバー、アイコンのみ表示
- デスクトップ（1025px〜）: フルサイドバー表示

## チャートカラースキーム

### 価格チャート
```css
--chart-up: var(--success);      /* 上昇ローソク足・ライン */
--chart-down: var(--error);      /* 下降ローソク足・ライン */
--chart-neutral: var(--warning); /* 同値・横ばい */
--chart-volume: rgba(0, 212, 255, 0.3); /* 出来高バー */
--chart-grid: var(--border);     /* グリッドライン */
--chart-text: var(--text-secondary); /* チャート内テキスト */
```

### テクニカル指標
```css
--indicator-ma5: #ff6b9d;        /* 移動平均線5日 */
--indicator-ma25: #4ecdc4;       /* 移動平均線25日 */
--indicator-ma75: #45b7d1;       /* 移動平均線75日 */
--indicator-rsi: var(--warning); /* RSI */
--indicator-macd: var(--primary); /* MACD */
--indicator-bb: rgba(0, 212, 255, 0.2); /* ボリンジャーバンド */
```

### 予測ライン
```css
--prediction-1w: var(--primary);     /* 1週間予測 */
--prediction-2w: #33ddff;           /* 2週間予測 */
--prediction-3w: #66e6ff;           /* 3週間予測 */
--prediction-1m: #99eeff;           /* 1ヶ月予測 */
--confidence-area: rgba(0, 212, 255, 0.1); /* 信頼区間 */
```

## アニメーション

### トランジション
```css
--transition-fast: 0.15s ease-out;   /* 高速トランジション */
--transition-base: 0.3s ease-out;    /* 基本トランジション */
--transition-slow: 0.5s ease-out;    /* 低速トランジション */
```

### アニメーション定義
```css
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideInLeft {
  from { opacity: 0; transform: translateX(-20px); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

@keyframes shimmer {
  0% { background-position: -200px 0; }
  100% { background-position: calc(200px + 100%) 0; }
}

/* 数値更新アニメーション */
@keyframes numberUpdate {
  0% { color: var(--text-primary); }
  50% { color: var(--primary); transform: scale(1.05); }
  100% { color: var(--text-primary); transform: scale(1); }
}

.animate-fade-in { animation: fadeIn 0.6s ease-out; }
.animate-slide-in { animation: slideInLeft 0.4s ease-out; }
.animate-pulse { animation: pulse 2s ease-in-out infinite; }
.animate-number-update { animation: numberUpdate 0.8s ease-out; }
```

## レスポンシブブレークポイント

```css
/* モバイルファースト設計 */
--breakpoint-sm: 640px;   /* スマートフォン横向き */
--breakpoint-md: 768px;   /* タブレット縦向き */
--breakpoint-lg: 1024px;  /* タブレット横向き・小型PC */
--breakpoint-xl: 1280px;  /* デスクトップPC */
--breakpoint-2xl: 1536px; /* 大型ディスプレイ */

/* メディアクエリ */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: -280px;
    z-index: 1000;
    transition: left var(--transition-base);
  }
  
  .sidebar.open {
    left: 0;
  }
  
  .grid-cols-2,
  .grid-cols-3,
  .grid-cols-4 {
    grid-template-columns: 1fr;
  }
  
  .text-4xl { font-size: 2rem; }
  .text-3xl { font-size: 1.5rem; }
}

@media (max-width: 640px) {
  .container,
  .container-fluid {
    padding: 0 var(--spacing-md);
  }
  
  .card {
    padding: var(--spacing-md);
  }
}
```

## アクセシビリティ

### フォーカス管理
```css
/* キーボードフォーカス */
*:focus {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

/* フォーカス表示の改善 */
.btn-primary:focus,
.btn-secondary:focus {
  box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.3);
}

.form-input:focus {
  box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.2);
}
```

### カラーコントラスト
全ての色の組み合わせがWCAG 2.1 AA基準（4.5:1以上のコントラスト比）を満たすよう設計済み

### スクリーンリーダー対応
```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

## 実装ガイド

### 1. CSS変数の読み込み
プロジェクトのメインCSSファイルに以下を追加:

```css
/* globals.css または main.css */
:root {
  /* カラーパレット */
  --primary: #00d4ff;
  --secondary: #1a1f2e;
  --background: #0f1419;
  /* 以下、上記で定義された全ての変数 */
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-primary);
  background: var(--background);
  color: var(--text-primary);
  line-height: var(--leading-normal);
}
```

### 2. クラスの使用例

```html
<!-- ダッシュボードカード例 -->
<div class="card">
  <div class="card-header">USD/JPY 現在レート</div>
  <div class="card-value">149.85</div>
  <div class="card-meta">+0.45 (+0.30%)</div>
</div>

<!-- ボタン例 -->
<button class="btn-primary">予測実行</button>
<button class="btn-secondary">設定</button>

<!-- フォーム例 -->
<div class="form-group">
  <label class="form-label" for="period">予測期間</label>
  <select id="period" class="form-input form-select">
    <option>1週間</option>
    <option>2週間</option>
    <option>1ヶ月</option>
  </select>
</div>

<!-- アラート例 -->
<div class="alert alert-success">
  予測が正常に更新されました
</div>
```

### 3. ナビゲーション実装例

```html
<!-- メインレイアウト -->
<div class="main-layout">
  <!-- サイドバー -->
  <aside class="sidebar">
    <div class="nav-brand">Forex Prediction</div>
    <ul class="sidebar-menu">
      <li class="menu-section">メイン機能</li>
      <li class="menu-item active">
        <span class="menu-icon">📊</span>
        予測ダッシュボード
      </li>
      <li class="menu-item">
        <span class="menu-icon">📈</span>
        詳細分析
      </li>
      <li class="menu-item">
        <span class="menu-icon">🔍</span>
        バックテスト
      </li>
      
      <li class="menu-section">管理機能</li>
      <li class="menu-item">
        <span class="menu-icon">🗄️</span>
        データ管理
      </li>
      <li class="menu-item">
        <span class="menu-icon">⚙️</span>
        設定
      </li>
    </ul>
  </aside>

  <!-- メインコンテンツ -->
  <main class="content-area">
    <div class="container">
      <!-- ページコンテンツ -->
    </div>
  </main>
</div>
```

## 更新履歴

### v1.0.0 (2025-08-23)
- 初回デザインシステム作成
- プロフェッショナル・トレーディングテーマ適用
- Bloomberg Terminal風ダークモードデザイン実装
- 完全なカラーパレット・タイポグラフィ・コンポーネント定義
- レスポンシブブレークポイント設定
- アクセシビリティ対応指針策定

## 注意事項

1. **数値表示**: 為替レートなど重要な数値は必ず`var(--font-numeric)`（等幅フォント）を使用
2. **カラーコントラスト**: 全ての組み合わせでWCAG 2.1 AA基準を満たすことを確認済み
3. **ダークモード専用**: ライトモード切り替えは現バージョンでは未対応
4. **アニメーション**: 数値更新時は`animate-number-update`クラスを適用してユーザビリティを向上
5. **レスポンシブ**: モバイルファースト設計により全デバイスで最適化済み
6. **フォーカス管理**: キーボードナビゲーション完全対応

このデザインシステムは、プロトレーダーの厳しい要求に応える高密度情報表示と、長時間使用に適した目に優しいダークモード環境を両立させています。