ARG base_image=ubuntu:latest
FROM ${base_image}

RUN set -x \
	&& export DEBIAN_FRONTEND=noninteractive \
    # ===== apt dependencies =====
	&& apt-get update --ignore-missing -y -qq \
    # && apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
    #     ca-certificates \
    #     sudo \
    # Debian-based:
    && apt-get install --no-install-recommends --no-install-suggests --fix-missing -y \
        ca-certificates \
        software-properties-common \
        wget \
        curl \
        git \
        # python3.11 \
        # python3-pip \
        # python3-venv \
        libgl1 \
        libglib2.0-0 \
    # ubuntu install python3.11 or python3.10
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update --ignore-missing -y -qq \
    && apt-get install -y \
        python3.11 \
        python3-pip \
        python3-venv \
    && export python_cmd="python3.11" \
    # ===== Clean apt =====
    && apt-get autoremove --purge -y -qq \
    && apt-get clean -y -qq \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/log/*.log \
    # # ===== samba configuration =====
    # # && echo -e "password\npassword" | smbpasswd -a root \
    # # ===== docker-entrypoint.sh =====
    # && sh_entrypoint="/docker-entrypoint.sh" \
    # && echo "#!/usr/bin/env bash" >> ${sh_entrypoint} \
    # # ----- start samba -----
	# && sh_samba="/start-samba.sh" \
	# && echo "smbd" >> ${sh_samba} \
	# && chmod +x ${sh_samba} \
	# && echo "${sh_samba} &" >> ${sh_entrypoint} \
    # # ----- end of docker-entrypoint.sh -----
    # && echo "uname -a" >> ${sh_entrypoint} \
	# && echo "sleep infinity" >> ${sh_entrypoint} \
	# && chmod +x ${sh_entrypoint}
    # ========== user ==========
    && unset DEBIAN_FRONTEND \
    && useradd -m sduser \
    && echo "sduser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# # 创建一个非root用户
# RUN useradd -m sduser
# USER sduser
# WORKDIR /home/sduser

# # 创建非root用户
# RUN useradd -m sduser \
#     && echo "sduser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

    # 克隆AMD支持版本的仓库
RUN git clone https://github.com/lshqqytiger/stable-diffusion-webui-amdgpu.git /home/sduser/stable-diffusion-webui --depth=1 \
    && chown -R sduser:sduser /home/sduser/stable-diffusion-webui

USER sduser
WORKDIR /home/sduser/stable-diffusion-webui

RUN bash webui.sh
    # && export COMMANDLINE_ARGS="--use-directml --listen --port 7860"

# # 设置工作目录
# WORKDIR /home/sduser/webui

# 暴露端口
EXPOSE 7860

# 启动服务
# ENTRYPOINT ["/home/webui/webui.sh", "--use-directml", "--listen", "--port", "7860"]
# uname -a sleep infinity
ENTRYPOINT ["sleep", "infinity"]

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
