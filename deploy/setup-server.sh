#!/usr/bin/env bash
# One-time setup of a fresh Ubuntu/Debian server for the deploy job in .github/workflows/build.yml.
# Run as root, next to sli.caddy, with the public half of the GitHub deploy key:
#   bash setup-server.sh "ssh-ed25519 AAAA... github-deploy"
set -euo pipefail

pubkey="${1:?usage: setup-server.sh '<deploy public key>'}"
here="$(cd "$(dirname "$0")" && pwd)"

# password login is switched off below, stop before that locks root out
if [ ! -s /root/.ssh/authorized_keys ]; then
  echo "add your own SSH key to /root/.ssh/authorized_keys first" >&2
  exit 1
fi

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get -y upgrade
DEBIAN_FRONTEND=noninteractive apt-get -y install rsync ufw unattended-upgrades \
  debian-keyring debian-archive-keyring apt-transport-https curl gpg

# Caddy from its own repository, it fetches and renews the HTTPS certificate
curl -1sLf https://dl.cloudsmith.io/public/caddy/stable/gpg.key \
  | gpg --dearmor --yes -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt \
  > /etc/apt/sources.list.d/caddy-stable.list
apt-get update
apt-get -y install caddy

# the deploy user only owns the site folder, it has no sudo
id deploy &>/dev/null || adduser --disabled-password --gecos "" deploy
install -d -m 700 -o deploy -g deploy /home/deploy/.ssh
printf '%s\n' "$pubkey" > /home/deploy/.ssh/authorized_keys
chown deploy:deploy /home/deploy/.ssh/authorized_keys
chmod 600 /home/deploy/.ssh/authorized_keys

install -d -m 755 -o deploy -g deploy /var/www/apps/sli /var/www/apps/sli/releases

# every app gets its own file in /etc/caddy/apps
install -d /etc/caddy/apps
install -m 644 "$here/sli.caddy" /etc/caddy/apps/sli.caddy
printf 'import apps/*.caddy\n' > /etc/caddy/Caddyfile
caddy validate --config /etc/caddy/Caddyfile
systemctl enable caddy
systemctl reload-or-restart caddy

# SSH with keys only
printf 'PasswordAuthentication no\nKbdInteractiveAuthentication no\nPermitRootLogin prohibit-password\n' \
  > /etc/ssh/sshd_config.d/10-keys-only.conf
systemctl reload ssh

ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 443/udp
ufw --force enable

echo "done, add DEPLOY_SSH_KEY and DEPLOY_KNOWN_HOSTS to the GitHub secrets"
