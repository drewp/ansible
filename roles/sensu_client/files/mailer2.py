import sys, json, smtplib
ev = json.loads(sys.stdin.read())

from email.mime.text import MIMEText

if ev['occurrences'] == 1 and ev['action'] == 'create' and ev['check'].get('mail', True):
    msg = MIMEText('\n'.join("%s: %r" % (k,v) for k,v in sorted(ev['check'].items())) + "\n" +
                   "\n\naction: %s occurrences %s" % (ev['action'], ev['occurrences']),
                   )

    msg['Subject'] = '*sensu* %s failed on %s' % (ev['check']['name'], ev['client']['name'].split('.')[0])
    msg['From'] = 'sensu@bigasterisk.com'
    msg['To'] = 'drewp@bigasterisk.com'

    s = smtplib.SMTP('localhost')
    s.sendmail(msg['From'], [msg['To']], msg.as_string())
    s.quit()
