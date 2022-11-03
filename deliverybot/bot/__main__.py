# https://stackoverflow.com/questions/53130265/python-run-package-with-python3-6-m-somepackge-run
import asyncio

from deliverybot.bot import main


if __name__ == "__main__":
    asyncio.run(main())
