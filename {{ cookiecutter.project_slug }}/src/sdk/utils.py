import json
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any
from typing import List
from typing import Optional
from uuid import UUID

import aiosmtplib
from config import settings
from fastapi import Request
from fastapi.security import HTTPBearer


async def send_mail(
    sender: str,
    subject: str,
    content: str,
    to: Optional[List[str]] = None,
    mime_type: str = 'plain',
    **params,
) -> None:
    """
    Send an outgoing email with the given parameters.

    :param sender: From whom the email is being sent
    :type sender: str

    :param to: A list of recipient email addresses, defaults empty list.
    :type to: list

    :param subject: The subject of the email.
    :type subject: str

    :param content: The text of the email.
    :type content: str

    :param mime_type: Mime subtype of text, defaults to 'plain' (can be 'html').
    :type mime_type: str

    :param params: An optional set of parameters. (See below)
    :type params; dict

    Optional Parameters:
    :cc: A list of Cc email addresses.
    :bcc: A list of Bcc email addresses.
    """

    # Default Parameters
    cc = params.get('cc', [])
    bcc = params.get('bcc', [])

    # Prepare Message
    msg = MIMEMultipart()
    msg.preamble = subject
    msg['Subject'] = subject
    msg['From'] = sender

    if to:
        msg['To'] = ', '.join(to)
    if cc:
        msg['Cc'] = ', '.join(cc)
    if cc:
        msg['Bcc'] = ', '.join(bcc)

    msg.attach(MIMEText(content, mime_type, 'utf-8'))

    host = params.get('host', 'localhost')
    use_tls = params.get('tls', False)
    port = params.get('port')
    smtp = aiosmtplib.SMTP(hostname=host, port=port, use_tls=use_tls)
    await smtp.connect()
    if use_tls:
        await smtp.starttls()
    if 'user' in params and 'password' in params:
        await smtp.login(params['user'], params['password'])
    await smtp.send_message(msg)
    await smtp.quit()


class DefaultJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:  # noqa: ANN401, VNE001
        if isinstance(o, datetime):
            return o.strftime(settings.DEFAULT_DATETIME_FORMAT)
        elif isinstance(o, UUID):
            return str(o)
        return super().default(o)


class FakeHTTPBearer(HTTPBearer):
    """
    Фейковый класс для проставления в интерфейсе сваггера
    кнопки "Authorize"
    """

    async def __call__(self, request: Request) -> None:
        pass


fake_http_bearer = FakeHTTPBearer()
