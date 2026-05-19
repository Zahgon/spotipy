""" A simple and thin Python library for the Spotify Web API """

__all__ = ["Spotify", "SpotifyException"]

import json
import logging
import re
import warnings
from collections import defaultdict

import requests

from spotipy.exceptions import SpotifyException
from spotipy.util import REQUESTS_SESSION, Retry

logger = logging.getLogger(__name__)


class Spotify:
    """
        Example usage::

            import spotipy

            urn = 'spotify:artist:3jOstUTkEu2JkjvRdBA5Gu'
            sp = spotipy.Spotify()

            artist = sp.artist(urn)
            print(artist)

            user = sp.user('plamere')
            print(user)
    """
    max_retries = 3
    default_retry_codes = (429, 500, 502, 503, 504)
    country_codes = [
        "AD",
        "AR",
        "AU",
        "AT",
        "BE",
        "BO",
        "BR",
        "BG",
        "CA",
        "CL",
        "CO",
        "CR",
        "CY",
        "CZ",
        "DK",
        "DO",
        "EC",
        "SV",
        "EE",
        "FI",
        "FR",
        "DE",
        "GR",
        "GT",
        "HN",
        "HK",
        "HU",
        "IS",
        "ID",
        "IE",
        "IT",
        "JP",
        "LV",
        "LI",
        "LT",
        "LU",
        "MY",
        "MT",
        "MX",
        "MC",
        "NL",
        "NZ",
        "NI",
        "NO",
        "PA",
        "PY",
        "PE",
        "PH",
        "PL",
        "PT",
        "SG",
        "ES",
        "SK",
        "SE",
        "CH",
        "TW",
        "TR",
        "GB",
        "US",
        "UY"]

    # Spotify URI scheme defined in [1], and the ID format as base-62 in [2].
    #
    # Unfortunately the IANA specification is out of date and doesn't include the new types
    # show and episode. Additionally, for the user URI, it does not specify which characters
    # are valid for usernames, so the assumption is alphanumeric which coincidentally are also
    # the same ones base-62 uses.
    # In limited manual exploration this seems to hold true, as newly accounts are assigned an
    # identifier that looks like the base-62 of all other IDs, but some older accounts only have
    # numbers and even older ones seemed to have been allowed to freely pick this name.
    #
    # [1] https://www.iana.org/assignments/uri-schemes/prov/spotify
    # [2] https://developer.spotify.com/documentation/web-api/concepts/spotify-uris-ids
    _regex_spotify_uri = r'^spotify:(?:(?P<type>track|artist|album|playlist|show|episode|audiobook):(?P<id>[0-9A-Za-z]+)|user:(?P<username>[0-9A-Za-z]+):playlist:(?P<playlistid>[0-9A-Za-z]+))$'  # noqa: E501

    # Spotify URLs are defined at [1]. The assumption is made that they are all
    # pointing to open.spotify.com, so a regex is used to parse them as well,
    # instead of a more complex URL parsing function.
    # Spotify recently added "/intl-<countrycode>" to their links. This change is undocumented.
    # There is an assumption that the country code uses the ISO 3166-1 alpha-2 standard [2],
    # but this has not been confirmed yet. Spotipy has no use for this, so it gets ignored.
    #
    # [1] https://developer.spotify.com/documentation/web-api/concepts/spotify-uris-ids
    # [2] https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
    _regex_spotify_url = r'^(http[s]?:\/\/)?open.spotify.com\/(intl-\w\w\/)?(?P<type>track|artist|album|playlist|show|episode|user|audiobook)\/(?P<id>[0-9A-Za-z]+)(\?.*)?$'  # noqa: E501

    _regex_base62 = r'^[0-9A-Za-z]+$'

    def __init__(
        self,
        auth=None,
        requests_session=True,
        client_credentials_manager=None,
        oauth_manager=None,
        auth_manager=None,
        proxies=None,
        requests_timeout=5,
        status_forcelist=None,
        retries=max_retries,
        status_retries=max_retries,
        backoff_factor=0.3,
        language=None,
    ):
        """
        Creates a Spotify API client.

        :param auth: An access token (optional)
        :param requests_session:
            A Requests session object or a truthy value to create one.
            A falsy value disables sessions.
            It should generally be a good idea to keep sessions enabled
            for performance reasons (connection pooling).
        :param client_credentials_manager:
            SpotifyClientCredentials object
        :param oauth_manager:
            SpotifyOAuth object
        :param auth_manager:
            SpotifyOauth, SpotifyClientCredentials,
            or SpotifyImplicitGrant object
        :param proxies:
            Definition of proxies (optional).
            See Requests doc https://2.python-requests.org/en/master/user/advanced/#proxies
        :param requests_timeout:
            Tell Requests to stop waiting for a response after a given
            number of seconds
        :param status_forcelist:
            Tell requests what type of status codes retries should occur on
        :param retries:
            Total number of retries to allow
        :param status_retries:
            Number of times to retry on bad status codes
        :param backoff_factor:
            A backoff factor to apply between attempts after the second try
            See urllib3 https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html
        :param language:
            The language parameter advertises what language the user prefers to see.
            See ISO-639-1 language code: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
        """
        self.prefix = "https://api.spotify.com/v1/"
        self._auth = auth
        self.client_credentials_manager = client_credentials_manager
        self.oauth_manager = oauth_manager
        self.auth_manager = auth_manager
        self.proxies = proxies
        self.requests_timeout = requests_timeout
        self.status_forcelist = status_forcelist or self.default_retry_codes
        self.backoff_factor = backoff_factor
        self.retries = retries
        self.status_retries = status_retries
        self.language = language

        if isinstance(requests_session, requests.Session):
            self._session = requests_session
        else:
            if requests_session:  # Build a new session.
                self._build_session()
            else:  # Use the Requests API module as a "session".
                self._session = requests.api




    def __del__(self):
        """Make sure the connection (pool) gets closed"""
        if getattr(self, "_session", None) and isinstance(self._session, REQUESTS_SESSION):
            self._session.close()








    def next(self, result):
        """ returns the next result given a paged result

            Parameters:
                - result - a previously returned paged result
        """
        pass

    def previous(self, result):
        """ returns the previous result given a paged result

            Parameters:
                - result - a previously returned paged result
        """
        pass

    def track(self, track_id, market=None):
        """ returns a single track given the track's ID, URI or URL

            Parameters:
                - track_id - a spotify URI, URL or ID
                - market - an ISO 3166-1 alpha-2 country code.
        """
        pass

    def tracks(self, tracks, market=None):
        """ returns a list of tracks given a list of track IDs, URIs, or URLs

            Parameters:
                - tracks - a list of spotify URIs, URLs or IDs. Maximum: 50 IDs.
                - market - an ISO 3166-1 alpha-2 country code.
        """
        pass

    def artist(self, artist_id):
        """ returns a single artist given the artist's ID, URI or URL

            Parameters:
                - artist_id - an artist ID, URI or URL
        """
        pass

    def artists(self, artists):
        """ returns a list of artists given the artist IDs, URIs, or URLs

            Parameters:
                - artists - a list of  artist IDs, URIs or URLs
        """
        pass

    def artist_albums(
        self, artist_id, album_type=None, include_groups=None, country=None, limit=10, offset=0
    ):
        """ Get Spotify catalog information about an artist's albums

            .. deprecated::
            This method is deprecated and may be removed in a future version. Use
            `artist_albums(..., include_groups='...')` instead.

            Parameters:
                - artist_id - the artist ID, URI or URL
                - include_groups - the types of items to return. One or more of 'album', 'single',
                                   'appears_on', 'compilation'. If multiple types are desired,
                                   pass in a comma separated string; e.g., 'album,single'.
                - country - limit the response to one particular country.
                - limit  - the number of albums to return
                - offset - the index of the first album to return
        """
        pass

    def artist_top_tracks(self, artist_id, country="US"):
        """ Get Spotify catalog information about an artist's top 10 tracks
            by country.

            Parameters:
                - artist_id - the artist ID, URI or URL
                - country - limit the response to one particular country.
        """
        pass

    def artist_related_artists(self, artist_id):
        """ Get Spotify catalog information about artists similar to an
            identified artist. Similarity is based on analysis of the
            Spotify community's listening history.

            .. deprecated::
            This endpoint has been removed by Spotify and is no longer available.

            Parameters:
                - artist_id - the artist ID, URI or URL
        """
        pass

    def album(self, album_id, market=None):
        """ returns a single album given the album's ID, URIs or URL

            Parameters:
                - album_id - the album ID, URI or URL
                - market - an ISO 3166-1 alpha-2 country code
        """
        pass

    def album_tracks(self, album_id, limit=50, offset=0, market=None):
        """ Get Spotify catalog information about an album's tracks

            Parameters:
                - album_id - the album ID, URI or URL
                - limit  - the number of items to return
                - offset - the index of the first item to return
                - market - an ISO 3166-1 alpha-2 country code.

        """
        pass

    def albums(self, albums, market=None):
        """ returns a list of albums given the album IDs, URIs, or URLs

            Parameters:
                - albums - a list of  album IDs, URIs or URLs
                - market - an ISO 3166-1 alpha-2 country code
        """
        pass

    def show(self, show_id, market=None):
        """ returns a single show given the show's ID, URIs or URL

            Parameters:
                - show_id - the show ID, URI or URL
                - market - an ISO 3166-1 alpha-2 country code.
                           The show must be available in the given market.
                           If user-based authorization is in use, the user's country
                           takes precedence. If neither market nor user country are
                           provided, the content is considered unavailable for the client.
        """
        pass

    def shows(self, shows, market=None):
        """ returns a list of shows given the show IDs, URIs, or URLs

            Parameters:
                - shows - a list of show IDs, URIs or URLs
                - market - an ISO 3166-1 alpha-2 country code.
                           Only shows available in the given market will be returned.
                           If user-based authorization is in use, the user's country
                           takes precedence. If neither market nor user country are
                           provided, the content is considered unavailable for the client.
        """
        pass

    def show_episodes(self, show_id, limit=50, offset=0, market=None):
        """ Get Spotify catalog information about a show's episodes

            Parameters:
                - show_id - the show ID, URI or URL
                - limit  - the number of items to return
                - offset - the index of the first item to return
                - market - an ISO 3166-1 alpha-2 country code.
                           Only episodes available in the given market will be returned.
                           If user-based authorization is in use, the user's country
                           takes precedence. If neither market nor user country are
                           provided, the content is considered unavailable for the client.
        """
        pass

    def episode(self, episode_id, market=None):
        """ returns a single episode given the episode's ID, URIs or URL

            Parameters:
                - episode_id - the episode ID, URI or URL
                - market - an ISO 3166-1 alpha-2 country code.
                           The episode must be available in the given market.
                           If user-based authorization is in use, the user's country
                           takes precedence. If neither market nor user country are
                           provided, the content is considered unavailable for the client.
        """
        pass

    def episodes(self, episodes, market=None):
        """ returns a list of episodes given the episode IDs, URIs, or URLs

            Parameters:
                - episodes - a list of episode IDs, URIs or URLs
                - market - an ISO 3166-1 alpha-2 country code.
                           Only episodes available in the given market will be returned.
                           If user-based authorization is in use, the user's country
                           takes precedence. If neither market nor user country are
                           provided, the content is considered unavailable for the client.
        """
        pass

    def search(self, q, limit=10, offset=0, type="track", market=None):
        """ searches for an item

            Parameters:
                - q - the search query (see how to write a query in the
                      official documentation https://developer.spotify.com/documentation/web-api/reference/search/)  # noqa
                - limit - the number of items to return (min = 1, default = 10, max = 50). The limit is applied
                          within each type, not on the total response.
                - offset - the index of the first item to return
                - type - the types of items to return. One or more of 'artist', 'album',
                         'track', 'playlist', 'show', and 'episode'.  If multiple types are desired,
                         pass in a comma separated string; e.g., 'track,album,episode'.
                - market - An ISO 3166-1 alpha-2 country code or the string
                           from_token.
        """
        pass

    def search_markets(self, q, limit=10, offset=0, type="track", markets=None, total=None):
        """ (experimental) Searches multiple markets for an item

            Parameters:
                - q - the search query (see how to write a query in the
                      official documentation https://developer.spotify.com/documentation/web-api/reference/search/)  # noqa
                - limit  - the number of items to return (min = 1, default = 10, max = 50). If a search is to be done on multiple
                            markets, then this limit is applied to each market. (e.g. search US, CA, MX each with a limit of 10).
                            If multiple types are specified, this applies to each type.
                - offset - the index of the first item to return
                - type - the types of items to return. One or more of 'artist', 'album',
                         'track', 'playlist', 'show', or 'episode'. If multiple types are desired, pass in a comma separated string.
                - markets - A list of ISO 3166-1 alpha-2 country codes. Search all country markets by default.
                - total - the total number of results to return across multiple markets and types.
        """
        pass

    def user(self, user):
        """ Gets basic profile information about a Spotify User

            Parameters:
                - user - the id of the usr
        """
        pass

    def current_user_playlists(self, limit=50, offset=0):
        """ Get current user playlists without required getting his profile
            Parameters:
                - limit  - the number of items to return
                - offset - the index of the first item to return
        """
        pass

    def playlist(self, playlist_id, fields=None, market=None, additional_types=("track",)):
        """ Gets playlist by id.

            Parameters:
                - playlist - the id of the playlist
                - fields - which fields to return
                - market - An ISO 3166-1 alpha-2 country code or the
                           string from_token.
                - additional_types - list of item types to return.
                                     valid types are: track and episode
        """
        pass

    def playlist_tracks(
        self,
        playlist_id,
        fields=None,
        limit=50,
        offset=0,
        market=None,
        additional_types=("track",)
    ):
        """ Get full details of the tracks of a playlist.

            .. deprecated::
            This method is deprecated and may be removed in a future version. Use
            `playlist_items(playlist_id, ..., additional_types=('track',))` instead.

            Parameters:
                - playlist_id - the playlist ID, URI or URL
                - fields - which fields to return
                - limit - the maximum number of tracks to return
                - offset - the index of the first track to return
                - market - an ISO 3166-1 alpha-2 country code.
                - additional_types - list of item types to return.
                                     valid types are: track and episode
        """
        pass

    def playlist_items(
        self,
        playlist_id,
        fields=None,
        limit=50,
        offset=0,
        market=None,
        additional_types=("track", "episode")
    ):
        """ Get full details of the tracks and episodes of a playlist.

            Parameters:
                - playlist_id - the playlist ID, URI or URL
                - fields - which fields to return
                - limit - the maximum number of tracks to return
                - offset - the index of the first track to return
                - market - an ISO 3166-1 alpha-2 country code.
                - additional_types - list of item types to return.
                                     valid types are: track and episode
        """
        pass

    def playlist_cover_image(self, playlist_id):
        """ Get cover image of a playlist.

            Parameters:
                - playlist_id - the playlist ID, URI or URL
        """
        pass

    def playlist_upload_cover_image(self, playlist_id, image_b64):
        """ Replace the image used to represent a specific playlist

            Parameters:
                - playlist_id - the id of the playlist
                - image_b64 - image data as a Base64 encoded JPEG image string
                    (maximum payload size is 256 KB)
        """
        pass

    def user_playlist(self, user, playlist_id=None, fields=None, market=None):
        """ Gets a single playlist of a user

            .. deprecated::
            This method is deprecated and may be removed in a future version. Use
            `playlist(playlist_id)` instead.

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - fields - which fields to return
        """
        pass

    def user_playlist_tracks(
        self,
        user=None,
        playlist_id=None,
        fields=None,
        limit=100,
        offset=0,
        market=None,
    ):
        """ Get full details of the tracks of a playlist owned by a user.

            .. deprecated::
            This method is deprecated and may be removed in a future version. Use
            `playlist_tracks(playlist_id)` instead.

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - fields - which fields to return
                - limit - the maximum number of tracks to return
                - offset - the index of the first track to return
                - market - an ISO 3166-1 alpha-2 country code.
        """
        pass

    def user_playlists(self, user, limit=50, offset=0):
        """ Gets playlists of a user

            Parameters:
                - user - the id of the usr
                - limit  - the number of items to return
                - offset - the index of the first item to return
        """
        pass

    def user_playlist_create(self, user, name, public=True, collaborative=False, description=""):
        """ Creates a playlist for a user

            Parameters:
                - user - the id of the user
                - name - the name of the playlist
                - public - is the created playlist public
                - collaborative - is the created playlist collaborative
                - description - the description of the playlist
        """
        pass

    def current_user_playlist_create(self, name, public=True, collaborative=False, description=""):
        """ Creates a playlist for the current user

            Parameters:
                - name - the name of the playlist
                - public - is the created playlist public
                - collaborative - is the created playlist collaborative
                - description - the description of the playlist
        """
        pass

    def user_playlist_change_details(
        self,
        user,
        playlist_id,
        name=None,
        public=None,
        collaborative=None,
        description=None,
    ):
        """ This function is no longer in use, please use the recommended function in the warning!

            Changes a playlist's name and/or public/private state

            .. deprecated::
            This method is deprecated and may be removed in a future version. Use
            `playlist_change_details(playlist_id, ...)` instead.

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - name - optional name of the playlist
                - public - optional is the playlist public
                - collaborative - optional is the playlist collaborative
                - description - optional description of the playlist
        """
        pass

    def user_playlist_unfollow(self, user, playlist_id):
        """ This function is no longer in use, please use the recommended function in the warning!

            Unfollows (deletes) a playlist for a user

            .. deprecated::
            This method is deprecated and may be removed in a future version. Use
            `current_user_unfollow_playlist(playlist_id)` instead.

            Parameters:
                - user - the id of the user
                - name - the name of the playlist
        """
        pass

    def user_playlist_add_tracks(
        self, user, playlist_id, tracks, position=None
    ):
        """ This function is no longer in use, please use the recommended function in the warning!

            Adds tracks to a playlist

            .. deprecated::
            This method is deprecated and may be removed in a future version. Use
            `playlist_add_items(playlist_id, tracks)` instead.

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - tracks - a list of track URIs, URLs or IDs
                - position - the position to add the tracks
        """
        pass

    def user_playlist_add_episodes(
        self, user, playlist_id, episodes, position=None
    ):
        """ This function is no longer in use, please use the recommended function in the warning!

            Adds episodes to a playlist

            .. deprecated::
            This method is deprecated and may be removed in a future version. Use
            `playlist_add_items(playlist_id, episodes)` instead.

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - episodes - a list of track URIs, URLs or IDs
                - position - the position to add the episodes
        """
        pass

    def user_playlist_replace_tracks(self, user, playlist_id, tracks):
        """ This function is no longer in use, please use the recommended function in the warning!

            Replace all tracks in a playlist for a user

            .. deprecated::
            This method is deprecated and may be removed in a future version. Use
            `playlist_replace_items(playlist_id, tracks)` instead.

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - tracks - the list of track ids to add to the playlist
        """
        pass

    def user_playlist_reorder_tracks(
        self,
        user,
        playlist_id,
        range_start,
        insert_before,
        range_length=1,
        snapshot_id=None,
    ):
        """ This function is no longer in use, please use the recommended function in the warning!

            Reorder tracks in a playlist from a user

            .. deprecated::
            This method is deprecated and may be removed in a future version. Use
            `playlist_reorder_items(playlist_id, ...)` instead.

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - range_start - the position of the first track to be reordered
                - range_length - optional the number of tracks to be reordered
                                 (default: 1)
                - insert_before - the position where the tracks should be
                                  inserted
                - snapshot_id - optional playlist's snapshot ID
        """
        pass

    def user_playlist_remove_all_occurrences_of_tracks(
        self, user, playlist_id, tracks, snapshot_id=None
    ):
        """ This function is no longer in use, please use the recommended function in the warning!

            Removes all occurrences of the given tracks from the given playlist

            .. deprecated::
            This method is deprecated and may be removed in a future version. Use
            `playlist_remove_all_occurrences_of_items(playlist_id, tracks)` instead.

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - tracks - the list of track ids to remove from the playlist
                - snapshot_id - optional id of the playlist snapshot
        """
        pass

    def user_playlist_remove_specific_occurrences_of_tracks(
        self, user, playlist_id, tracks, snapshot_id=None
    ):
        """ This function is no longer in use, please use the recommended function in the warning!

            Removes specific occurrences of the given tracks from the given playlist

            .. deprecated::
            This endpoint has been removed by Spotify and is no longer available.

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - tracks - an array of objects containing Spotify URIs of the
                    tracks to remove with their current positions in the
                    playlist.  For example:
                        [  { "uri":"4iV5W9uYEdYUVa79Axb7Rh", "positions":[2] },
                        { "uri":"1301WleyT98MSxVHPZCA6M", "positions":[7] } ]
                - snapshot_id - optional id of the playlist snapshot
        """
        pass

    def user_playlist_follow_playlist(self, playlist_owner_id, playlist_id):
        """ This function is no longer in use, please use the recommended function in the warning!

            Add the current authenticated user as a follower of a playlist.

            .. deprecated::
            This method is deprecated and may be removed in a future version. Use
            `current_user_follow_playlist(playlist_id)` instead.

            Parameters:
                - playlist_owner_id - the user id of the playlist owner
                - playlist_id - the id of the playlist
        """
        pass

    def user_playlist_is_following(
        self, playlist_owner_id, playlist_id, user_ids
    ):
        """ This function is no longer in use, please use the recommended function in the warning!

            Check to see if the given users are following the given playlist

            .. deprecated::
            This method is deprecated and may be removed in a future version. Use
            `playlist_is_following(playlist_id, user_ids)` instead.

            Parameters:
                - playlist_owner_id - the user id of the playlist owner
                - playlist_id - the id of the playlist
                - user_ids - the ids of the users that you want to check to see
                    if they follow the playlist. Maximum: 5 ids.
        """
        pass

    def playlist_change_details(
        self,
        playlist_id,
        name=None,
        public=None,
        collaborative=None,
        description=None,
    ):
        """ Changes a playlist's name and/or public/private state,
            collaborative state, and/or description

            Parameters:
                - playlist_id - the id of the playlist
                - name - optional name of the playlist
                - public - optional is the playlist public
                - collaborative - optional is the playlist collaborative
                - description - optional description of the playlist
        """
        pass

    def current_user_unfollow_playlist(self, playlist_id):
        """ Unfollows (deletes) a playlist for the current authenticated
            user

            Parameters:
                - playlist_id - the id of the playlist
        """
        pass

    def playlist_add_items(
        self, playlist_id, items, position=None
    ):
        """ Adds tracks/episodes to a playlist

            Parameters:
                - playlist_id - the id of the playlist
                - items - a list of track/episode URIs or URLs
                - position - the position to add the tracks
        """
        pass

    def playlist_replace_items(self, playlist_id, items):
        """ Replace all tracks/episodes in a playlist

            Parameters:
                - playlist_id - the id of the playlist
                - items - list of track/episode ids to comprise playlist
        """
        pass

    def playlist_reorder_items(
        self,
        playlist_id,
        range_start,
        insert_before,
        range_length=1,
        snapshot_id=None,
    ):
        """ Reorder tracks in a playlist

            Parameters:
                - playlist_id - the id of the playlist
                - range_start - the position of the first track to be reordered
                - range_length - optional the number of tracks to be reordered
                                 (default: 1)
                - insert_before - the position where the tracks should be
                                  inserted
                - snapshot_id - optional playlist's snapshot ID
        """
        pass

    def playlist_remove_all_occurrences_of_items(
        self, playlist_id, items, snapshot_id=None
    ):
        """ Removes all occurrences of the given tracks/episodes from the given playlist

            Parameters:
                - playlist_id - the id of the playlist
                - items - list of track/episode ids to remove from the playlist
                - snapshot_id - optional id of the playlist snapshot

        """
        pass

    def playlist_remove_specific_occurrences_of_items(
        self, playlist_id, items, snapshot_id=None
    ):
        """ Removes all occurrences of the given tracks from the given playlist

            Parameters:
                - playlist_id - the id of the playlist
                - items - an array of objects containing Spotify URIs of the
                    tracks/episodes to remove with their current positions in
                    the playlist.  For example:
                        [  { "uri":"4iV5W9uYEdYUVa79Axb7Rh", "positions":[2] },
                        { "uri":"1301WleyT98MSxVHPZCA6M", "positions":[7] } ]
                - snapshot_id - optional id of the playlist snapshot
        """
        pass

    def current_user_follow_playlist(self, playlist_id):
        """
        Add the current authenticated user as a follower of a playlist.

        Parameters:
            - playlist_id - the id of the playlist

        """
        pass

    def playlist_is_following(
        self, playlist_id, user_ids
    ):
        """
        Check to see if the given users are following the given playlist

        Parameters:
            - playlist_id - the id of the playlist
            - user_ids - the ids of the users that you want to check to see
                if they follow the playlist. Maximum: 5 ids.

        """
        pass

    def current_user_saved_items(self, uris):
        """
        Check if the current user is following the given artists, users, or playlists

        Parameters:
            - uris - a list of URIs to check for following status. Maximum: 40 ids.

        """
        pass

    def me(self):
        """ Get detailed profile information about the current user.
            An alias for the 'current_user' method.
        """
        pass

    def current_user(self):
        """ Get detailed profile information about the current user.
            An alias for the 'me' method.
        """
        pass

    def current_user_playing_track(self, market=None, additional_types=("track",)):
        """ Get information about the current users currently playing track.

            Parameters:
                - market - An ISO 3166-1 alpha-2 country code or the
                           string from_token.
                - additional_types - list of item types to return.
                                     valid types are: track and episode
        """
        pass

    def current_user_saved_albums(self, limit=20, offset=0, market=None):
        """ Gets a list of the albums saved in the current authorized user's
            "Your Music" library

            Parameters:
                - limit - the number of albums to return (MAX_LIMIT=50)
                - offset - the index of the first album to return
                - market - an ISO 3166-1 alpha-2 country code.

        """
        pass

    def current_user_saved_albums_add(self, albums=[]):
        """ Add one or more albums to the current user's
            "Your Music" library.
            Parameters:
                - albums - a list of album URIs, URLs or IDs
        """
        pass

    def current_user_saved_albums_delete(self, albums=[]):
        """ Remove one or more albums from the current user's
            "Your Music" library.

            Parameters:
                - albums - a list of album URIs, URLs or IDs
        """
        pass

    def current_user_saved_albums_contains(self, albums=[]):
        """ Check if one or more albums is already saved in
            the current Spotify user’s “Your Music” library.

            Parameters:
                - albums - a list of album URIs, URLs or IDs
        """
        pass

    def current_user_saved_tracks(self, limit=20, offset=0, market=None):
        """ Gets a list of the tracks saved in the current authorized user's
            "Your Music" library

            Parameters:
                - limit - the number of tracks to return
                - offset - the index of the first track to return
                - market - an ISO 3166-1 alpha-2 country code

        """
        pass

    def current_user_saved_tracks_add(self, tracks=None):
        """ Add one or more tracks to the current user's
            "Your Music" library.

            Parameters:
                - tracks - a list of track URIs, URLs or IDs
        """
        pass

    def current_user_saved_tracks_delete(self, tracks=None):
        """ Remove one or more tracks from the current user's
            "Your Music" library.

            Parameters:
                - tracks - a list of track URIs, URLs or IDs
        """
        pass

    def current_user_saved_tracks_contains(self, tracks=None):
        """ Check if one or more tracks is already saved in
            the current Spotify user’s “Your Music” library.

            Parameters:
                - tracks - a list of track URIs, URLs or IDs
        """
        pass

    def current_user_saved_episodes(self, limit=20, offset=0, market=None):
        """ Gets a list of the episodes saved in the current authorized user's
            "Your Music" library

            Parameters:
                - limit - the number of episodes to return
                - offset - the index of the first episode to return
                - market - an ISO 3166-1 alpha-2 country code

        """
        pass

    def current_user_saved_episodes_add(self, episodes=None):
        """ Add one or more episodes to the current user's
            "Your Music" library.

            Parameters:
                - episodes - a list of episode URIs, URLs or IDs
        """
        pass

    def current_user_saved_episodes_delete(self, episodes=None):
        """ Remove one or more episodes from the current user's
            "Your Music" library.

            Parameters:
                - episodes - a list of episode URIs, URLs or IDs
        """
        pass

    def current_user_saved_episodes_contains(self, episodes=None):
        """ Check if one or more episodes is already saved in
            the current Spotify user’s “Your Music” library.

            Parameters:
                - episodes - a list of episode URIs, URLs or IDs
        """
        pass

    def current_user_saved_shows(self, limit=20, offset=0, market=None):
        """ Gets a list of the shows saved in the current authorized user's
            "Your Music" library

            Parameters:
                - limit - the number of shows to return
                - offset - the index of the first show to return
                - market - an ISO 3166-1 alpha-2 country code

        """
        pass

    def current_user_saved_shows_add(self, shows=[]):
        """ Add one or more albums to the current user's
            "Your Music" library.
            Parameters:
                - shows - a list of show URIs, URLs or IDs
        """
        pass

    def current_user_saved_shows_delete(self, shows=[]):
        """ Remove one or more shows from the current user's
            "Your Music" library.

            Parameters:
                - shows - a list of show URIs, URLs or IDs
        """
        pass

    def current_user_saved_shows_contains(self, shows=[]):
        """ Check if one or more shows is already saved in
            the current Spotify user’s “Your Music” library.

            Parameters:
                - shows - a list of show URIs, URLs or IDs
        """
        pass

    def current_user_followed_artists(self, limit=20, after=None):
        """ Gets a list of the artists followed by the current authorized user

            Parameters:
                - limit - the number of artists to return
                - after - the last artist ID retrieved from the previous
                          request

        """
        pass

    def current_user_following_artists(self, ids=None):
        """ Check if the current user is following certain artists

            Returns list of booleans respective to ids

            Parameters:
                - ids - a list of artist URIs, URLs or IDs
        """
        pass

    def current_user_following_users(self, ids=None):
        """ Check if the current user is following certain users

            Returns list of booleans respective to ids

            Parameters:
                - ids - a list of user URIs, URLs or IDs
        """
        pass

    def current_user_top_artists(
        self, limit=20, offset=0, time_range="medium_term"
    ):
        """ Get the current user's top artists

            Parameters:
                - limit - the number of entities to return (max 50)
                - offset - the index of the first entity to return
                - time_range - Over what time frame are the affinities computed
                  Valid-values: short_term, medium_term, long_term
        """
        pass

    def current_user_top_tracks(
        self, limit=20, offset=0, time_range="medium_term"
    ):
        """ Get the current user's top tracks

            Parameters:
                - limit - the number of entities to return
                - offset - the index of the first entity to return
                - time_range - Over what time frame are the affinities computed
                  Valid-values: short_term, medium_term, long_term
        """
        pass

    def current_user_recently_played(self, limit=50, after=None, before=None):
        """ Get the current user's recently played tracks

            Parameters:
                - limit - the number of entities to return
                - after - unix timestamp in milliseconds. Returns all items
                          after (but not including) this cursor position.
                          Cannot be used if before is specified.
                - before - unix timestamp in milliseconds. Returns all items
                           before (but not including) this cursor position.
                           Cannot be used if after is specified
        """
        pass

    def user_follow_artists(self, ids=[]):
        """ Follow one or more artists
            Parameters:
                - ids - a list of artist IDs
        """
        pass

    def user_follow_users(self, ids=[]):
        """ Follow one or more users
            Parameters:
                - ids - a list of user IDs
        """
        pass

    def user_unfollow_artists(self, ids=[]):
        """ Unfollow one or more artists
            Parameters:
                - ids - a list of artist IDs
        """
        pass

    def user_unfollow_users(self, ids=[]):
        """ Unfollow one or more users
            Parameters:
                - ids - a list of user IDs
        """
        pass

    def featured_playlists(
        self, locale=None, country=None, timestamp=None, limit=20, offset=0
    ):
        """ Get a list of Spotify featured playlists

            .. deprecated::
            This endpoint has been removed by Spotify and is no longer available.

            Parameters:
                - locale - The desired language, consisting of a lowercase ISO
                  639-1 alpha-2 language code and an uppercase ISO 3166-1 alpha-2
                  country code, joined by an underscore.

                - country - An ISO 3166-1 alpha-2 country code.

                - timestamp - A timestamp in ISO 8601 format:
                  yyyy-MM-ddTHH:mm:ss. Use this parameter to specify the user's
                  local time to get results tailored for that specific date and
                  time in the day

                - limit - The maximum number of items to return. Default: 20.
                  Minimum: 1. Maximum: 50

                - offset - The index of the first item to return. Default: 0
                  (the first object). Use with limit to get the next set of
                  items.
        """
        pass

    def new_releases(self, country=None, limit=20, offset=0):
        """ Get a list of new album releases featured in Spotify

            Parameters:
                - country - An ISO 3166-1 alpha-2 country code.

                - limit - The maximum number of items to return. Default: 20.
                  Minimum: 1. Maximum: 50

                - offset - The index of the first item to return. Default: 0
                  (the first object). Use with limit to get the next set of
                  items.
        """
        pass

    def category(self, category_id, country=None, locale=None):
        """ Get info about a category

            Parameters:
                - category_id - The Spotify category ID for the category.

                - country - An ISO 3166-1 alpha-2 country code.
                - locale - The desired language, consisting of an ISO 639-1 alpha-2
                  language code and an ISO 3166-1 alpha-2 country code, joined
                  by an underscore.
        """
        pass

    def categories(self, country=None, locale=None, limit=20, offset=0):
        """ Get a list of categories

            Parameters:
                - country - An ISO 3166-1 alpha-2 country code.
                - locale - The desired language, consisting of an ISO 639-1 alpha-2
                  language code and an ISO 3166-1 alpha-2 country code, joined
                  by an underscore.

                - limit - The maximum number of items to return. Default: 20.
                  Minimum: 1. Maximum: 50

                - offset - The index of the first item to return. Default: 0
                  (the first object). Use with limit to get the next set of
                  items.
        """
        pass

    def category_playlists(
        self, category_id=None, country=None, limit=20, offset=0
    ):
        """ Get a list of playlists for a specific Spotify category

            .. deprecated::
            This endpoint has been removed by Spotify and is no longer available.

            Parameters:
                - category_id - The Spotify category ID for the category.

                - country - An ISO 3166-1 alpha-2 country code.

                - limit - The maximum number of items to return. Default: 20.
                  Minimum: 1. Maximum: 50

                - offset - The index of the first item to return. Default: 0
                  (the first object). Use with limit to get the next set of
                  items.
        """
        pass

    def recommendations(
        self,
        seed_artists=None,
        seed_genres=None,
        seed_tracks=None,
        limit=20,
        country=None,
        **kwargs
    ):
        """ Get a list of recommended tracks for one to five seeds.
            (at least one of `seed_artists`, `seed_tracks` and `seed_genres`
            are needed)

            .. deprecated::
            This endpoint has been removed by Spotify and is no longer available.

            Parameters:
                - seed_artists - a list of artist IDs, URIs or URLs
                - seed_tracks - a list of track IDs, URIs or URLs
                - seed_genres - a list of genre names. Available genres for
                                recommendations can be found by calling
                                recommendation_genre_seeds

                - country - An ISO 3166-1 alpha-2 country code. If provided,
                            all results will be playable in this country.

                - limit - The maximum number of items to return. Default: 20.
                          Minimum: 1. Maximum: 100

                - min/max/target_<attribute> - For the tuneable track
                    attributes listed in the documentation, these values
                    provide filters and targeting on results.
        """
        pass

    def recommendation_genre_seeds(self):
        """ Get a list of genres available for the recommendations function.

            .. deprecated::
            This endpoint has been removed by Spotify and is no longer available.
        """
        pass

    def audio_analysis(self, track_id):
        """ Get audio analysis for a track based upon its Spotify ID

            .. deprecated::
            This endpoint has been removed by Spotify and is no longer available.

            Parameters:
                - track_id - a track URI, URL or ID
        """
        pass

    def audio_features(self, tracks=[]):
        """ Get audio features for one or multiple tracks based upon their Spotify IDs

            .. deprecated::
            This endpoint has been removed by Spotify and is no longer available.

            Parameters:
                - tracks - a list of track URIs, URLs or IDs, maximum: 100 ids
        """
        pass

    def devices(self):
        """ Get a list of user's available devices.
        """
        pass

    def current_playback(self, market=None, additional_types=None):
        """ Get information about user's current playback.

            Parameters:
                - market - an ISO 3166-1 alpha-2 country code.
                - additional_types - `episode` to get podcast track information
        """
        pass

    def currently_playing(self, market=None, additional_types=None):
        """ Get user's currently playing track.

            Parameters:
                - market - an ISO 3166-1 alpha-2 country code.
                - additional_types - `episode` to get podcast track information
        """
        pass

    def transfer_playback(self, device_id, force_play=True):
        """ Transfer playback to another device.
            Note that the API accepts a list of device ids, but only
            actually supports one.

            Parameters:
                - device_id - transfer playback to this device
                - force_play - true: after transfer, play. false:
                               keep current state.
        """
        pass

    def start_playback(
        self, device_id=None, context_uri=None, uris=None, offset=None, position_ms=None
    ):
        """ Start or resume user's playback.

            Provide a `context_uri` to start playback of an album,
            artist, or playlist.

            Provide a `uris` list to start playback of one or more
            tracks.

            Provide `offset` as {"position": <int>} or {"uri": "<track uri>"}
            to start playback at a particular offset.

            Parameters:
                - device_id - device target for playback
                - context_uri - spotify context uri to play
                - uris - spotify track uris
                - offset - offset into context by index or track
                - position_ms - (optional) indicates from what position to start playback.
                                Must be a positive number. Passing in a position that is
                                greater than the length of the track will cause the player to
                                start playing the next song.
        """
        pass

    def pause_playback(self, device_id=None):
        """ Pause user's playback.

            Parameters:
                - device_id - device target for playback
        """
        pass

    def next_track(self, device_id=None):
        """ Skip user's playback to next track.

            Parameters:
                - device_id - device target for playback
        """
        pass

    def previous_track(self, device_id=None):
        """ Skip user's playback to previous track.

            Parameters:
                - device_id - device target for playback
        """
        pass

    def seek_track(self, position_ms, device_id=None):
        """ Seek to position in current track.

            Parameters:
                - position_ms - position in milliseconds to seek to
                - device_id - device target for playback
        """
        pass

    def repeat(self, state, device_id=None):
        """ Set repeat mode for playback.

            Parameters:
                - state - `track`, `context`, or `off`
                - device_id - device target for playback
        """
        pass

    def volume(self, volume_percent, device_id=None):
        """ Set playback volume.

            Parameters:
                - volume_percent - volume between 0 and 100
                - device_id - device target for playback
        """
        pass

    def shuffle(self, state, device_id=None):
        """ Toggle playback shuffling.

            Parameters:
                - state - true or false
                - device_id - device target for playback
        """
        pass

    def queue(self):
        """ Gets the current user's queue """
        pass

    def add_to_queue(self, uri, device_id=None):
        """ Adds a song to the end of a user's queue

            If device A is currently playing music, and you try to add to the queue
            and pass in the id for device B, you will get a
            'Player command failed: Restriction violated' error
            I therefore recommend leaving device_id as None so that the active device is targeted

            :param uri: song uri, id, or url
            :param device_id:
                the id of a Spotify device.
                If None, then the active device is used.

        """
        pass

    def available_markets(self):
        """ Get the list of markets where Spotify is available.
            Returns a list of the countries in which Spotify is available, identified by their
            ISO 3166-1 alpha-2 country code with additional country codes for special territories.
        """
        pass

    def _append_device_id(self, path, device_id):
        """ Append device ID to API path.

            Parameters:
                - device_id - device id to append
        """
        pass





    def get_audiobook(self, id, market=None):
        """ Get Spotify catalog information for a single audiobook identified by its unique
        Spotify ID.

        Parameters:
        - id - the Spotify ID for the audiobook
        - market - an ISO 3166-1 alpha-2 country code.
        """
        pass

    def get_audiobooks(self, ids, market=None):
        """ Get Spotify catalog information for multiple audiobooks based on their Spotify IDs.

        Parameters:
        - ids - a list of Spotify IDs for the audiobooks
        - market - an ISO 3166-1 alpha-2 country code.
        """
        pass

    def get_audiobook_chapters(self, id, market=None, limit=20, offset=0):
        """ Get Spotify catalog information about an audiobook’s chapters.

        Parameters:
        - id - the Spotify ID for the audiobook
        - market - an ISO 3166-1 alpha-2 country code.
        - limit - the maximum number of items to return
        - offset - the index of the first item to return
        """
        pass
