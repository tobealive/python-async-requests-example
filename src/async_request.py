import asyncio, time, requests
from aiohttp import ClientSession
from typing import TypedDict
from enum import Enum

url_source = "https://gist.githubusercontent.com/tobealive/b2c6e348dac6b3f0ffa150639ad94211/raw/31524a7aac392402e354bced9307debd5315f0e8/100-popular-urls.txt"
seperator = "-------------------------------------------------------------------------------"

ResultStatus = Enum('ResultStatus', 'SUCCESS ERROR TIMEOUT PENDING')
TestResult = dict[str, TypedDict("TestResultData", status=ResultStatus, transferred=int, time=float)]
Stats = TypedDict("Stats", time=float, successes=int, errors=int, timeouts=int, transferred=float)

results: TestResult = {}
summary: Stats = {"time": 0, "successes": 0, "errors": 0, "timeouts": 0, "transferred": 0}
outputs: list[str] = []

iterations = 10
single_source = False
verbose = False


def prep_urls() -> list[str]:
	if single_source:
		urls = []
		for i in range(100):
			urls.append(f"google.com/search?q={i}")
		return urls

	urls = requests.get(url_source).text.split('\n')
	urls = list(dict.fromkeys(urls))[:100]  # remove duplicats limit to 100 urls
	return urls


async def get_http_resp(url: str, session: ClientSession):
	start_time = time.time()

	try:
		async with session.get(f"http://www.{url}") as resp:
			response = await resp.read()
			res_len = len(response)
			result = results[url]
			result["status"] = ResultStatus.SUCCESS
			result["transferred"] = res_len
			if verbose:
				results[url]["time"] = time.time() - start_time
				print(f"{url}: - Transferred: {res_len} Bytes. Time: {results[url]['time']:.4f}s.")
	except Exception as e:
		global errorNum
		results[url]["time"] = time.time() - start_time
		results[url]["status"] = ResultStatus.ERROR
		if verbose:
			print(f"Error: {url} - {e.__class__}")


async def spawn_requests(urls: list[str]) -> float:
	start = time.time()

	async with ClientSession() as session:
		await asyncio.gather(*[get_http_resp(url, session) for url in urls])

	duration = time.time() - start

	if verbose:
		print(f"Requested {len(urls)} websites in {duration:.2f}s.")

	return duration


def eval() -> Stats:
	stats: Stats = {"time": 0.0, "successes": 0, "errors": 0, "timeouts": 0, "transferred": 0}
	for res in results.values():
		stats["transferred"] += res["transferred"]
		stats["successes"] += res["status"] == ResultStatus.SUCCESS
		stats["errors"] += res["status"] == ResultStatus.ERROR
		stats["timeouts"] += res["status"] == ResultStatus.TIMEOUT

		summary["transferred"] += res["transferred"]
		summary["successes"] += res["status"] == ResultStatus.SUCCESS
		summary["errors"] += res["status"] == ResultStatus.ERROR
		summary["timeouts"] += res["status"] == ResultStatus.TIMEOUT

	stats['transferred'] = stats['transferred'] / (1024 * 1024)

	return stats


def main():
	urls = prep_urls()

	print("Starting requests...")

	for i in range(iterations):
		print(f"Run: {i + 1}/{iterations}")

		for url in urls:
			results[url] = {"status": ResultStatus.PENDING, "transferred": 0, "time": 0.0}

		duration = asyncio.run(spawn_requests(urls))

		stats = eval()
		stats["time"] = duration
		summary["time"] += duration

		output = f"{i + 1}: Time: {stats['time']:.2f}s. Sent: {stats['successes'] + stats['errors'] + stats['timeouts']}. Successes: {stats['successes']}. Errors: {stats['errors']}. Timeouts: {stats['timeouts']}. Transferred: {stats['transferred']:.2f} MB ({stats['transferred'] / stats['time']:.2f} MB/s)."

		outputs.append(output)

		if verbose:
			print(f"{seperator}\n{output}\n")

	if len(outputs) <= 1 and verbose:
		return

	print(f"{seperator}")

	for output in outputs:
		print(output)

	summary['transferred'] = summary['transferred'] / (1024 * 1024)

	print(f"""{seperator}
Runs: {iterations}. Average Time: {summary['time'] / float(len(outputs)):.2f}s. Total Errors: {summary['errors']}. Total Timeouts: {summary['timeouts']}. Transferred: {summary['transferred']:.2f} MB ({summary['transferred']/summary['time']:.2f} MB/s).
{seperator}
""")


main()
