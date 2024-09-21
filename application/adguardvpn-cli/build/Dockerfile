ARG base_image=alpine:latest
FROM ${base_image}

# ARG update_channel=release
# ENV update_channel=${update_channel}

ARG build_arg="" \
    flag_split=","
RUN set -x \
    # ===== Set environment variable =====
    && export build_arg=$(echo "${build_arg}" | sed 's|^[\"]*||;s|[\"]*$||' | sed "s|^[\']*||;s|[\']*$||") \
    && echo "${build_arg}" \
    && echo "${build_arg}" | tr "${flag_split}" '\n' | while IFS='=' read -r key value; do \
        if [ -n "$key" ] && [ -n "$value" ]; then \
            echo "$key=$value" >> /etc/environment; \
        fi; \
    done \
    && set -a \
    && . /etc/environment \
    && set +a \
    && printenv \
    # ===== apk dependencies =====
    && apk update \
    && apk add --no-cache \
        ca-certificates \
        curl \
        tar \
        gpg \
        jq \
    # ===== System info =====
    && cpu='x86_64' \
    && case "$(uname --machine)" in \
        'x86_64'|'amd64') cpu='x86_64' ;; \
        'aarch64'|'arm64') cpu='aarch64' ;; \
        'armv7l') cpu='armv7' ;; \
        # 'mips') cpu=$(hexdump -o <<<I | awk '{print substr($2, 6, 1)}' | grep -q 1 && echo 'mipsel' || echo 'mips') ;; \
        *) echo "Unsupported CPU architecture: $(uname --machine)" ; exit 1 ;; \
    esac \
    # ===== Setup AdGuardVPNCLI =====
    && tag_target=${update_channel} \
    # https://api.github.com/repos/AdguardTeam/AdGuardVPNCLI/tags
    && tag_download=$(curl -s "https://api.github.com/repos/AdguardTeam/AdGuardVPNCLI/tags" | \
        jq -r --arg tag_target "$tag_target" '.[] | select(.name | contains($tag_target)) | .name' | head -n 1) \
    # https://api.github.com/repos/AdguardTeam/AdGuardVPNCLI/releases/tags/v1.0.0
    && URL_download=$(curl -s "https://api.github.com/repos/AdguardTeam/AdGuardVPNCLI/releases/tags/${tag_download}" | \
        jq -r --arg cpu "$cpu" '.assets[] | select(.name | contains($cpu)) | .browser_download_url' | head -n 1)  \
    && FILE_download="/tmp/adguardvpn-cli.tar.gz" \
    && PATH_adguardvpn_cli="/opt/adguardvpn_cli" \
    && mkdir -p ${PATH_adguardvpn_cli} \
    && curl -fsSL ${URL_download} -o ${FILE_download} \
    && tar xzf ${FILE_download} -C ${PATH_adguardvpn_cli} --strip-components=1 \
    && ls -lh ${PATH_adguardvpn_cli} \
    && ln -sf "${PATH_adguardvpn_cli}/adguardvpn-cli" "/usr/local/bin/adguardvpn-cli" \
    && rm -f ${FILE_download} \
    # ===== Clean pre-install =====
    && apk del --no-cache \
        curl \
        tar \
        gpg \
        jq \
    # ===== Clean apk =====
    && rm -rf /var/cache/apk/* \
    && rm -rf /var/log/*.log \
    # ===== docker-entrypoint.sh =====
    && sh_entrypoint="/docker-entrypoint.sh" \
    && echo "#!/usr/bin/env sh" >> ${sh_entrypoint} \
    # ----- end of docker-entrypoint.sh -----
    && echo "uname -a" >> ${sh_entrypoint} \
	&& echo "sleep infinity" >> ${sh_entrypoint} \
	&& chmod +x ${sh_entrypoint}

ENTRYPOINT ["/docker-entrypoint.sh"]

# ----- OLD -----
# && URL_SH="https://raw.githubusercontent.com/AdguardTeam/AdGuardVPNCLI/master/scripts/${update_channel}/install.sh" \
# && FILE_SH="/install.sh" \
# && curl -fsSL ${URL_SH} -o ${FILE_SH} \
# && sed -i 's/read -r response < \/dev\/tty/response="y"/g' ${FILE_SH} \
# && chmod +x ${FILE_SH} \
# && sh --verbose ${FILE_SH} \
# && rm -f ${FILE_SH} \
