from hamcrest import assert_that, has_item
from mbtest.imposters.imposters import Address, smtp_imposter
from mbtest.matchers import email_sent
from suts import mail_client


def test_sending_mail(mock_server, config):
    # Set up the imposter to mock the mail server, see https://www.mbtest.org/docs/protocols/smtp
    imposter = smtp_imposter("Virtual Mail Server")

    with mock_server(imposter):
        # Send an email using the mail client.
        mail_client.send_mail(
            "Test Sender <sender@example.com>",
            "Test Recipient <recipient@example.com>",
            "Test Email",
            "This is a test email.",
            in_production=False,
            **config)

        # Verify that the mail client has properly sent the email to the mail server.
        assert_that(imposter,
                    email_sent(
                        to=has_item(Address(address="recipient@example.com", name="Test Recipient")),
                        subject="Test Email",
                        body_text="This is a test email."))
