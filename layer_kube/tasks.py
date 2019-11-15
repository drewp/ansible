from invoke import task

# sudo inv playbook --hosts=dash

@task
def playbook(ctx, hosts='all', _args=None):

    if _args is None:
        _args = "-l %s" % hosts

    # must alaways include master, so the token is set for other hosts
    ctx.run('''ANSIBLE_SCP_IF_SSH=y
export ANSIBLE_SCP_IF_SSH

HOME=/root
export HOME
eval `keychain --quiet --eval id_ecdsa`
cd /my/proj/ansible/layer_kube
ansible-playbook -v ./k3s/contrib/ansible/site.yml %s
    ''' % _args, pty=True)
