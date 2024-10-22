class StreamingFetcherException(Exception):
    pass


class FetchEpisodeFailed(StreamingFetcherException):
    pass


class FetchEpisodeRateLimitExceeded(FetchEpisodeFailed):
    pass
