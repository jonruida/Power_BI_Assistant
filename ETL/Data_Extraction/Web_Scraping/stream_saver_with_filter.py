import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from mitmproxy import ctx


class StreamSaver:
    TAG = "save_streamed_data: "

    def __init__(self, flow, direction):
        self.flow = flow
        self.direction = direction
        self.fh = None
        self.path = None

    def done(self):
        if self.fh:
            self.fh.close()
            self.fh = None
        # Make sure we have no circular references
        self.flow = None

    def __call__(self, data):
        # End of stream?
        if len(data) == 0:
            self.done()
            return data

        # Just in case the option changes while a stream is in flight
        if not ctx.options.save_streamed_data:
            return data

        # This is a safeguard but should not be needed
        if not self.flow or not self.flow.request:
            return data

        if not self.fh:
            self.path = datetime.fromtimestamp(
                self.flow.request.timestamp_start
            ).strftime(ctx.options.save_streamed_data)
            self.path = self.path.replace("%+T", str(self.flow.request.timestamp_start))
            self.path = self.path.replace("%+I", str(self.flow.client_conn.id))
            self.path = self.path.replace("%+D", self.direction)
            self.path = self.path.replace("%+C", self.flow.client_conn.address[0])
            self.path = os.path.expanduser(self.path)

            parent = Path(self.path).parent
            try:
                if not parent.exists():
                    parent.mkdir(parents=True, exist_ok=True)
            except OSError:
                logging.error(f"{self.TAG}Failed to create directory: {parent}")

            try:
                self.fh = open(self.path, "wb", buffering=0)
            except OSError:
                logging.error(f"{self.TAG}Failed to open for writing: {self.path}")

        if self.fh:
            try:
                self.fh.write(data)
            except OSError:
                logging.error(f"{self.TAG}Failed to write to: {self.path}")

        return data


def load(loader):
    loader.add_option(
        "save_streamed_data",
        Optional[str],
        None,
        "Format string for saving streamed data to files.",
    )
    loader.add_option(
        "save_streamed_data_filter",
        Optional[str],
        None,
        "Filter for saving streamed data based on headers. Format should be 'header_name=header_value'."
    )


def requestheaders(flow):
    if ctx.options.save_streamed_data and flow.request.stream:
        filter_header = ctx.options.save_streamed_data_filter
        if filter_header:
            header_name, header_value = filter_header.split('=', 1)
            if flow.request.headers.get(header_name) == header_value:
                flow.request.stream = StreamSaver(flow, "req")


def responseheaders(flow):
    if isinstance(flow.request.stream, StreamSaver):
        flow.request.stream.done()
    if ctx.options.save_streamed_data and flow.response.stream:
        filter_header = ctx.options.save_streamed_data_filter
        if filter_header:
            header_name, header_value = filter_header.split('=', 1)
            if flow.response.headers.get(header_name) == header_value:
                flow.response.stream = StreamSaver(flow, "rsp")


def response(flow):
    if isinstance(flow.response.stream, StreamSaver):
        flow.response.stream.done()


def error(flow):
    if flow.request and isinstance(flow.request.stream, StreamSaver):
        flow.request.stream.done()
    if flow.response and isinstance(flow.response.stream, StreamSaver):
        flow.response.stream.done()
