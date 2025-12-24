# ファイル名: Dockerfile

# RTX 3090 をサポートする CUDA 12.0 ベースの PaddlePaddle イメージ
FROM paddlepaddle/paddle:2.6.1-gpu-cuda12.0-cudnn8.9-trt8.6

# パッケージリストを更新し、OpenCV 実行に必要なシステムライブラリをインストール
# (libgl1、libglib2.0 などは映像処理で必須)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリを設定
WORKDIR /workspace

# コンテナ起動時に bash シェルを実行
CMD ["/bin/bash"]