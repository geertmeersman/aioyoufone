# aioyoufone

Asynchronous library to communicate with the Youfone API

[![maintainer](https://img.shields.io/badge/maintainer-Geert%20Meersman-green?style=for-the-badge&logo=github)](https://github.com/geertmeersman)
[![buyme_coffee](https://img.shields.io/badge/Buy%20me%20a%20Duvel-donate-yellow?style=for-the-badge&logo=buymeacoffee)](https://www.buymeacoffee.com/geertmeersman)
[![discord](https://img.shields.io/discord/1094198226493636638?style=for-the-badge&logo=discord)](https://discord.gg/s8JNwREmxV)

[![MIT License](https://img.shields.io/github/license/geertmeersman/aioyoufone?style=flat-square)](https://github.com/geertmeersman/aioyoufone/blob/master/LICENSE)

[![GitHub issues](https://img.shields.io/github/issues/geertmeersman/aioyoufone)](https://github.com/geertmeersman/aioyoufone/issues)
[![Average time to resolve an issue](http://isitmaintained.com/badge/resolution/geertmeersman/aioyoufone.svg)](http://isitmaintained.com/project/geertmeersman/aioyoufone)
[![Percentage of issues still open](http://isitmaintained.com/badge/open/geertmeersman/aioyoufone.svg)](http://isitmaintained.com/project/geertmeersman/aioyoufone)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](https://github.com/geertmeersman/aioyoufone/pulls)

[![Python](https://img.shields.io/badge/Python-FFD43B?logo=python)](https://github.com/geertmeersman/aioyoufone/search?l=python)

[![github release](https://img.shields.io/github/v/release/geertmeersman/aioyoufone?logo=github)](https://github.com/geertmeersman/aioyoufone/releases)
[![github release date](https://img.shields.io/github/release-date/geertmeersman/aioyoufone)](https://github.com/geertmeersman/aioyoufone/releases)
[![github last-commit](https://img.shields.io/github/last-commit/geertmeersman/aioyoufone)](https://github.com/geertmeersman/aioyoufone/commits)
[![github contributors](https://img.shields.io/github/contributors/geertmeersman/aioyoufone)](https://github.com/geertmeersman/aioyoufone/graphs/contributors)
[![github commit activity](https://img.shields.io/github/commit-activity/y/geertmeersman/aioyoufone?logo=github)](https://github.com/geertmeersman/aioyoufone/commits/main)

## API Example

```python
"""Test for aioyoufone."""
from aioyoufone import YoufoneClient
import json
import asyncio
import logging

# Setup logging
logger = logging.getLogger(__name__)

async def main():
    client = YoufoneClient(
        "user@email.com",
        "YourPassword",
        "nl",
        None,
        True
    )

    try:
        customer_data = await client.fetch_data()
        if isinstance(customer_data, dict) and 'error' in customer_data:
            logging.error("Error occurred while retrieving customer data: %s", customer_data['error'])
        else:
            logging.info("Customer data retrieved successfully: %s", json.dumps(customer_data, indent=4, sort_keys=True))
    except Exception as e:
        logging.error("Error occurred while retrieving customer data: %s", str(e))
    finally:
        await client.close_session()

logging.basicConfig(level=logging.INFO)
asyncio.run(main())
```
