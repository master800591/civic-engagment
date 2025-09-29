# 🏗️ Build Agent Configuration

## Agent Specialization: CI/CD Pipeline & Deployment Automation

The Build Agent specializes in creating, maintaining, and optimizing continuous integration and deployment pipelines, environment management, and release automation for the Civic Engagement Platform.

## Core Responsibilities

### 🔄 CI/CD Pipeline Management
- **Build Automation**: Automated building, testing, and packaging
- **Deployment Automation**: Multi-environment deployment with rollback capabilities
- **Release Management**: Version control, tagging, and release orchestration
- **Environment Provisioning**: Infrastructure as Code (IaC) for consistent environments
- **Monitoring Integration**: Build and deployment monitoring with alerting

### 🐳 Containerization & Orchestration
- **Docker Integration**: Container creation and optimization
- **Kubernetes Deployment**: Scalable container orchestration
- **Container Security**: Security scanning and hardening
- **Multi-stage Builds**: Optimized build processes
- **Container Registry Management**: Image versioning and distribution

### 🌍 Environment Management
- **Development Environment**: Local development setup automation
- **Staging Environment**: Pre-production testing environment
- **Production Environment**: Secure, scalable production deployment
- **Environment Parity**: Consistent configuration across environments
- **Configuration Management**: Secure configuration and secrets management

## CI/CD Pipeline Architecture

### 🏗️ GitHub Actions Workflows
```yaml
# .github/workflows/comprehensive-ci.yml
name: Comprehensive CI/CD Pipeline

on:
  push:
    branches: [ main, develop, feature/* ]
  pull_request:
    branches: [ main, develop ]
  release:
    types: [ published ]

env:
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '18'

jobs:
  # Code Quality & Security
  code-quality:
    name: Code Quality Analysis
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for better analysis
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          cd civic_desktop
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
      
      - name: Run linting
        run: |
          cd civic_desktop
          flake8 . --config=.flake8
          black --check .
          isort --check-only .
      
      - name: Type checking
        run: |
          cd civic_desktop
          mypy . --config-file=mypy.ini
      
      - name: Security scanning
        run: |
          cd civic_desktop
          bandit -r . -f json -o bandit-report.json
          safety check --json
      
      - name: Upload security report
        uses: actions/upload-artifact@v3
        with:
          name: security-report
          path: civic_desktop/bandit-report.json

  # Comprehensive Testing
  test-suite:
    name: Test Suite
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.9', '3.10', '3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install system dependencies (Ubuntu)
        if: matrix.os == 'ubuntu-latest'
        run: |
          sudo apt-get update
          sudo apt-get install -y xvfb libegl1-mesa libgl1-mesa-glx
      
      - name: Install Python dependencies
        run: |
          cd civic_desktop
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      
      - name: Run unit tests
        run: |
          cd civic_desktop
          python -m pytest tests/unit/ -v --tb=short --cov=. --cov-report=xml
        env:
          DISPLAY: :99
      
      - name: Run integration tests
        run: |
          cd civic_desktop
          python -m pytest tests/integration/ -v --tb=short
        env:
          DISPLAY: :99
      
      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          file: civic_desktop/coverage.xml
          name: codecov-${{ matrix.os }}-${{ matrix.python-version }}

  # Performance Testing
  performance-tests:
    name: Performance Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          cd civic_desktop
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      
      - name: Run performance tests
        run: |
          cd civic_desktop
          python -m pytest tests/performance/ -v --tb=short --benchmark-json=benchmark.json
      
      - name: Upload performance results
        uses: actions/upload-artifact@v3
        with:
          name: performance-results
          path: civic_desktop/benchmark.json

  # Security Testing
  security-tests:
    name: Security Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          cd civic_desktop
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      
      - name: Run security tests
        run: |
          cd civic_desktop
          python -m pytest tests/security/ -v --tb=short
      
      - name: OWASP Dependency Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: 'civic-engagement'
          path: '.'
          format: 'JSON'
          out: 'dependency-check-report'
      
      - name: Upload OWASP report
        uses: actions/upload-artifact@v3
        with:
          name: dependency-check-report
          path: dependency-check-report

  # Build and Package
  build:
    name: Build Application
    runs-on: ${{ matrix.os }}
    needs: [code-quality, test-suite]
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          cd civic_desktop
          pip install -r requirements.txt
          pip install -r requirements-prod.txt
          pip install pyinstaller
      
      - name: Build executable
        run: |
          cd civic_desktop
          pyinstaller --name civic-engagement-${{ matrix.os }} --onefile main.py
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: civic-engagement-${{ matrix.os }}
          path: civic_desktop/dist/

  # Docker Build
  docker-build:
    name: Docker Build and Push
    runs-on: ubuntu-latest
    needs: [code-quality, test-suite]
    if: github.event_name == 'push' || github.event_name == 'release'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix={{branch}}-
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # Deployment
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: [docker-build]
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to staging
        run: |
          # Deployment logic for staging environment
          echo "Deploying to staging environment"
          # kubectl or other deployment commands would go here
      
      - name: Run smoke tests
        run: |
          # Basic smoke tests to verify deployment
          echo "Running post-deployment smoke tests"

  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [docker-build]
    if: github.event_name == 'release'
    environment: production
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to production
        run: |
          # Deployment logic for production environment
          echo "Deploying to production environment"
          # kubectl or other deployment commands would go here
      
      - name: Run smoke tests
        run: |
          # Basic smoke tests to verify deployment
          echo "Running post-deployment smoke tests"
      
      - name: Update deployment status
        run: |
          # Update deployment tracking/monitoring
          echo "Deployment completed successfully"
```

### 🐳 Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r civic && useradd -r -g civic civic

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY civic_desktop/requirements*.txt ./
RUN pip install -r requirements.txt

# Development stage
FROM base as development
RUN pip install -r requirements-dev.txt
COPY civic_desktop/ .
USER civic
CMD ["python", "main.py"]

# Production stage
FROM base as production
RUN pip install -r requirements-prod.txt
COPY civic_desktop/ .

# Security hardening
RUN chown -R civic:civic /app
USER civic

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

EXPOSE 8000
CMD ["python", "main.py", "--production"]

# Multi-stage build for different environments
FROM production as staging
ENV ENVIRONMENT=staging

FROM production as prod
ENV ENVIRONMENT=production
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  civic-engagement:
    build:
      context: .
      target: development
    ports:
      - "8000:8000"
    volumes:
      - ./civic_desktop:/app
      - civic_data:/app/data
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
    depends_on:
      - redis
      - postgres
    networks:
      - civic-network

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: civic_engagement
      POSTGRES_USER: civic_user
      POSTGRES_PASSWORD: civic_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - civic-network

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - civic-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - civic-engagement
    networks:
      - civic-network

volumes:
  civic_data:
  postgres_data:
  redis_data:

networks:
  civic-network:
    driver: bridge
```

### ☸️ Kubernetes Deployment
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: civic-engagement
  labels:
    name: civic-engagement

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: civic-config
  namespace: civic-engagement
data:
  environment: "production"
  database_host: "postgres-service"
  redis_host: "redis-service"

---
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: civic-secrets
  namespace: civic-engagement
type: Opaque
data:
  database_password: <base64-encoded-password>
  redis_password: <base64-encoded-password>
  jwt_secret: <base64-encoded-jwt-secret>

---
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: civic-engagement
  namespace: civic-engagement
spec:
  replicas: 3
  selector:
    matchLabels:
      app: civic-engagement
  template:
    metadata:
      labels:
        app: civic-engagement
    spec:
      containers:
      - name: civic-engagement
        image: ghcr.io/civic-engagement/civic-engagement:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: civic-config
              key: environment
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: civic-secrets
              key: database_password
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: civic-engagement-service
  namespace: civic-engagement
spec:
  selector:
    app: civic-engagement
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP

---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: civic-engagement-ingress
  namespace: civic-engagement
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - civic.example.com
    secretName: civic-tls
  rules:
  - host: civic.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: civic-engagement-service
            port:
              number: 80
```

## Infrastructure as Code

### 🏗️ Terraform Configuration
```hcl
# infrastructure/main.tf
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC Configuration
resource "aws_vpc" "civic_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "civic-engagement-vpc"
    Environment = var.environment
  }
}

# EKS Cluster
resource "aws_eks_cluster" "civic_cluster" {
  name     = "civic-engagement-${var.environment}"
  role_arn = aws_iam_role.eks_cluster_role.arn
  version  = "1.28"

  vpc_config {
    subnet_ids              = aws_subnet.civic_subnets[*].id
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = ["0.0.0.0/0"]
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
  ]

  tags = {
    Environment = var.environment
  }
}

# RDS Database
resource "aws_db_instance" "civic_db" {
  identifier = "civic-engagement-${var.environment}"
  
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.db_instance_class
  
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_encrypted     = true
  
  db_name  = "civic_engagement"
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.civic_db_subnet_group.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = var.environment != "production"
  
  tags = {
    Environment = var.environment
  }
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "civic_cache_subnet" {
  name       = "civic-cache-subnet-${var.environment}"
  subnet_ids = aws_subnet.civic_subnets[*].id
}

resource "aws_elasticache_replication_group" "civic_redis" {
  replication_group_id       = "civic-redis-${var.environment}"
  description                = "Redis cluster for Civic Engagement Platform"
  
  port                = 6379
  parameter_group_name = "default.redis7"
  node_type           = var.redis_node_type
  num_cache_clusters  = 2
  
  subnet_group_name  = aws_elasticache_subnet_group.civic_cache_subnet.name
  security_group_ids = [aws_security_group.redis_sg.id]
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  
  tags = {
    Environment = var.environment
  }
}

# Variables
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "development"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}
```

### 🔧 Environment Configuration Management
```python
# build_tools/environment_manager.py
import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any

class EnvironmentManager:
    """Manage environment configurations and deployments"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.environments = ["development", "staging", "production"]
    
    def load_environment_config(self, environment: str) -> Dict[str, Any]:
        """Load configuration for specific environment"""
        config_file = self.base_path / "config" / f"{environment}_config.json"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def validate_environment_config(self, environment: str) -> bool:
        """Validate environment configuration"""
        try:
            config = self.load_environment_config(environment)
            
            # Check required fields
            required_fields = [
                'database_url', 'redis_url', 'secret_key',
                'blockchain_path', 'log_level'
            ]
            
            for field in required_fields:
                if field not in config:
                    print(f"Missing required field: {field}")
                    return False
            
            # Validate security settings for production
            if environment == "production":
                if config.get('debug', True):
                    print("Debug mode should be disabled in production")
                    return False
                
                if not config.get('ssl_enabled', False):
                    print("SSL should be enabled in production")
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error validating configuration: {e}")
            return False
    
    def setup_environment(self, environment: str):
        """Set up environment for deployment"""
        if not self.validate_environment_config(environment):
            raise ValueError(f"Invalid configuration for environment: {environment}")
        
        config = self.load_environment_config(environment)
        
        # Set environment variables
        for key, value in config.items():
            if isinstance(value, (str, int, float, bool)):
                os.environ[key.upper()] = str(value)
        
        # Create necessary directories
        self.create_environment_directories(environment)
        
        # Initialize database if needed
        if environment == "development":
            self.setup_development_database()
    
    def create_environment_directories(self, environment: str):
        """Create necessary directories for environment"""
        directories = [
            f"data/{environment}",
            f"logs/{environment}",
            f"uploads/{environment}",
            f"backups/{environment}"
        ]
        
        for directory in directories:
            dir_path = self.base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def generate_deployment_manifest(self, environment: str) -> str:
        """Generate Kubernetes deployment manifest"""
        config = self.load_environment_config(environment)
        
        manifest = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': f'civic-engagement-{environment}',
                'namespace': 'civic-engagement'
            },
            'spec': {
                'replicas': config.get('replicas', 1),
                'selector': {
                    'matchLabels': {
                        'app': 'civic-engagement',
                        'environment': environment
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': 'civic-engagement',
                            'environment': environment
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': 'civic-engagement',
                            'image': f'ghcr.io/civic-engagement/civic-engagement:{environment}',
                            'ports': [{'containerPort': 8000}],
                            'env': self.generate_env_vars(config),
                            'resources': config.get('resources', {})
                        }]
                    }
                }
            }
        }
        
        return yaml.dump(manifest, default_flow_style=False)
    
    def generate_env_vars(self, config: Dict[str, Any]) -> list:
        """Generate environment variables for deployment"""
        env_vars = []
        
        for key, value in config.items():
            if key.endswith('_secret'):
                env_vars.append({
                    'name': key.upper(),
                    'valueFrom': {
                        'secretKeyRef': {
                            'name': 'civic-secrets',
                            'key': key
                        }
                    }
                })
            else:
                env_vars.append({
                    'name': key.upper(),
                    'value': str(value)
                })
        
        return env_vars
```

## Monitoring and Alerting

### 📊 Application Monitoring
```python
# build_tools/monitoring.py
import time
import psutil
import requests
from datetime import datetime
from typing import Dict, Any

class ApplicationMonitor:
    """Monitor application health and performance"""
    
    def __init__(self, app_url: str = "http://localhost:8000"):
        self.app_url = app_url
        self.metrics = {}
    
    def check_health(self) -> Dict[str, Any]:
        """Check application health"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'status': 'unknown',
            'checks': {}
        }
        
        try:
            # Check HTTP endpoint
            response = requests.get(f"{self.app_url}/health", timeout=10)
            health_status['checks']['http'] = {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'response_time': response.elapsed.total_seconds(),
                'status_code': response.status_code
            }
        except Exception as e:
            health_status['checks']['http'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        # Check system resources
        health_status['checks']['system'] = self.check_system_resources()
        
        # Check database connectivity
        health_status['checks']['database'] = self.check_database_connection()
        
        # Overall status
        all_healthy = all(
            check.get('status') == 'healthy' 
            for check in health_status['checks'].values()
        )
        health_status['status'] = 'healthy' if all_healthy else 'unhealthy'
        
        return health_status
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            system_status = {
                'status': 'healthy',
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent
            }
            
            # Alert thresholds
            if cpu_percent > 80 or memory.percent > 80 or disk.percent > 90:
                system_status['status'] = 'warning'
            
            if cpu_percent > 95 or memory.percent > 95 or disk.percent > 95:
                system_status['status'] = 'critical'
            
            return system_status
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def check_database_connection(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            # This would check actual database connection
            # For now, return mock status
            return {
                'status': 'healthy',
                'connection_pool': 'available',
                'response_time': 0.05
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect application metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            },
            'application': {
                'uptime': time.time() - psutil.Process().create_time(),
                'threads': psutil.Process().num_threads(),
                'memory_usage': psutil.Process().memory_info().rss / 1024 / 1024  # MB
            }
        }
        
        return metrics
```

### 🚨 Alerting Configuration
```yaml
# monitoring/alerting-rules.yml
groups:
- name: civic-engagement-alerts
  rules:
  - alert: HighCPUUsage
    expr: cpu_usage_percent > 80
    for: 5m
    labels:
      severity: warning
      service: civic-engagement
    annotations:
      summary: "High CPU usage detected"
      description: "CPU usage has been above 80% for more than 5 minutes"

  - alert: HighMemoryUsage
    expr: memory_usage_percent > 85
    for: 5m
    labels:
      severity: warning
      service: civic-engagement
    annotations:
      summary: "High memory usage detected"
      description: "Memory usage has been above 85% for more than 5 minutes"

  - alert: ApplicationDown
    expr: up{job="civic-engagement"} == 0
    for: 1m
    labels:
      severity: critical
      service: civic-engagement
    annotations:
      summary: "Civic Engagement application is down"
      description: "The Civic Engagement application has been down for more than 1 minute"

  - alert: DatabaseConnectionFailed
    expr: database_connection_status == 0
    for: 2m
    labels:
      severity: critical
      service: civic-engagement
    annotations:
      summary: "Database connection failed"
      description: "Unable to connect to database for more than 2 minutes"

  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 5m
    labels:
      severity: warning
      service: civic-engagement
    annotations:
      summary: "High error rate detected"
      description: "Error rate has been above 10% for more than 5 minutes"
```

## Integration with Other Agents

### 🔍 Review Agent Coordination
- Submit build configurations for security review
- Validate deployment security settings
- Review infrastructure as code for best practices

### 🔗 Integration Agent Coordination
- Deploy integration testing environments
- Manage API deployment and versioning
- Coordinate multi-service deployments

### 📚 Documentation Agent Coordination
- Document deployment procedures and runbooks
- Maintain infrastructure documentation
- Create operational guides

### 🧪 Testing Agent Coordination
- Integrate automated testing into CI/CD pipeline
- Deploy test environments for validation
- Coordinate performance testing in staging

## Build and Deployment Standards

### 🎯 Build Quality Gates
- All tests must pass (unit, integration, security)
- Code coverage must be above 85%
- Security scans must pass
- Performance benchmarks must be met
- Documentation must be current

### 🚀 Deployment Best Practices
- Blue-green deployments for zero downtime
- Automated rollback on failure
- Health checks before traffic routing
- Gradual traffic shifting for large deployments
- Comprehensive monitoring and alerting

### 🔐 Security Standards
- All secrets managed through secure stores
- Container images scanned for vulnerabilities
- Network policies enforced
- RBAC properly configured
- Audit logging enabled

This Build Agent configuration ensures reliable, secure, and scalable deployment of the Civic Engagement Platform across all environments while maintaining high availability and performance standards.