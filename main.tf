# terraform/main.tf
# Provisions an EC2 instance + security group to host the Movie Recommender

terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Store state remotely (uncomment after creating the S3 bucket)
  # backend "s3" {
  #   bucket = "movie-recommender-tfstate"
  #   key    = "prod/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

provider "aws" {
  region = var.aws_region
}

# ─── Variables ───────────────────────────────────────────────────────────────

variable "aws_region" {
  description = "AWS region to deploy in"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.small"
}

variable "key_name" {
  description = "Name of your EC2 key pair for SSH access"
  type        = string
}

variable "tmdb_api_key" {
  description = "TMDB API key (sensitive)"
  type        = string
  sensitive   = true
}

# ─── Data Sources ─────────────────────────────────────────────────────────────

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-22.04-amd64-server-*"]
  }
}

# ─── Security Group ───────────────────────────────────────────────────────────

resource "aws_security_group" "movie_recommender_sg" {
  name        = "movie-recommender-sg"
  description = "Security group for Movie Recommender app"

  # Allow Streamlit
  ingress {
    description = "Streamlit port"
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow SSH (restrict to your IP in production!)
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # ⚠️ Change to your IP/32 in production
  }

  # Allow HTTP
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "movie-recommender-sg"
    Environment = "production"
    Project     = "movie-recommender"
  }
}

# ─── EC2 Instance ─────────────────────────────────────────────────────────────

resource "aws_instance" "movie_recommender" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.movie_recommender_sg.id]

  # Bootstrap script: install Docker and run the app
  user_data = <<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y docker.io curl
    systemctl start docker
    systemctl enable docker
    usermod -aG docker ubuntu

    # Pull and run the latest image
    docker pull ${var.dockerhub_username}/movie-recommender:latest
    docker run -d \
      --name movie-recommender \
      -p 8501:8501 \
      -e TMDB_API_KEY=${var.tmdb_api_key} \
      --restart unless-stopped \
      ${var.dockerhub_username}/movie-recommender:latest
  EOF

  tags = {
    Name        = "movie-recommender-server"
    Environment = "production"
    Project     = "movie-recommender"
    ManagedBy   = "terraform"
  }
}

variable "dockerhub_username" {
  description = "Docker Hub username"
  type        = string
}

# ─── Outputs ──────────────────────────────────────────────────────────────────

output "instance_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.movie_recommender.public_ip
}

output "app_url" {
  description = "URL to access the Movie Recommender app"
  value       = "http://${aws_instance.movie_recommender.public_ip}:8501"
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ~/.ssh/${var.key_name}.pem ubuntu@${aws_instance.movie_recommender.public_ip}"
}
