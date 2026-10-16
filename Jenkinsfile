pipeline {
    agent {
        node {
            label 'local'
        }
    }

    stages {

        
        stage('Checkout Code') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/PrakrutiTank/Jenkins_prac.git'
            }
        }

        stage('Show Workspace') {
            steps {
                bat 'cd'
            }
        }

        stage('Build Images') {
            steps {
                bat 'docker compose build'
            }
        }

        stage('Run Tests') {
            steps {
                bat 'docker compose run --rm webapp pytest'
            }
        }

        stage('Deploy Containers') {
            steps {
                bat 'docker compose up -d'
            }
        }
    }
}