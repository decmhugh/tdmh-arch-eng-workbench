build_agent {
  container('sdk') {
    scm_checkout()
    resolve_dependencies()

    stage('Validate Specs') {
      sh '''#!/bin/bash
        set -e
        export HOME=/tmp
        export PATH=/home/python/.local/bin:$PATH

        python3 scripts/validate_specs.py
          # Embedded mermaid blocks are generated from their .mmd source; a stale
          # copy means someone edited the published diagram instead of the source.
          python3 scripts/sync_mermaid_embeds.py --check
        # The assurance register is generated, and the same check sweeps specs/ and
        # docs/ for any ATG/ISRA id that was added without being declared.
        python3 scripts/generate_assurance_register.py --check
        # specs/README.md and specs/epic-mapping.json are generated: regenerating
        # must be a no-op, otherwise someone edited a spec without rebuilding them.
        python3 scripts/generate_spec_index.py
        if ! git diff --exit-code --quiet specs/README.md specs/epic-mapping.json; then
          echo "ERROR: derived spec files are stale."
          echo "Run 'python3 scripts/generate_spec_index.py' and commit the result."
          git --no-pager diff specs/README.md specs/epic-mapping.json
          exit 1
        fi
      '''
    }

    stage('Assemble Content') {
      sh '''#!/bin/bash
        set -e
        chmod +x scripts/assemble-docs.sh
        CI=true bash scripts/assemble-docs.sh
      '''
    }

    stage('Build Docs') {
      sh '''#!/bin/bash
        set -e
        export HOME=/tmp
        export PATH=/home/python/.local/bin:$PATH
        mkdocs build 2>&1
      '''
    }

    if (env.BRANCH_NAME == 'main') {
      stage('Publish to bb-pages') {
        withCredentials([usernamePassword(credentialsId: 'gitget-userid-password', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_PASS')]) {  // pragma: allowlist secret
          sh '''#!/bin/bash
            set -e
            export HOME=/tmp
            export PATH=/home/python/.local/bin:$PATH

            AUTH_URL="https://${GIT_USER}:${GIT_PASS}@bitbucket.sunlifecorp.com/scm/t1kacp/acp-specs.git"
            git remote set-url origin "${AUTH_URL}"
            git config user.name "Jenkins CI"
            git config user.email "jenkins@sunlife.com"

            mkdocs gh-deploy --remote-branch bb-pages --force 2>&1
          '''
        }
      }
    } else {
      echo "Skipping publish — only main branch publishes to bb-pages"
    }

    stage('Notify BitBucket') {
      currentBuild.result = currentBuild.result ?: 'SUCCESS'
      notifyBitbucket(
        credentialsId: 'gitget-userid-password',
        stashServerBaseUrl: 'https://bitbucket.sunlifecorp.com'
      )
      cleanWs()
    }
  }
}
