import smtplib
import ssl


def send_mail(sender, recipients, subject, payload, in_production=True, **config):
    """
    Sends an email using the provided configuration over a secure connection, if in production.
    Otherwise, the email is sent over an insecure connection.

    :param sender: who the email is from
    :param recipients: the list of email addresses to send the message to or a single email address
    :param subject: the subject of the email
    :param payload: the actual message to be sent
    :param in_production: signifies whether the code is running in a production environment
    :param config: dictionary containing the mail server, port, and password for the sender's email account

    Example usage::

        # This is a configuration for sending emails using a Gmail account.
        config = {
            "mail_server_host": "smtp.gmail.com",
            "mail_server_port": 465,
            "mail_app_password": "<YOUR APP PASSWORD>"
        }
        send_mail(
            "YOUR EMAIL ADDRESS",
            # You can send the email to multiple recipients by providing a list of email addresses.
            # Or you can only send the email to a single recipient by providing a single email address
            # as a string.
            ["RECIPIENT 1's EMAIL ADDRESS", "RECIPIENT 2's EMAIL ADDRESS"],
            "YOUR SUBJECT LINE",
            "YOUR MESSAGE (BODY OF THE EMAIL)",
            **config)
    """
    header_to = recipients if not isinstance(recipients, list) else ', '.join(recipients)

    message = f'''\
From: {sender}
To: {header_to}
Subject: {subject}

{payload}
'''
    params = {'host': config['mail_server_host'], 'port': config['mail_server_port']}
    if in_production:
        params['context'] = ssl.create_default_context()
        client_class = smtplib.SMTP_SSL
    else:
        client_class = smtplib.SMTP

    with client_class(**params) as client:
        if in_production:
            # For more details, see https://support.google.com/accounts/answer/185833
            client.login(sender, config['mail_app_password'])
        client.sendmail(sender, recipients, message)
