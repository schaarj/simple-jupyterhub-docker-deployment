# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Configuration file for JupyterHub
import os
import json
c = get_config()

# We rely on environment variables to configure JupyterHub so that we
# avoid having to rebuild the JupyterHub container every time we change a
# configuration parameter.

# Spawn single-user servers as Docker containers
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
# Spawn containers from this image
#c.DockerSpawner.container_image = os.environ['DOCKER_NOTEBOOK_IMAGE']
#c.DockerSpawner.image_whitelist = {'pyiron-base':'muhhassani/pyiron-base-image','pyiron-atomistic':'muhhassani/pyiron-image'}
with open('images.json') as fh:
    images = json.load(fh)
c.DockerSpawner.image_whitelist = images
#c.DockerSpawner.image_whitelist = {'pyiron-base':'muhhassani/pyiron-base-image','pyiron-md':'muhhassani/pyiron-lammps-image'}
# JupyterHub requires a single-user instance of the Notebook server, so we
# default to using the `start-singleuser.sh` script included in the
# jupyter/docker-stacks *-notebook images as the Docker run command when
# spawning containers.  Optionally, you can override the Docker run command
# using the DOCKER_SPAWN_CMD environment variable.
#spawn_cmd = os.environ.get('DOCKER_SPAWN_CMD', "start-singleuser.sh")
spawn_cmd = "start-singleuser.sh --SingleUserNotebookApp.default_url=/lab"
#spawn_cmd = '/bin/bash -c "if [ ! -d /home/pyiron/PMD-workflow-workshop ] ; then git clone https://github.com/materialdigital/PMD-workflow-workshop ; cp /home/pyiron/PMD-workflow-workshop/Exercises/1_intro.ipynb /home/pyiron/PMD-workflow-workshop/1_1_intro_pyiron_building_blocks/1_1_intro.ipynb;  cp /home/pyiron/PMD-workflow-workshop/Exercises/1_2_import_project.ipynb /home/pyiron/PMD-workflow-workshop/1_2_import_proj/; cp /home/pyiron/PMD-workflow-workshop/Exercises/{2_0_custom_python_job.ipynb,2_1_custom_bash_job.ipynb} /home/pyiron/PMD-workflow-workshop/2_customized_job/; cp /home/pyiron/PMD-workflow-workshop/Exercises/3_lammps-damask-workflow.ipynb /home/pyiron/PMD-workflow-workshop/3_lammps_damask_workflow/ ; rm -r /home/pyiron/PMD-workflow-workshop/Exercises/; fi && start-singleuser.sh  --SingleUserNotebookApp.default_url=/lab"'
c.DockerSpawner.extra_create_kwargs.update({ 'command': spawn_cmd })
# Connect containers to this Docker network
network_name = os.environ['DOCKER_NETWORK_NAME']
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.network_name = network_name
# Pass the network name as argument to spawned containers
c.DockerSpawner.extra_host_config = { 'network_mode': network_name }
notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/'
c.DockerSpawner.notebook_dir = notebook_dir
#c.DockerSpawner.volumes = { 'iron_docker_workspace/': notebook_dir }
c.DockerSpawner.volumes = { 'jupyterhub-user-{username}': notebook_dir }
# volume_driver is no longer a keyword argument to create_container()
# c.DockerSpawner.extra_create_kwargs.update({ 'volume_driver': 'local' })
# Remove containers once they are stopped
c.DockerSpawner.remove_containers = True
# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True

# User containers will access hub by container name on the Docker network
c.JupyterHub.hub_ip = 'jupyterhub'
c.JupyterHub.hub_port = 8080

# TLS config
c.JupyterHub.port = 443
c.JupyterHub.ssl_key = os.environ['SSL_KEY']
c.JupyterHub.ssl_cert = os.environ['SSL_CERT']

# Authenticate users with GitHub OAuth
#c.JupyterHub.authenticator_class = 'jupyterhub.auth.PAMAuthenticator'
#c.GitHubOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']
os.environ['OAUTH2_TOKEN_URL'] = "https://sso.material-digital.de/auth/realms/material-digital/protocol/openid-connect/token"
os.environ['OAUTH2_AUTHORIZE_URL'] = "https://sso.material-digital.de/auth/realms/material-digital/protocol/openid-connect/auth"
os.environ['OAUTH2_USERDATA_URL'] = 'https://sso.material-digital.de/auth/realms/material-digital/protocol/openid-connect/userinfo'
os.environ['OAUTH2_TLS_VERIFY'] = '0'
os.environ['OAUTH_TLS_VERIFY'] = '0'
os.environ['OAUTH2_USERNAME_KEY'] = 'preferred_username'

from oauthenticator.generic import GenericOAuthenticator
c.OAuthenticator.login_service = "MaterialDigital SSO"
c.JupyterHub.authenticator_class = GenericOAuthenticator
c.OAuthenticator.oauth_callback_url = 'https://pyiron.material-digital.de/hub/oauth_callback'
c.OAuthenticator.client_id = os.environ['KEYCLOAK_CLIENT_ID']
c.OAuthenticator.client_secret = os.environ['KEYCLOAK_CLIENT_SECRET']
c.GenericOAuthenticator.token_url ='https://sso.material-digital.de/auth/realms/material-digital/protocol/openid-connect/token'
c.GenericOAuthenticator.userdata_url ='https://sso.material-digital.de/auth/realms/material-digital/protocol/openid-connect/userinfo'
c.GenericOAuthenticator.userdata_method = 'GET'
c.GenericOAuthenticator.userdata_params = {"state": "state"}
c.OAuthenticator.tls_verify = False
c.LocalAuthenticator.create_system_users = True
c.GenericOAuthenticator.username_key = 'preferred_username'
#c.Authenticator.auto_login = True

# Persist hub data on volume mounted inside container
data_dir = os.environ.get('DATA_VOLUME_CONTAINER', '/data')

c.JupyterHub.cookie_secret_file = os.path.join(data_dir,
    'jupyterhub_cookie_secret')

c.JupyterHub.db_url = 'postgresql://postgres:{password}@{host}/{db}'.format(
    host=os.environ['POSTGRES_HOST'],
    password=os.environ['POSTGRES_PASSWORD'],
    db=os.environ['POSTGRES_DB'],
)

#c.DockerSpawner.mem_limit='10G'
#c.DockerSpawner.cpu_limit=2
#c.Spawner.mem_limit = '10G'
#c.Spawner.cpu_limit = 2
# Other stuff
c.Spawner.cpu_limit = 2
c.Spawner.mem_limit = '10G'

# Whitlelist users and admins
c.Authenticator.whitelist = whitelist = set()
#c.Authenticator.admin_users = admin = set()
c.Authenticator.admin_users = os.environ["JUPYTERHUB_ADMIN_USERS"].split(",")
c.JupyterHub.admin_access = True
pwd = os.path.dirname(__file__)
#with open(os.path.join(pwd, 'userlist')) as f:
#    for line in f:
#        if not line:
#            continue
#        parts = line.split()
        # in case of newline at the end of userlist file
#        if len(parts) >= 1:
#            name = parts[0]
#            whitelist.add(name)
#            if len(parts) > 1 and parts[1] == 'admin':
#                admin.add(name)
