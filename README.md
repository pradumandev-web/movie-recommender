# 🎬 Movie Recommender System

![CI/CD](https://github.com/pradumandev-web/movie-recommender/actions/workflows/ci-cd.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.9-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.37.1-red)
![Docker](https://img.shields.io/badge/docker-ready-blue?logo=docker)
![AWS](https://img.shields.io/badge/AWS-EC2%20%2B%20S3-orange?logo=amazonaws)
![Terraform](https://img.shields.io/badge/IaC-Terraform-purple?logo=terraform)
![License](https://img.shields.io/badge/license-MIT-green)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Praduman-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/praduman-dev-9b6b66367)

A content-based movie recommendation engine built with **Streamlit** and deployed with a full **DevOps pipeline** including Docker, GitHub Actions CI/CD, AWS S3 + EC2, and Terraform IaC.

---

## 🌐 Live Demo

👉 **[Try it here → http://3.235.30.195:8501](http://3.235.30.195:8501)**

---

## 🏗️ Architecture
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
│              AWS EC2 t3.micro            │
│  ┌────────────────────────────────────┐ │
│  │  Docker Container: Streamlit App   │ │
│  │  Port: 8501                        │ │
│  └────────────────────────────────────┘ │
│                                         │
│         AWS S3 (Model Storage)          │
│  movie_dict.pkl + similarity.pkl        │
└─────────────────────────────────────────┘

---

## 🚀 Tech Stack

| Layer | Technology |
|---|---|
| **App** | Python 3.9, Streamlit, scikit-learn, pandas |
| **ML** | Content-based filtering, cosine similarity |
| **API** | TMDB API (movie posters, ratings, details) |
| **Container** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions (4-stage pipeline) |
| **Storage** | AWS S3 (184MB model files) |
| **Cloud** | AWS EC2 t3.micro (Free Tier) |
| **IaC** | Terraform |
| **Security** | Trivy vulnerability scanning, non-root Docker user |
| **Testing** | pytest (12 tests) |

---

## 📁 Project Structure
movie-recommender/
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # GitHub Actions 4-stage pipeline
├── terraform/
│   └── main.tf                # AWS EC2 + Security Group IaC
├── monitoring/
│   └── prometheus.yml         # Prometheus scrape config
├── tests/
│   └── test_app.py            # 12 unit tests (pytest)
├── app.py                     # Streamlit application
├── Dockerfile                 # Optimized, non-root Docker image
├── docker-compose.yml         # Local dev stack
├── requirements.txt           # Python dependencies
└── README.md

---

## ⚡ Quick Start

### Run Locally with Docker
```bash
# 1. Clone the repo
git clone https://github.com/pradumandev-web/movie-recommender.git
cd movie-recommender

# 2. Set your environment variables
cp .env.example .env
# Edit .env with your TMDB_API_KEY, AWS credentials, S3 bucket name

# 3. Build and run
docker compose up --build

# 4. Open in browser
open http://localhost:8501
```

---

## 🔄 CI/CD Pipeline

Every push to `main` automatically triggers:
┌──────────────┐  ┌─────────────┐  ┌──────────────────┐  ┌──────────┐
│  Lint & Test │─▶│  Trivy Scan │─▶│ Build & Push     │─▶│  Deploy  │
│  (flake8 +   │  │  (security) │  │ Docker → Hub     │  │  to EC2  │
│   pytest)    │  │             │  │                  │  │          │
└──────────────┘  └─────────────┘  └──────────────────┘  └──────────┘

### GitHub Secrets Required

| Secret | Description |
|---|---|
| `TMDB_API_KEY` | TMDB API key |
| `DOCKERHUB_USERNAME` | Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
| `EC2_HOST` | EC2 public IP |
| `EC2_USER` | EC2 SSH user (ubuntu) |
| `EC2_SSH_KEY` | Private SSH key |
| `S3_BUCKET_NAME` | S3 bucket name |

---

## 🏗️ Infrastructure (Terraform)
```bash
cd terraform
terraform init
terraform apply
```

**Creates:**
- EC2 `t3.micro` instance (Ubuntu 22.04)
- Security group (ports 22, 80, 8501)
- Auto-bootstraps Docker and runs the container

---

## 🧪 Tests
```bash
pip install pytest pytest-cov
pytest tests/ -v --cov=app
```

12 tests covering recommendation logic, data validation and environment checks.

---

## 🔒 Security

- ✅ Non-root user inside Docker container
- ✅ Secrets via GitHub Secrets / environment variables
- ✅ Trivy image vulnerability scanning in CI
- ✅ Docker health checks
- ✅ AWS IAM role with minimal S3 permissions

---

## 💰 Cost

Runs completely on **AWS Free Tier — $0/month**:
- EC2 t3.micro — 750 hrs/month free
- S3 — 5GB free (using 188MB)
- Data transfer — 100GB/month free

---

## 👨‍💻 Author

**Praduman** — [![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/praduman-dev-9b6b66367) | [![GitHub](https://img.shields.io/badge/GitHub-pradumandev--web-black?style=flat&logo=github)](https://github.com/pradumandev-web)