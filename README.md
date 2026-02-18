# PaddleDetection PP-Human（WSL2 & Docker 環境）

このプロジェクトは、Windows 11 の WSL2（Ubuntu 24.04）および NVIDIA RTX 3090 環境で PaddleDetection の `PP-Human` パイプライン（人物追跡、属性解析、ReID）を実行するためのガイドです。

### デモ（自動再生 GIF）
以下は結果の例として保存された 5 秒の GIF です。

![Demo](real_test.jpg)

## 1. 環境構築（Installation）

### 事前準備
- Windows に WSL2 と Ubuntu がインストールされていること
- Docker Desktop または Docker Engine がインストールされていること
- NVIDIA ドライバーがインストールされていること

### Step 1: Docker コンテナの起動
ターミナルで `docker-compose.yml` があるフォルダに移動して起動します。

```bash
docker compose up -d
docker compose exec paddle-dev /bin/bash
```

### Step 2: 必要ライブラリのインストール（コンテナ内）
コンテナに初回で入る場合、以下を一度実行してください。

```bash
# 1. ソースコード取得
cd /workspace
git clone https://github.com/PaddlePaddle/PaddleDetection.git

# 2. 依存関係インストール
cd PaddleDetection
pip install -r requirements.txt
python setup.py install

# 3. 足りないライブラリの追加インストール（重要）
pip install scikit-learn numba
```

---

## 2. 実行方法（Usage）

WSL2 環境では USB カメラ接続が不安定（タイムアウト）になることがあるため、Windows 側で録画した動画ファイルを解析する方法を推奨します。

### Step 1: 動画準備
1. Windows の「カメラ」アプリで動画を撮影します。
2. 撮影したファイルを WSL のフォルダにコピーします（例: `real_test.mp4`）。
   * エクスプローラーのパス例: `\\wsl$\\Ubuntu-24.04\\home\\snowflake\\PP-Human`

### Step 2: AI 解析の実行
以下のコマンドで解析を開始します（ファイルパスは絶対パス推奨）。

```bash
# 実行ディレクトリ移動
cd /workspace/PaddleDetection/deploy/pipeline

# 解析コマンド実行
python pipeline.py \
    --config config/infer_cfg_pphuman.yml \
    --video_file=/workspace/real_test.mp4 \
    --device=gpu \
    -o ATTR.enable=True REID.enable=True MOT.tracker_config=config/tracker_config.yml \
    --output_dir=/workspace/output_result
```

- `--video_file`: 解析する動画ファイルのパス
- `ATTR.enable=True`: 性別・年齢などの属性解析を有効化
- `REID.enable=True`: Re-Identification（再識別）を有効化
- `output_dir`: 結果動画の保存先

### Step 3: 結果確認
解析が完了したら、Windows エクスプローラーで `/workspace/output_result` フォルダを確認してください。

---

## 3. 参考（Reference）

### A. RTSP ネットワークカメラを使用する場合
実運用ではファイルではなく CCTV のストリームアドレスを指定して解析します。

```bash
python pipeline.py \
    ... \
    --video_file=rtsp://admin:1234@192.168.0.10:554/stream \
    ...
```

### B. USB カメラ接続（WSL2 - 非推奨）
WSL2 の USB 帯域の問題で途切れが発生する可能性があります。必要な場合は `usbipd` を利用してください。

**Windows PowerShell（管理者）**
```powershell
usbipd list
usbipd bind --busid <BUSID>
usbipd attach --wsl --busid <BUSID>
```

**Docker 実行時のデバイス確認**
```bash
ls -l /dev/video0
```

### C. トラブルシューティング
- **ModuleNotFoundError: No module named 'sklearn'**: `pip install scikit-learn` を実行してください。
- **FileNotFoundError: config/tracker_config.yml**: `MOT.tracker_config=config/tracker_config.yml` のように設定ファイルパスを明示してください。
```
