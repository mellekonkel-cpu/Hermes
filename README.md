# Hermes Agent — 青桑的 Hermes 分身

一键部署 Hermes Agent，继承记忆与能力。

## 快速开始

### 1. 安装 WSL（Windows）

管理员 PowerShell：

```powershell
wsl --install -d Ubuntu
```

重启电脑。

### 2. 安装 Hermes

在 WSL 终端执行：

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

### 3. 部署配置

```bash
git clone https://github.com/mellekonkel-cpu/Hermes.git ~/Hermes
cd ~/Hermes
bash setup.sh
```

### 4. 配置 API Key

```bash
cp .env.example /opt/data/.env
# 编辑 .env 填入你的 API Key
```

### 5. 验证

```bash
hermes doctor
```

---

## 目录结构

```
Hermes/
├── .hermes/config.yaml   # Hermes 配置（脱敏）
├── .env.example          # 环境变量模板
├── SOUL.md               # 人格定义
├── skills/               # 所有技能文件
├── setup.sh              # 部署脚本
└── README.md             # 本文件
```
