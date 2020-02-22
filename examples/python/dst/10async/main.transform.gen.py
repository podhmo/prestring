import asyncio
async def main():
    print('Hello ...')
    await asyncio.sleep(0.1)
    print('... World!')


asyncio.get_event_loop().run_until_complete(main())
