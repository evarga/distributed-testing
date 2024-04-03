import pytest
from hamcrest import assert_that, equal_to, has_entry, has_length
from mbtest.imposters import Imposter, Stub, Predicate, Response
from mbtest.matchers import had_request
from suts import album_viewer


# This is a coarse-grained test that exercises the album_viewer module. In a more complex scenario, we would have
# multiple tests that would test each function in the module.
def test_album_viewer(mock_server, config):
    # Set up the imposter to virtualize Spotify services.
    imposter = Imposter((Stub(Predicate(path="/api/token",
                                        method="POST",
                                        body="client_id=0000",
                                        operator=Predicate.Operator.CONTAINS),
                              Response(
                                  body='{"error":"invalid_client","error_description":"Invalid client"}',
                                  status_code=400)),
                         Stub(Predicate(path="/api/token",
                                        method="POST"),
                              Response(
                                  body={
                                      "access_token": "ABCD",
                                      "token_type": "Bearer",
                                      "expires_in": 3600
                                  },
                                  status_code=200)),
                         Stub(Predicate(path="/v1/search",
                                        method="GET",
                                        query={"q": "Test Artist",
                                               "type": "artist",
                                               "limit": 1}),
                              Response(
                                  # We don't need to return the whole response, just the part that the function uses.
                                  body={
                                      "artists": {
                                          "items": [{"id": "1"}]
                                      }
                                  },
                                  status_code=200)),
                         Stub(Predicate(path="/v1/artists/1/albums",
                                        method="GET"),
                              Response(
                                  body={
                                      "items": [
                                          {"name": "Album 1"},
                                          {"name": "Album 2"}
                                      ]
                                  },
                                  status_code=200))),
                        port=config["spotify_server_port"],
                        name="Virtualized Spotify API")
    base_addr = f"http://{config['spotify_server_host']}:{config['spotify_server_port']}"

    with mock_server(imposter):
        try:
            album_viewer.get_access_token("0000", "1111", base_addr)
            pytest.fail("Should have raised an exception due to invalid client id.")
        except Exception as e:
            assert_that(
                str(e),
                equal_to("Failed to get access token: "
                         "{\"error\":\"invalid_client\",\"error_description\":\"Invalid client\"}"))

        access_token = album_viewer.get_access_token("1111", "2222", base_addr)
        assert_that(access_token, equal_to("ABCD"))

        artist_id = album_viewer.get_artist("Test Artist", access_token, base_addr)
        assert_that(imposter, had_request().with_headers(has_entry("Authorization", f"Bearer {access_token}")))
        assert_that(artist_id, equal_to("1"))

        albums = album_viewer.get_albums(artist_id, access_token, base_addr)
        assert_that(albums, has_length(2))
        assert_that(albums[1], has_entry("name", "Album 2"))
