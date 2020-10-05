from typing import Any, Optional

from django.conf import settings
from django.core.files.uploadhandler import FileUploadHandler, StopFutureHandlers
from django.core.handlers.wsgi import WSGIRequest
from google.auth.transport import requests as tr_requests
from google.oauth2.service_account import Credentials
from google.resumable_media.requests import ResumableUpload

from ..streams import AutoTruncatingChunkedStreamable


class GCPStreamingFileUploadHandler(FileUploadHandler):
    upload_url = "https://www.googleapis.com/upload/storage/v1/b/" \
                 "{bucket}/o?uploadType=resumable"
    chunk_size = 256 * 1024  # needs to be at least 256KB for google

    def __init__(self,
                 request: WSGIRequest = None,
                 bucket: str = None) -> None:
        super(GCPStreamingFileUploadHandler, self).__init__(request)
        self.upload_url: str = self.upload_url.format(bucket=bucket)
        self.transport = tr_requests.AuthorizedSession(
            credentials=Credentials.from_service_account_file(
                settings.GCP_STORAGE_KEY,
                scopes=["https://www.googleapis.com/auth/devstorage.read_write"]
            )
        )
        self.data = AutoTruncatingChunkedStreamable(self.chunk_size)
        self.file = None  # type: Optional[ResumableUpload]

    def new_file(self, *args, **kwargs) -> None:
        super(GCPStreamingFileUploadHandler, self).new_file(*args, **kwargs)
        self.file = ResumableUpload(
            self.upload_url,
            self.chunk_size,
        )
        self.file.initiate(
            self.transport,
            self.data,
            {"name": self.file_name},
            self.content_type,
            stream_final=False,
        )
        raise StopFutureHandlers("Continue resumable upload session")

    def receive_data_chunk(self, raw_data: bytes, start: int) -> None:
        # Since we have provided a dynamic size for our upload session,
        # Google will assume our request is finished when:
        # chunk_size > raw_data
        self.data.write(raw_data)
        if self.data.read(anon=True):
            self.file.transmit_next_chunk(self.transport)

        # needed to stop django multipart skipping the upload
        return None

    def file_complete(self, file_size: int) -> Any:
        if self.file.finished:
            return object  # TODO: implement streamed blob response
