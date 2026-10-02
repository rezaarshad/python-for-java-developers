# asyncio basics

async def creates a coroutine; await pauses it while waiting for I/O. asyncio.gather runs many coroutines
concurrently, and a Semaphore limits how many run at once, which is useful for API rate limits.
Never call time.sleep inside async code; use await asyncio.sleep instead.
