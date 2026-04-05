# 🎬 Movie Recommender System

![CI/CD](https://github.com/YOUR_USERNAME/movie-recommender/actions/workflows/ci-cd.yml/badge.svg)
![Docker Pulls](https://img.shields.io/docker/pulls/YOUR_DOCKERHUB_USERNAME/movie-recommender)
![Python](https://img.shields.io/badge/python-3.9-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.37.1-red)
![License](https://img.shields.io/badge/license-MIT-green)

A content-based movie recommendation engine built with **Streamlit** and deployed with a full **DevOps pipeline** including Docker, GitHub Actions CI/CD, Terraform (IaC), and cloud monitoring.

---

## 🌐 Live Demo

👉 **[Try it here →](http://YOUR_EC2_IP:8501)**

---

## 🏗️ Architecture

```
┌──────────────┐    push     ┌─────────────────────────────────────────┐
│   Developer  │────────────▶│           GitHub Actions CI/CD          │
└──────────────┘             │                                         │
                             │  ┌──────────┐  ┌────────┐  ┌────────┐  │
                             │  │  Lint &  │─▶│  Build │─▶│ Deploy │  │
                             │  │   Test   │  │ Docker │  │  EC2   │  │
                             │  └──────────┘  └────────┘  └────┬───┘  │
                             └────────────────────────────────-│───────┘
                                                               │
                             ┌─────────────────────────────────▼───────┐
                             │              AWS EC2 Instance            │
                             │  ┌────────────────────────────────────┐ │
                             │  │  Docker Container: Streamlit App   │ │
                             │  │  Port: 8501                        │ │
                             │  └────────────────────────────────────┘ │
                             │  ┌────────────┐  ┌───────────────────┐  │
                             │  │ Prometheus │  │     Grafana       │  │
                             │  │ Port: 9090 │  │    Port: 3000     │  │
                             │  └────────────┘  └───────────────────┘  │
                             └─────────────────────────────────────────┘
```

---

## 🚀 Tech Stack

| Layer | Technology |
|---|---|
| **App** | Python 3.9, Streamlit, scikit-learn, pandas |
| **ML** | Content-based filtering, cosine similarity |
| **API** | TMDB API |
| **Container** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions |
| **IaC** | Terraform |
| **Cloud** | AWS EC2 |
| **Monitoring** | Prometheus + Grafana |
| **Security** | Trivy vulnerability scanning, non-root Docker user |

---

## 📁 Project Structure

```
movie-recommender/
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # GitHub Actions pipeline
├── terraform/
│   └── main.tf                # AWS infrastructure as code
├── monitoring/
│   └── prometheus.yml         # Prometheus scrape config
├── tests/
│   └── test_app.py            # Unit tests (pytest)
├── app.py                     # Main Streamlit application
├── Dockerfile                 # Optimized, non-root Docker image
├── docker-compose.yml         # Local dev + monitoring stack
├── requirements.txt           # Python dependencies
└── README.md
```

---

## ⚡ Quick Start

### Run Locally with Docker

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/movie-recommender.git
cd movie-recommender

# 2. Set your TMDB API key
echo "TMDB_API_KEY=your_key_here" > .env

# 3. Build and run
docker compose up --build

# 4. Open in browser
open http://localhost:8501
```

### Run with Monitoring Stack

```bash
docker compose --profile monitoring up --build
# App:        http://localhost:8501
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3000  (admin / admin)
```

---

## 🔄 CI/CD Pipeline

Every push to `main` triggers:

```
┌──────────────┐     ┌─────────────┐     ┌──────────────────┐     ┌──────────┐
│  Lint & Test │────▶│  Trivy Scan │────▶│ Build & Push     │────▶│  Deploy  │
│  (flake8 +   │     │  (security) │     │ Docker → Hub     │     │  to EC2  │
│   pytest)    │     │             │     │                  │     │          │
└──────────────┘     └─────────────┘     └──────────────────┘     └──────────┘
```

### Required GitHub Secrets

| Secret | Description |
|---|---|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
| `TMDB_API_KEY` | TMDB API key |
| `EC2_HOST` | EC2 public IP |
| `EC2_USER` | EC2 SSH user (e.g., `ubuntu`) |
| `EC2_SSH_KEY` | Private SSH key content |

---

## 🏗️ Infrastructure (Terraform)

Provision AWS infrastructure with one command:

```bash
cd terraform

terraform init
terraform plan -var="key_name=your-keypair" \
               -var="tmdb_api_key=your-key" \
               -var="dockerhub_username=your-username"
terraform apply
```

**What it creates:**
- EC2 `t3.small` instance (Ubuntu 22.04)
- Security group (ports 22, 80, 8501)
- Bootstraps Docker + runs the container automatically

---

## 🧪 Running Tests

```bash
pip install pytest pytest-cov
pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## 🔒 Security Highlights

- ✅ Non-root user inside Docker container
- ✅ Secrets managed via GitHub Secrets / environment variables (never hardcoded)
- ✅ Trivy image vulnerability scanning in CI
- ✅ Docker health checks configured
- ✅ API key loaded from environment, not source code

---

## 📊 Monitoring

| Tool | Purpose | Port |
|---|---|---|
| Prometheus | Metrics collection | 9090 |
| Grafana | Dashboards & alerts | 3000 |

---

## 👨‍💻 Author

**Your Name** — [LinkedIn](https://linkedin.com/in/yourprofile) | [GitHub](https://github.com/YOUR_USERNAME)
