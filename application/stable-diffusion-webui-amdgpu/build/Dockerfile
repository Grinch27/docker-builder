ARG base_image=ubuntu:latest
FROM ${base_image}

RUN set -x \
	&& export DEBIAN_FRONTEND=noninteractive \
    # ===== apt dependencies =====
	&& apt-get update --ignore-missing -y -qq \
    && apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
        ca-certificates \
        sudo \
    # Debian-based:
    && sudo apt-get install --fix-missing -y -qq \
        wget git python3.11 python3-pip libgl1 libglib2.0-0 \
    # ===== Clean apt =====
    && apt-get autoremove --purge -y -qq \
    && apt-get clean -y -qq \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/log/*.log \
	&& unset DEBIAN_FRONTEND \
    # ===== samba configuration =====
    # && echo -e "password\npassword" | smbpasswd -a root \
    # ===== docker-entrypoint.sh =====
    && sh_entrypoint="/docker-entrypoint.sh" \
    && echo "#!/usr/bin/env bash" >> ${sh_entrypoint} \
    # ----- start samba -----
	&& sh_samba="/start-samba.sh" \
	&& echo "smbd" >> ${sh_samba} \
	&& chmod +x ${sh_samba} \
	&& echo "${sh_samba} &" >> ${sh_entrypoint} \
    # ----- end of docker-entrypoint.sh -----
    && echo "uname -a" >> ${sh_entrypoint} \
	&& echo "sleep infinity" >> ${sh_entrypoint} \
	&& chmod +x ${sh_entrypoint}

# 安装基础依赖
RUN apt-get update && apt-get install -y \
    git \
    wget \
    python3.11 \
    python3-pip \
    python3-venv \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 创建一个非root用户
RUN useradd -m sduser
USER sduser
WORKDIR /home/sduser

# 克隆AMD支持版本的仓库
RUN git clone https://github.com/lshqqytiger/stable-diffusion-webui-amdgpu.git webui

# 设置工作目录
WORKDIR /home/sduser/webui

# 配置启动脚本，添加DirectML支持
RUN echo '#!/bin/bash\n\
export COMMANDLINE_ARGS="--use-directml --listen --port 7860"\n\
bash webui.sh\n\
' > /home/sduser/start.sh && chmod +x /home/sduser/start.sh

# 暴露端口
EXPOSE 7860

# 启动服务
ENTRYPOINT ["/home/sduser/start.sh"]




# ARG base_image=debian:testing-slim
# FROM ${base_image}

# RUN set -x \
#     # ===== apt dependencies =====
# 	&& export DEBIAN_FRONTEND=noninteractive \
# 	&& apt-get update --ignore-missing -y -qq \
#     && apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
# 		ca-certificates \
# 		samba \
#     # ===== Clean apt =====
#     && apt-get autoremove --purge -y -qq \
#     && apt-get clean -y -qq \
#     && rm -rf /var/lib/apt/lists/* \
#     && rm -rf /var/log/*.log \
# 	&& unset DEBIAN_FRONTEND \
#     # ===== samba configuration =====
#     # && echo -e "password\npassword" | smbpasswd -a root \
#     # ===== docker-entrypoint.sh =====
#     && sh_entrypoint="/docker-entrypoint.sh" \
#     && echo "#!/usr/bin/env bash" >> ${sh_entrypoint} \
#     # ----- start samba -----
# 	&& sh_samba="/start-samba.sh" \
# 	&& echo "smbd" >> ${sh_samba} \
# 	&& chmod +x ${sh_samba} \
# 	&& echo "${sh_samba} &" >> ${sh_entrypoint} \
#     # ----- end of docker-entrypoint.sh -----
#     && echo "uname -a" >> ${sh_entrypoint} \
# 	&& echo "sleep infinity" >> ${sh_entrypoint} \
# 	&& chmod +x ${sh_entrypoint}

# ENTRYPOINT ["/docker-entrypoint.sh"]
