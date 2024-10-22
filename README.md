# Streaming fetcher

[![GitHub](https://img.shields.io/github/license/RobertoBochet/streaming-fetcher?style=flat-square)](https://github.com/RobertoBochet/streaming-fetcher)
[![GitHub Version](https://img.shields.io/github/v/tag/RobertoBochet/streaming-fetcher?label=version&style=flat-square)](https://github.com/RobertoBochet/streaming-fetcher)
[![PyPI - Version](https://img.shields.io/pypi/v/streaming-fetcher?style=flat-square)](https://pypi.org/project/streaming-fetcher/)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/RobertoBochet/streaming-fetcher/test-code.yml?label=test%20code&style=flat-square)](https://github.com/RobertoBochet/streaming-fetcher)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/RobertoBochet/streaming-fetcher/release.yml?label=publish%20release&style=flat-square)](https://github.com/RobertoBochet/streaming-fetcher/pkgs/container/streaming-fetcher)
[![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/RobertoBochet/streaming-fetcher?style=flat-square)](https://www.codefactor.io/repository/github/robertobochet/streaming-fetcher)

Streaming fetcher library can be used to automatize downloads from streaming sites.

## Disclaimer

> This project is in no way meant to be an incitement to piracy.
> But publishers often have no respect for the works they own the rights to.
> If a product is no longer profitable, it disappears into thin air and becomes legally unobtainable.
> This project exists to preserve these works of art.

## Using

The library can be found on PyPi

```shell
pip install streaming-fetcher
```

The library needs to work playwright firefox. Before using it, you have to initialize it
```shell
playwright install --with-deps firefox
```
More information available in the [official docs](https://playwright.dev/python/docs/intro#installing-playwright-pytest)

### Example

```python
import asyncio
import logging
from pathlib import Path
from streaming_fetcher import StreamingFetcher, AnimeUnityFetchTask

# streaming_fetcher uses the python standard logging library
logging.basicConfig(level=logging.INFO)

anime_fetcher = StreamingFetcher(base_path=Path('/mnt/media-library'))

# add a task to retrieve episodes from anime unity
anime_fetcher.add_task(AnimeUnityFetchTask("42-hitchhikers-guide", episode_path=lambda season,episode: Path("Hitchhiker's Guide") / f"Hitchhiker's Guide S{season:02d}E{episode:02d}.mp4"))

asyncio.run(anime_fetcher.run())
```

## Supported sites

- streamingcommunity.computer `StreamingCommunityFetchTask`
- animeunity.to `AnimeUnityFetchTask`
