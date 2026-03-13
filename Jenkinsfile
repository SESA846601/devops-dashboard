pipeline {
    agent any

    stages {

        stage('Clone Repository') {
            steps {
                git 'https://github.com/sesa846601/devops-dashboard.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t devops-dashboard .'
            }
        }

        stage('Stop Old Container') {
            steps {
                sh 'docker stop devops-dashboard || true'
                sh 'docker rm devops-dashboard || true'
            }
        }

        stage('Run New Container') {
            steps {
                sh 'docker run -d -p 5000:5000 --name devops-dashboard devops-dashboard'
            }
        }

    }
}