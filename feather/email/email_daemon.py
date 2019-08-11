"""File that contains the EmailDaemon class."""
from threading import Thread
from queue import Queue
import smtplib
import ssl
import logging

from constants import Constants
from feather.email.data_packet import EndOfStreamPacket
from feather.email.create_email import create_email

LOGGER = logging.getLogger(__name__)


class EmailDaemon(Thread):
    """Daemon that coordinates email campaigns."""
    def __init__(self, queue: Queue) -> None:
        super().__init__(daemon=True)
        self._queue = queue

    def run(self) -> None:
        """Run method for the EmailDaemon. This method listens on self._queue and sends
        an email when ordered to. The daemon will run until it receives an EndOfStreamPacket.
        """
        LOGGER.info("The EmailDaemon thread is starting.")

        # start the server and log in to your email account
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(Constants.EMAIL_HOST, 465, context=context) as server:
            server.login(Constants.EMAIL, Constants.EMAIL_PASSWORD)

            while True:
                # block when the queue is empty
                data = self._queue.get()
                if isinstance(data, EndOfStreamPacket):
                    break

                # create and send email
                mail = create_email(data.template_name, data.email_subject, data.email, data.first_name)
                server.sendmail(
                    Constants.EMAIL, data.email, mail.as_string()
                )

                LOGGER.info(f"Email sent. (name={data.first_name}, email={data.email}, template={data.template_name})")

        LOGGER.info("The EmailDaemon thread is finished.")
