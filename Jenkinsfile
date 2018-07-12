pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        echo 'hello fro Build stage'
        sh 'mkdir jenkins'
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