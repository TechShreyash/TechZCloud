import math
import logging
import mimetypes
from .TG.customdl import ByteStreamer
from .TG.tgfileproperty import get_name
from aiohttp import web

logger = logging.getLogger("streamer")


class_cache = {}
channel = -1001901516995
multi_clients = {}  # {0: client1, 1: client2, 2: client3}
work_loads = {}  # {0: 0, 1: 0, 2: 0}


async def media_streamer(request, message_id: int):
    global class_cache, multi_clients, work_loads

    range_header = request.headers.get("Range", 0)

    index = min(work_loads, key=work_loads.get)
    faster_client = multi_clients[index]

    logger.info(
        f"Client {index} is now serving the request for message {message_id}")

    if faster_client in class_cache:
        tg_connect = class_cache[faster_client]
        logger.debug(f"Using cached ByteStreamer object for client {index}")
    else:
        logger.debug(f"Creating new ByteStreamer object for client {index}")
        tg_connect = ByteStreamer(faster_client)
        class_cache[faster_client] = tg_connect
    logger.debug("before calling get_file_properties")
    file_id = await tg_connect.get_file_properties(message_id)
    logger.debug("after calling get_file_properties")

    file_size = file_id.file_size

    if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = (request.http_range.stop or file_size) - 1

    if (until_bytes > file_size) or (from_bytes < 0) or (until_bytes < from_bytes):
        return web.Response(
            status=416,
            body="416: Range not satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"},
        )

    chunk_size = 1024 * 1024
    until_bytes = min(until_bytes, file_size - 1)

    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1

    req_length = until_bytes - from_bytes + 1
    part_count = math.ceil(until_bytes / chunk_size) - \
        math.floor(offset / chunk_size)
    body = tg_connect.yield_file(
        file_id,
        index,
        offset,
        first_part_cut,
        last_part_cut,
        part_count,
        chunk_size,
        work_loads,
    )

    mime_type = file_id.mime_type
    file_name = get_name(file_id)
    disposition = "attachment"

    if not mime_type:
        mime_type = mimetypes.guess_type(
            file_name)[0] or "application/octet-stream"

    if "video/" in mime_type or "audio/" in mime_type or "/html" in mime_type:
        disposition = "inline"

    return web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": f"{mime_type}",
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(req_length),
            "Content-Disposition": f'{disposition}; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        },
    )
