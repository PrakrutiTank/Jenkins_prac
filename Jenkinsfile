pipeline {
    agent {
        node {
            label 'local'
            customWorkspace 'C:\\Users\\hp\\OneDrive\\Desktop\\SEM 7\\mlops\\Jenkins_prac'
        }
    }

    stages {

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