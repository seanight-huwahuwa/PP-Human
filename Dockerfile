# 파일명: Dockerfile

# RTX 3090을 지원하는 CUDA 12.0 기반 PaddlePaddle 이미지
FROM paddlepaddle/paddle:2.6.1-gpu-cuda12.0-cudnn8.9-trt8.6

# 패키지 목록 업데이트 및 OpenCV 실행을 위한 필수 시스템 라이브러리 설치
# (libgl1, libglib2.0 등은 영상 처리 시 필수입니다)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /workspace

# 컨테이너 실행 시 bash 쉘 실행
CMD ["/bin/bash"]