pipeline {
  agent any
  stages {
    stage('Build') {
      parallel {
        stage('Build') {
          steps {
            echo 'hello fro Build stage'
            sh 'mkdir jenkins'
          }
        }
        stage('') {
          steps {
            echo 'parallel'
          }
        }
      }
    }
    stage('test') {
      steps {
        echo 'hello from test'
      }
    }
    stage('Deploy') {
      steps {
        echo 'hello from deploy'
      }
    }
  }
}