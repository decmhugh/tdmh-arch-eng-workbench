libraries {
  pod_template {
    build_agent {
      userId = '0'
      cloud = 'prod-eks--prod-devops-jenkinsagents-ns'
      sdk {
        // dace/python ubuntu images were deleted from quay; dpep/python-containers is the sanctioned replacement.
        image = 'quay.prod-openshift-na.hybrid.sunlifecorp.com/dpep/python-containers:3.12-ubuntu22.04-20260511T101424Z'
        resource {
          cpu {
            request_mcore = '200'
            limit_mcore = '400'
          }
          memory {
            request_mbyte = '512'
            limit_mbyte = '512'
          }
        }
      }
    }
  }

  git
  pip {
    requirements = []
    pip_config_file_id = 'pip.config'
    requirements_files = ['requirements-docs.txt']
  }
}
