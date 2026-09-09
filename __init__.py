# Picard Sözler is a plugin that fetches lyrics from a public API.
# Copyright (C) 2024 Deniz Engin <dev@dilbil.im>
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from functools import partial

from picard.plugin3.api import PluginApi
from picard.track import Track


def log_debug(api: PluginApi, s):
    api.logger.debug(f"{'Picard Sözler'}: {s}")


def log_err(api: PluginApi, s):
    api.logger.error(f"{'Picard Sözler'}: {s}")


def process_response(api: PluginApi, track: Track, metadata, data, reply,
                     error):
    if error:
        return

    try:
        log_debug(api, "starting to process")
        log_debug(api, f"got response: {data}")
        instrumental = data.get("instrumental")
        if instrumental:
            log_debug(api, "instrumental track; skipping")
            lyrics = None
        else:
            # Fallbacks to plain, ie, unsynced lyrics.
            lyrics = data.get("syncedLyrics") or data.get("plainLyrics")

        if lyrics is not None:
            metadata["lyrics"] = lyrics
    except AttributeError:
        log_err(api, f"api malformed response: {data}")


def process_track(api: PluginApi, track: Track, metadata, _, __):
    (mins, secs) = map(int, metadata["~length"].split(":"))
    query = {
        "artist_name": metadata["albumartist"] or metadata["artist"],
        "album_name": metadata["album"],
        "track_name": metadata["title"],
        "duration": mins * 60 + secs,  # accepts seconds only
    }
    log_debug(api, f"trying to query with: {query}")
    track.tagger.webservice.get_url(
        url="https://lrclib.net/api/get",
        handler=partial(process_response, api, track, metadata),
        parse_response_type="json",
        queryargs=query,
    )


def enable(api: PluginApi):
    """Called when plugin is enabled."""
    api.register_track_metadata_processor(process_track)
