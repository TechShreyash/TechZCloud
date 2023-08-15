from utils.download import DL_STATUS, download_file
from utils.upload import upload_file_to_channel


async def start_remote_upload(session, hash, url):
    ext = await download_file(session, hash, url)
    if ext:
        await upload_file_to_channel(hash, hash + ext, ext)
