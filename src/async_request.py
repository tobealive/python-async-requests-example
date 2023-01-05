import asyncio, time, requests
from aiohttp import ClientSession

urls = requests.get(
	"https://gist.githubusercontent.com/tobealive/b2c6e348dac6b3f0ffa150639ad94211/raw/e90479f11e179b7f65c60a8477f060e740061815/100-popular-urls.txt"
).text.split('\n')
durations: list[float] = []
errorNum = 0


async def getHttpResp(url: str, session: ClientSession):
	try:
		async with session.get(url) as resp:
			result = await resp.read()
			print(f"{url} - response length: {len(result)}")
	except Exception as e:
		global errorNum
		errorNum += 1
		print(f"Error: {url} - {e.__class__}")


async def requestUrls(urls: list[str]):
	start = time.time()
	print("Starting requests...")

	async with ClientSession() as session:
		await asyncio.gather(*[getHttpResp(f"http://www.{url}", session) for url in urls])

	duration = time.time() - start
	durations.append(duration)
	print(f"Requested {len(urls)} websites in {duration}.")


iterations = 1

for i in range(iterations):
	print(f"Iteration {i + 1}/{iterations}")
	asyncio.run(requestUrls(urls))

sum = 0.0

for i in range(len(durations)):
	v = durations[i]
	sum += v
	print(f"{i + 1}: {v}")

print(f"""
Iterations: {iterations}. Total errors: {errorNum}.
Average time to request {len(urls)} websites: {sum / len(durations)}.
""")
