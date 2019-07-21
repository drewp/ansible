from invoke import task

# sudo inv playbook --hosts=dash

@task
def playbook(ctx, hosts='all', _args=None):

    if _args is None:
        _args = "-l %s" % hosts

    ctx.run('''ANSIBLE_SCP_IF_SSH=y
export ANSIBLE_SCP_IF_SSH

HOME=/root
export HOME
eval `keychain --quiet --eval id_ecdsa`
cd /my/proj/ansible/layer_net
ansible-playbook net.yml %s
    ''' % _args, pty=True)

@task
def dnsmasq_reread_config(ctx):
    playbook(ctx, _args='-l bang -t dnsmasq')
