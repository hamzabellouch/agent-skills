---
name: wireguard-mesh-vpn-routing
metadata:
  category: Network Engineering and Edge Routing
description: Design, deploy, and maintain zero-trust mesh VPNs and site-to-site overlay networks using WireGuard. Configure cryptographic key pairs, AllowedIPs subnet routing, persistent keepalives, NAT traversal, and automated tunnel configurations using wg-quick. Trigger when setting up secure cross-cloud VPC peering, remote access tunnels, or encrypted overlays.
compatibility: Linux Kernel 5.6+, WireGuard Tools (`wg`, `wg-quick`)
---

# WireGuard Mesh VPN & Routing Skill Guide

This skill provides step-by-step guidance for configuring, automating, and troubleshooting WireGuard kernel-based VPN tunnels for site-to-site and point-to-point mesh networks.

---

## 1. Cryptographic Mesh Architecture

WireGuard relies on **Noise Protocol Framework (Curve25519, ChaCha20-Poly1305, BLAKE2s)**. Every peer is identified solely by its public key.

```text
[ Cloud Node A (AWS) ]                  [ Cloud Node B (GCP) ]
Public IP: 198.51.100.1                 Public IP: 203.0.113.5
WireGuard IP: 10.100.0.1/24             WireGuard IP: 10.100.0.2/24
      |                                       |
      +========== Encrypted UDP Tunnel ======+
                  (Port 51820)
                       |
        Routing: AllowedIPs = 10.100.0.0/24
```

---

## 2. Production WireGuard Configuration Patterns

### A. Hub / Gateway Node Configuration (`/etc/wireguard/wg0.conf`)

```ini
[Interface]
# Gateway internal overlay address
Address = 10.100.0.1/24
ListenPort = 51820
PrivateKey = <GATEWAY_PRIVATE_KEY>

# Forwarding & NAT iptables rules
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
SaveConfig = false

# Peer 1: Remote Cloud Worker
[Peer]
PublicKey = <WORKER_NODE_PUBLIC_KEY>
AllowedIPs = 10.100.0.2/32
PersistentKeepalive = 25

# Peer 2: Branch Office Gateway (Subnet Routing)
[Peer]
PublicKey = <BRANCH_GW_PUBLIC_KEY>
# Route both the tunnel IP and the remote office LAN
AllowedIPs = 10.100.0.3/32, 192.168.50.0/24
PersistentKeepalive = 25
```

### B. Automated Peer Provisioning Script (Bash / Linux)

```bash
#!/usr/bin/env bash
set -euo pipefail

PEER_NAME="${1:?Usage: $0 <peer_name> <tunnel_ip>}"
PEER_IP="${2:?Usage: $0 <peer_name> <tunnel_ip>}"

CONFIG_DIR="/etc/wireguard/peers/${PEER_NAME}"
mkdir -p "${CONFIG_DIR}"
chmod 700 "${CONFIG_DIR}"

# 1. Generate keypair
wg genkey | tee "${CONFIG_DIR}/privatekey" | wg pubkey > "${CONFIG_DIR}/publickey"
wg genpsk > "${CONFIG_DIR}/preshared.key"

PRIV_KEY=$(cat "${CONFIG_DIR}/privatekey")
PUB_KEY=$(cat "${CONFIG_DIR}/publickey")
PSK=$(cat "${CONFIG_DIR}/preshared.key")

echo "Created keys for ${PEER_NAME}:"
echo "Public Key: ${PUB_KEY}"

# 2. Generate client wg-quick configuration
cat <<EOF > "${CONFIG_DIR}/${PEER_NAME}.conf"
[Interface]
Address = ${PEER_IP}/24
PrivateKey = ${PRIV_KEY}
DNS = 10.100.0.1

[Peer]
PublicKey = $(cat /etc/wireguard/server_publickey)
PresharedKey = ${PSK}
Endpoint = vpn.example.com:51820
AllowedIPs = 10.100.0.0/24
PersistentKeepalive = 25
EOF

chmod 600 "${CONFIG_DIR}/${PEER_NAME}.conf"
echo "Configuration generated at ${CONFIG_DIR}/${PEER_NAME}.conf"
```

---

## 3. Operational Best Practices

1. **Kernel Forwarding:** Ensure `net.ipv4.ip_forward = 1` is persistently enabled in `/etc/sysctl.d/99-wireguard.conf`.
2. **NAT Keepalive:** For peers behind dynamic NAT or firewalls, set `PersistentKeepalive = 25` to keep NAT mappings alive.
3. **Restricted AllowedIPs:** Avoid setting `AllowedIPs = 0.0.0.0/0` unless routing all internet traffic (full tunnel); for inter-service communication, specify only the cluster subnets.
