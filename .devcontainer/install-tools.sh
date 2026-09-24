#!/bin/bash
# Installs pinned, checksum-verified CLI tools into /usr/local/bin.
# Run by devcontainer.json's postCreateCommand. To bump a tool, update its
# version and both sha256s from the release's published checksums file.
set -euo pipefail

case "$(uname -m)" in
x86_64) ARCH=amd64 ;;
aarch64 | arm64) ARCH=arm64 ;;
*)
  echo "install-tools: unsupported architecture $(uname -m)" >&2
  exit 1
  ;;
esac

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# fetch <url> <sha256> <dest>
fetch() {
  curl -fsSL --retry 3 -o "$3" "$1"
  echo "$2  $3" | sha256sum --check --quiet -
}

# install_bin <name> <url> <sha256> [<path-in-tarball>]
install_bin() {
  local name="$1" url="$2" sha="$3" member="${4:-}"
  local file="$TMP/$name.download"
  fetch "$url" "$sha" "$file"
  if [ -n "$member" ]; then
    tar -xzf "$file" -C "$TMP" "$member"
    file="$TMP/$member"
  fi
  sudo install -m 0755 "$file" "/usr/local/bin/$name"
  echo "install-tools: $name installed"
}

GH=https://github.com

# actionlint — GitHub Actions workflow linter
V=1.7.12
declare -A SHA=(
  [amd64]=8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8
  [arm64]=325e971b6ba9bfa504672e29be93c24981eeb1c07576d730e9f7c8805afff0c6
)
install_bin actionlint \
  "$GH/rhysd/actionlint/releases/download/v$V/actionlint_${V}_linux_${ARCH}.tar.gz" \
  "${SHA[$ARCH]}" actionlint

# yq — YAML processor (mikefarah)
V=4.53.6
SHA=(
  [amd64]=c5f056448f973ae7d39b5401949648a78f2dc1947d6a8eb65be60d5c504b9385
  [arm64]=88a1016bc1d657375a35864e4f44b6f333df8ff97b559f51bba0adcb2169df09
)
install_bin yq "$GH/mikefarah/yq/releases/download/v$V/yq_linux_${ARCH}" "${SHA[$ARCH]}"

# hadolint — Dockerfile linter
V=2.15.1
declare -A HADOLINT_ARCH=([amd64]=x86_64 [arm64]=arm64)
SHA=(
  [amd64]=c7187db94eeeeca956519a6af171adc31453941a1e777961f6e680f697c8c507
  [arm64]=f6198ef8090f404dbb771abfee086eb8c48ac177f30da7fd3510aca35b344b5d
)
install_bin hadolint \
  "$GH/hadolint/hadolint/releases/download/v$V/hadolint-linux-${HADOLINT_ARCH[$ARCH]}" \
  "${SHA[$ARCH]}"

# trivy — image / filesystem vulnerability scanner
V=0.74.0
declare -A TRIVY_ARCH=([amd64]=64bit [arm64]=ARM64)
SHA=(
  [amd64]=2ae6fe3ee734b7fdf11335663e18c75ea12dccc76062f09f164a3b0f8be4371a
  [arm64]=b94ce1976bbf3c15b514b605ee88be7c6d94a29be2302847ff01cb794d47aad5
)
install_bin trivy \
  "$GH/aquasecurity/trivy/releases/download/v$V/trivy_${V}_Linux-${TRIVY_ARCH[$ARCH]}.tar.gz" \
  "${SHA[$ARCH]}" trivy

# act — run GitHub Actions workflows locally
V=0.2.89
declare -A ACT_ARCH=([amd64]=x86_64 [arm64]=arm64)
SHA=(
  [amd64]=0191d6f1f3b716b5c55820032605d05fc3c1cdbf581ebeff655019e5dd1524c0
  [arm64]=daa8679ba9615a74d2d0cec321dc593f21948a2a11bb65862b063d8b930f4bcb
)
install_bin act \
  "$GH/nektos/act/releases/download/v$V/act_Linux_${ACT_ARCH[$ARCH]}.tar.gz" \
  "${SHA[$ARCH]}" act
