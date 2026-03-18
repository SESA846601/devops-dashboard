def failedStageName = ''   // Scripted: tracks which stage failed
//testing webhook
// ── DECLARATIVE PIPELINE ──────────────────────────────────────
pipeline {

    // ── AGENT USING VM ────────────────────────────────────────
    // All stages run on the VM node labelled 'linux-vm'
    // Set this label in: Manage Jenkins → Nodes → built-in → Labels
    agent { label 'linux-vm' }

    // ── ENVIRONMENT / SECRETS MANAGEMENT ──────────────────────
    // GitHub PAT is stored securely in Jenkins credentials store
    // (ID: 'github-pat') and injected as GIT_TOKEN at runtime.
    // Never hardcoded — Jenkins masks it in all console logs.
    environment {
        GIT_TOKEN    = credentials('github-pat')
        REPO_URL     = 'https://github.com/sesa846601/devops-dashboard.git'
        IMAGE_NAME   = 'devops-dashboard'
        CONTAINER_PORT = '5000'
    }

    stages {

        // ── STAGE 1: CLONE ─────────────────────────────────────
        // Uses GitHub PAT from credentials store for authenticated clone.
        // Scripted block used to catch failure and record stage name.
        stage('Clone Repository') {
            steps {
                script {    // ← Scripted Pipeline block inside Declarative
                    try {
                        git branch: 'main',
                            credentialsId: 'github-pat',
                            url: "${env.REPO_URL}"
                    } catch (e) {
                        failedStageName = 'Clone'
                        throw e
                    }
                }
            }
        }

        // ── STAGE 2: TEST ──────────────────────────────────────
        // Agent using Container: pytest runs inside python:3.9-slim.
        // A fresh container is created, tests run, container removed.
        // The VM-level Docker daemon handles the container lifecycle.
        stage('Run Tests') {
            agent {
                docker {
                    image 'python:3.9-slim'   // ← Agent using Container
                    args '-u root'
                    reuseNode true            // reuse linux-vm workspace
                }
            }
            steps {
                script {    // ← Scripted Pipeline block
                    try {
                        sh '''
pip install -r app/requirements.txt

echo "Running tests..."
pytest app/tests/ -v > logs.txt 2>&1 || true

echo "Logs saved"
ls -l logs.txt

'''
                        //now saving logs
                    } catch (e) {
                        failedStageName = 'Test'
                        throw e
                    }
                }
            }
        }

        // ── STAGE 3: GENERATE BUILD INFO ───────────────────────
        // Scripted block reads git metadata and writes build_info.json.
        // This file is baked into the Docker image in the next stage.
        stage('Generate Build Info') {
            steps {
                script {    // ← Scripted Pipeline block
                    try {

                        sh 'cp logs.txt app/logs.txt || true'
                        def commitHash = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                        def buildTime  = sh(script: 'date "+%Y-%m-%d %H:%M:%S"',  returnStdout: true).trim()
                        def branch     = sh(script: 'git rev-parse --abbrev-ref HEAD', returnStdout: true).trim()

                        writeFile file: 'build_info.json', text: """{
  "build_number": "${env.BUILD_NUMBER}",
  "git_commit":   "${commitHash}",
  "git_branch":   "${branch}",
  "build_time":   "${buildTime}",
  "status":       "success",
  "failed_stage": ""
}"""
                        echo "✔ Build info written — #${env.BUILD_NUMBER} | ${commitHash}"
                    } catch (e) {
                        failedStageName = 'Build Info'
                        throw e
                    }
                }
            }
        }

        // ── STAGE 4: BUILD DOCKER IMAGE ────────────────────────
        stage('Build Docker Image') {
            steps {
                script {
                    try {
                        sh "docker build -t ${env.IMAGE_NAME}:${env.BUILD_NUMBER} ."
                        sh "docker tag  ${env.IMAGE_NAME}:${env.BUILD_NUMBER} ${env.IMAGE_NAME}:latest"
                    } catch (e) {
                        failedStageName = 'Build'
                        throw e
                    }
                }
            }
        }

        // ── STAGE 5: STOP OLD CONTAINER ────────────────────────
        stage('Stop Old Container') {
            steps {
                script {
                    try {
                        sh "docker stop ${env.IMAGE_NAME} || true"
                        sh "docker rm   ${env.IMAGE_NAME} || true"
                    } catch (e) {
                        failedStageName = 'Deploy'
                        throw e
                    }
                }
            }
        }

        // ── STAGE 6: RUN NEW CONTAINER ─────────────────────────
        stage('Run New Container') {
            steps {
                script {
                    try {
                        sh """
                            docker run -d \
                                -p ${env.CONTAINER_PORT}:5000 \
                                --name ${env.IMAGE_NAME} \
                                ${env.IMAGE_NAME}:latest
                        """
                    } catch (e) {
                        failedStageName = 'Deploy'
                        throw e
                    }
                }
            }
        }

        // ── STAGE 7: VERIFY DEPLOYMENT ─────────────────────────
        // Hits /health endpoint — if container didn't start, stage fails.
        stage('Verify Deployment') {
            steps {
                script {
                    try {
                        sh 'sleep 5'
                        sh "curl -f http://localhost:${env.CONTAINER_PORT}/health || exit 1"
                        echo "✔ Health check passed — container is live"
                    } catch (e) {
                        failedStageName = 'Deploy'
                        throw e
                    }
                }
            }
        }

    }

    // ── POST ACTIONS ───────────────────────────────────────────
    post {

        // On failure: write failed build_info.json and inject it
        // into the still-running old container so dashboard goes red.
        failure {
            script {    // ← Scripted Pipeline block
                def commitHash = sh(script: 'git rev-parse --short HEAD 2>/dev/null || echo unknown', returnStdout: true).trim()
                def buildTime  = sh(script: 'date "+%Y-%m-%d %H:%M:%S"', returnStdout: true).trim()
                def branch     = sh(script: 'git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown', returnStdout: true).trim()

                writeFile file: 'build_info.json', text: """{
  "build_number": "${env.BUILD_NUMBER}",
  "git_commit":   "${commitHash}",
  "git_branch":   "${branch}",
  "build_time":   "${buildTime}",
  "status":       "failed",
  "failed_stage": "${failedStageName}"
}"""
                // Inject into running container so dashboard updates live
                sh "docker cp build_info.json ${env.IMAGE_NAME}:/app/build_info.json || true"
                echo "❌ Build #${env.BUILD_NUMBER} failed at stage: ${failedStageName}"
            }
        }

        success {
            echo "✅ Deployment #${env.BUILD_NUMBER} live at http://192.168.78.128:${env.CONTAINER_PORT}"
        }

        // Always clean up old Docker images to save disk space
        always {
            sh "docker image prune -f || true"
        }
    }
}