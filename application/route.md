# application\samba

新建一个文件夹，参考该 markdown 指出的文件夹架构，创建文件,名为：

## level 1

samba

## level 2

samba\build
samba\env
samba\meta-app
samba\test
samba\push

## level 3

samba\build\build.sh
samba\build\Dockerfile
samba\env\vars.env
samba\meta-app\meta-app.sh
samba\test\test.sh
samba\push\tag_version.shw

## file

### samba\build\build.sh

```bash
#!/bin/sh

set -x

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

# 搜索 Dockerfile 文件，不区分大小写
dockerfile=$(find "${dir_current}" -type f -iname 'dockerfile')
if [ -z "$dockerfile" ]; then
  echo "未找到 Dockerfile 文件"
  exit 1
else
  echo "找到 Dockerfile 文件: ${dockerfile}"
fi

# ===== docker buildx =====
docker buildx build \
  --platform ${arch_branch} \
  --file ${dockerfile} \
  --tag "${registry_local}/${repo_dockerhub}:${tag_repo}" \
  --build-arg base_image=${base_image} \
  ${build_arg:+--build-arg build_arg=${build_arg}} \
  --label version=${version} \
  --output type=registry,registry.insecure=true \
  .
```

## samba\env\vars.env

```bash
repo_dockerhub=grinch27/samba
arch_branch=linux/amd64,linux/arm64
base_image=debian:sid-slim
```

## samba\meta-app\meta-app.sh

```bash
#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

apt-get update --ignore-missing -y -qq
apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
	ca-certificates \
	samba

# Version 4.20.6
# 4.21.3-Debian-4.21.3+dfsg-6+b1
version=$(smbd --version)
# version=$(echo "$version" | awk '/Version/ {print $2}')
# echo "version=${version}"

remove_prefix="Version "
remove_suffix="-Debian"
version=${version##*$remove_prefix}
version=${version%%$remove_suffix*}
echo "version=${version}"
```

## samba\test\test.sh

```bash
#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

# Version 4.20.6
# 4.21.3-Debian-4.21.3+dfsg-6+b1
version=$(smbd --version)
# version=$(echo "$version" | awk '/Version/ {print $2}')
# echo "version=${version}"

remove_prefix="Version "
remove_suffix="-Debian"
version=${version##*$remove_prefix}
version=${version%%$remove_suffix*}
echo "version=${version}"
```

## samba\push\tag_version.sh

```bash
#!/bin/sh

# Get current directory
dir_current=$(dirname "$(readlink -f "$0")")
echo "dir_current=${dir_current}"

echo "tag_version=${tag_version}"
tag_version=$(echo "${tag_version}" | cut -d'-' -f2-)
echo "tag_version=${tag_version}"
# 4.21.3-Debian-4.21.3+dfsg-6+b1
```

## Dockerfile

```dockerfile
ARG base_image=debian:testing-slim
FROM ${base_image}

RUN set -x \
    # ===== apt dependencies =====
	&& export DEBIAN_FRONTEND=noninteractive \
	&& apt-get update --ignore-missing -y -qq \
    && apt-get install --no-install-recommends --no-install-suggests --fix-missing -y -qq \
		ca-certificates \
		samba \
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

ENTRYPOINT ["/docker-entrypoint.sh"]
```
