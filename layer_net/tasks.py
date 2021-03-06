from invoke import task

# this is hard to use on bang without 'invoke' present:
#   sudo pip3 install -U invoke

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

@task
def docker(ctx):
    playbook(ctx, _args='-l bang -t docker')

@task
def wireguard_install(ctx):
    playbook(ctx, _args='-l all -t wg-install')

@task
def wireguard(ctx):
    playbook(ctx, _args='-l all -t wg-config,wg-generate-keys')

@task
def prime_firewall(ctx):
    playbook(ctx, _args='-l prime -t prime_firewall')

@task
def run_hosts(ctx):
    playbook(ctx, _args='-t hosts')

@task
def ppa(ctx):
    playbook(ctx, _args='-l all -t ppa')

@task
def users(ctx):
    playbook(ctx, _args='-l all -t bigasterisk_users')
