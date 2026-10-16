pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source repository...'
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing Python test and application dependencies...'
                script {
                    if (isUnix()) {
                        sh 'pip install --no-cache-dir flask requests scikit-learn numpy pytest'
                    } else {
                        bat 'pip install --no-cache-dir flask requests scikit-learn numpy pytest'
                    }
                }
            }
        }

        stage('Run Unit Tests') {
            steps {
                echo 'Executing Pytest test suite...'
                script {
                    if (isUnix()) {
                        sh 'pytest webapp/test_sample.py -v --junitxml=test-reports/results.xml'
                    } else {
                        bat 'pytest webapp/test_sample.py -v --junitxml=test-reports/results.xml'
                    }
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                echo 'Building Docker images via Docker Compose...'
                script {
                    if (isUnix()) {
                        sh 'docker compose build'
                    } else {
                        bat 'docker compose build'
                    }
                }
            }
        }

        stage('Deploy Containers') {
            steps {
                echo 'Deploying application stack using Docker Compose...'
                script {
                    if (isUnix()) {
                        sh 'docker compose up -d'
                    } else {
                        bat 'docker compose up -d'
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'Archiving test results...'
            junit testResults: 'test-reports/*.xml', allowEmptyResults: true
        }
        success {
            echo '========================================='
            echo ' Pipeline execution succeeded! '
            echo ' Web app running on http://localhost:5000 '
            echo ' DB service running on http://localhost:5002 '
            echo '========================================='
        }
        failure {
            echo 'Pipeline failed. Check previous stage console output.'
        }
    }
}
