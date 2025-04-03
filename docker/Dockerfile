FROM ubuntu:jammy

ENV DEBIAN_FRONTEND=noninteractive

# Update and install necessary packages
RUN <<EOF
apt-get update
apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    curl \
    gnupg \
    locales
apt-get clean
rm -rf /var/lib/apt/lists/*
EOF

# Configure Japanese locale
RUN <<EOF
locale-gen ja_JP.UTF-8
update-locale LANG=ja_JP.UTF-8 LC_ALL=ja_JP.UTF-8
EOF

# Set environment variables for Japanese locale
ENV LANG=ja_JP.UTF-8
ENV LC_ALL=ja_JP.UTF-8

# Install GitHub CLI
RUN <<EOF
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null
apt-get update
apt-get install -y gh
apt-get clean
rm -rf /var/lib/apt/lists/*
EOF

# Install uv
RUN <<EOF
curl -fsSL https://astral.sh/uv/install.sh | bash
EOF

ENV PATH="/root/.local/bin:${PATH}"

# Set Python 3 as the default python
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Check Python version
RUN python3 --version

# TeXLiveのインストール、TeXLiveのサイトから最新のinstall-tlを取得して行う
# 作業の際、余計なデータが残らないように、install-tlは/tmp以下にダウンロードして展開し、呼び出す
RUN --mount=type=bind,source=.,target=/docker <<EOM
# Install TeXLive
set -x
mkdir -p /tmp/texlive
cd /tmp/texlive
# Download the TeXLive installer
curl -L -O https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz
tar xvzf install-tl-unx.tar.gz
mv install-tl-*/ install-tl.d
cd install-tl.d
./install-tl --profile=/docker/texlive.profile --lang=ja --repository=https://ftp.yz.yamagata-u.ac.jp/pub/CTAN/systems/texlive/tlnet/
hash -r
tlmgr install wrapfig capt-of framed upquote needspace \
    tabulary varwidth titlesec latexmk cmap float wrapfig \
    fancyvrb booktabs parskip 
# Clean up
cd /tmp
rm -rf /tmp/texlive
EOM

# /opt/texlive/2023/bin/x86_64-linuxにパスを通すようにシェルのスタートアップを書き換え
RUN <<EOM
echo 'export PATH=/opt/texlive/bin/x86_64-linux:$PATH' >> /etc/bash.bashrc
echo 'export PATH=/opt/texlive/bin/x86_64-linux:$PATH' >> /etc/profile
EOM

