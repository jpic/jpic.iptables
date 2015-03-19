#!/usr/bin/env python2
from ansible.module_utils.basic import *


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(),
            table=dict(),
            chain=dict(),
            rule=dict(),
            state=dict(default='present'),
            args=dict(),
        )
    )

    if module.params.get('args', None) is not None:
        params = module.params['args']
    else:
        params = module.params

    name = params['name']
    table = params.get('table', None)
    chain = params['chain']
    state = params.get('state', 'present')

    if isinstance(params['rule'], list):
        rule = []
        for fragment in params['rule']:
            option = fragment.split(' ')[0]

            rule.append('%s%s' % (
                '-' if len(option) == 1 else '--', fragment))

        rule = ' '.join(rule)
    else:
        rule = params['rule']

    comment = '-m comment --comment "%s"' % name.replace(
            "'", "").replace('"', '')

    ret, out, err = module.run_command('iptables-save')

    if ret != 0:
        module.exit_json(failed=True, msg='Running iptables-save failed')

    if ((comment in out and state == 'present') 
            or (comment not in out and state == 'absent')):

        module.exit_json(changed=False)

    cmd = ['iptables']

    if table:
        cmd.append('-t %s' % table)

    if state == 'present':
        cmd.append('-A %s' % chain)
    elif state == 'absent':
        cmd.append('-D %s' % chain)

    cmd.append(rule)

    cmd.append(comment)

    print ' '.join(cmd)

    ret, out, err = module.run_command(' '.join(cmd))
    
    if ret != 0:
        module.exit_json(failed=True, msg=' '.join(cmd) + out + err)

    module.exit_json(changed=True)

main()
