import asyncio, time, requests
from aiohttp import ClientSession
from typing import TypedDict
from enum import Enum

url_source = "https://gist.githubusercontent.com/tobealive/b2c6e348dac6b3f0ffa150639ad94211/raw/3db61fe72e1ce6854faa025298bf4cdfd2b2f250/100-popular-urls.txt"
seperator = '-' * 80
iterations = 10
single_source = False
verbose = True
timeout = 5

ResultStatus = Enum('ResultStatus', 'SUCCESS ERROR PENDING')
TestResult = TypedDict("TestResult", url=str, status=ResultStatus, transferred=int, time=float)
Stats = TypedDict("Stats", time=float, successes=int, errors=int, timeouts=int, transferred=float)

summary: Stats = {"time": 0, "successes": 0, "errors": 0, "timeouts": 0, "transferred": 0}
outputs: list[str] = []


def prep_urls() -> list[str]:
	if single_source:
		urls = [(f"google.com/search?q={i}") for i in range(100)]
		return urls

	urls = requests.get(url_source).text.split('\n')
	urls = list(dict.fromkeys(urls))[:100]  # remove duplicats, limit to 100 urls
	return urls


async def get_http_resp(session: ClientSession, url: str) -> TestResult:
	test_result: TestResult = {"url": url, "status": ResultStatus.PENDING, "transferred": 0, "time": 0}
	start_time = time.time()

	try:
		async with session.get(f"http://www.{url}", timeout=timeout) as resp:
			response = await resp.read()
			res_len = len(response)
			test_result["status"] = ResultStatus.SUCCESS
			test_result["transferred"] = res_len
			test_result["time"] = time.time() - start_time
			if verbose:
				print(f"{url} — Transferred: {res_len} Bytes. Time: {test_result['time']:.2f}s.")
	except Exception as e:
		test_result["time"] = time.time() - start_time
		test_result["status"] = ResultStatus.ERROR
		if verbose:
			print(f"Error: {url} — {e.__class__}")

	return test_result


async def spawn_requests(urls: list[str]) -> list[TestResult]:
	async with ClientSession() as session:
		return await asyncio.gather(*[get_http_resp(session, url) for url in urls])


def eval(results: list[TestResult]) -> Stats:
	stats: Stats = {"time": 0.0, "successes": 0, "errors": 0, "timeouts": 0, "transferred": 0}
	for res in results:
		stats["transferred"] += res["transferred"]
		stats["successes"] += res["status"] == ResultStatus.SUCCESS
		stats["errors"] += res["status"] == ResultStatus.ERROR
		stats["timeouts"] += res["status"] == ResultStatus.PENDING

		summary["transferred"] += res["transferred"]
		summary["successes"] += res["status"] == ResultStatus.SUCCESS
		summary["errors"] += res["status"] == ResultStatus.ERROR
		summary["timeouts"] += res["status"] == ResultStatus.PENDING

	stats['transferred'] = stats['transferred'] / (1024 * 1024)

	return stats


def main():
	urls = prep_urls()
	print("Starting requests...")

	for i in range(iterations):
		print(f"Run: {i + 1}/{iterations}")

		start = time.time()
		results = asyncio.run(spawn_requests(urls))
		duration = time.time() - start

		stats = eval(results)
		stats["time"] = duration
		summary["time"] += duration

		output = (f"{i + 1}: Time: {stats['time']:.2f}s. "
			f"Sent: {stats['successes'] + stats['errors'] + stats['timeouts']}. "
			f"Successes: {stats['successes']}. "
			f"Errors: {stats['errors']}. "
			f"Timeouts: {stats['timeouts']}. "
			f"Transferred: {stats['transferred']:.2f} MB "
			f"({stats['transferred'] / stats['time']:.2f} MB/s).")
		outputs.append(output)

		if verbose:
			print(f"{seperator}\n{output}\n")

	if len(outputs) <= 1 and verbose:
		return

	print(seperator)

	for output in outputs:
		print(output)

	summary['transferred'] = summary['transferred'] / (1024 * 1024)

	print(seperator)
	print(f"Runs: {iterations}. "
		f"Average Time: {summary['time'] / float(len(outputs)):.2f}s. "
		f"Total Errors: {summary['errors']}. "
		f"Total Timeouts: {summary['timeouts']}. "
		f"Transferred: {summary['transferred']:.2f} MB ({summary['transferred']/summary['time']:.2f} MB/s).")
	print(seperator)


main()
