# Picard Sözler is a plugin that fetches lyrics from a public API.
# Copyright (C) 2024 Deniz Engin <dev@dilbil.im>
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.


from picard.plugin3.api import PluginApi

from functools import partial
import json


def log_debug(s):
    api.logger.debug(f"{'Picard Sözler'}: {s}")


def log_err(s):
    api.logger.error(f"{'Picard Sözler'}: {s}")


def process_response(album, metadata, data, reply, error):
    if error:
        album._requests -= 1
        album._finalize_loading(None)
        return

    try:
        log_debug("starting to process")
        log_debug(f"got response: {data}")
        instrumental = data.get("instrumental")
        if instrumental:
            log_debug("instrumental track; skipping")
            lyrics = None
        else:
            # Fallbacks to plain, ie, unsynced lyrics.
            lyrics = data.get("syncedLyrics") or data.get("plainLyrics")

        if lyrics is not None:
            metadata["lyrics"] = lyrics
    except AttributeError:
        log_err(f"api malformed response: {data}")
    finally:
        album._requests -= 1
        album._finalize_loading(None)


def process_track(album, metadata, track, __):
    (mins, secs) = map(int, metadata["~length"].split(":"))
    query = {
        "artist_name": metadata["albumartist"] or metadata["artist"],
        "album_name": metadata["album"],
        "track_name": metadata["title"],
        "duration": mins * 60 + secs,  # accepts seconds only
    }
    log_debug(f"trying to query with: {query}")
    album.tagger.webservice.get_url(
        url="https://lrclib.net/api/get",
        handler=partial(process_response, album, metadata),
        parse_response_type="json",
        queryargs=query,
    )
    album._requests += 1


def enable(api: PluginApi):
    """Called when plugin is enabled."""
    api.register_track_metadata_processor(process_track)
