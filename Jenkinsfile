pipeline {
    agent any

    stages {

        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/sesa846601/devops-dashboard.git'
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    docker run --rm \
                        -v $(pwd)/app:/app \
                        -w /app \
                        python:3.9-slim \
                        sh -c "pip install flask pytest --quiet && pytest tests/ -v"
                '''
            }
        }

        stage('Generate Build Info') {
            steps {
                script {
                    def commitHash = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    def buildTime  = sh(script: 'date "+%Y-%m-%d %H:%M:%S"', returnStdout: true).trim()
                    def branch     = sh(script: 'git rev-parse --abbrev-ref HEAD', returnStdout: true).trim()

                    writeFile file: 'build_info.json', text: """{
  "build_number": "${env.BUILD_NUMBER}",
  "git_commit": "${commitHash}",
  "git_branch": "${branch}",
  "build_time": "${buildTime}",
  "status": "success"
}"""
                    echo "Build info written → build #${env.BUILD_NUMBER} | commit ${commitHash}"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t devops-dashboard .'
            }
        }

        stage('Stop Old Container') {
            steps {
                sh 'docker sop devops-dashboard || true'
                sh 'docker rm   devops-dashboard || true'
            }
        }

        stage('Run New Container') {
            steps {
                sh 'docker run -d -p 5000:5000 --name devops-dashboard devops-dashboard'
            }
        }

    }

    post {
        success {
            echo "✅ Deployment #${env.BUILD_NUMBER} completed successfully."
        }
        failure {
            echo "❌ Deployment #${env.BUILD_NUMBER} failed. Check stage logs above."
        }
    }
}