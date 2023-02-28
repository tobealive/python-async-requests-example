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

Stats = TypedDict("Stats", time=float, successes=int, errors=int, timeouts=int, transferred=float)
ResultStatus = Enum('ResultStatus', 'SUCCESS ERROR PENDING')


class TestItem:

	def __init__(self, url: str, status: ResultStatus, transferred: int, time: float):
		self.url = url
		self.status = status
		self.transferred = transferred
		self.time = time

	def __str__(self):
		return f"{self.url}, {self.status}, {self.transferred}, {self.time}"


summary: Stats = {"time": 0, "successes": 0, "errors": 0, "timeouts": 0, "transferred": 0}
outputs: list[str] = []


def prep_urls() -> list[str]:
	if single_source:
		urls = [(f"google.com/search?q={i}") for i in range(100)]
		return urls

	urls = requests.get(url_source).text.split('\n')
	urls = list(dict.fromkeys(urls))[:100]  # remove duplicats, limit to 100 urls
	return urls


async def get_http_resp(session: ClientSession, test_item: TestItem) -> TestItem:
	start_time = time.time()

	try:
		async with session.get(f"http://www.{test_item.url}") as resp:
			response = await resp.read()
			res_len = len(response)
			test_item.status = ResultStatus.SUCCESS
			test_item.transferred = res_len
			test_item.time = time.time() - start_time
			if verbose:
				print(f"{test_item.url} - Transferred: {res_len} Bytes. Time: {test_item.time:.4f}s.")
	except Exception as e:
		global errorNum
		test_item.time = time.time() - start_time
		test_item.status = ResultStatus.ERROR
		if verbose:
			print(f"Error: {test_item.url} - {e.__class__}")

	return test_item


async def spawn_requests(test_items: list[TestItem]) -> list[TestItem]:
	async with ClientSession() as session:
		tasks = [get_http_resp(session, test_item) for test_item in test_items]
		try:
			await asyncio.wait_for(asyncio.gather(*tasks), timeout=5)
		except asyncio.TimeoutError:
			await asyncio.gather(*tasks, return_exceptions=True)

	return test_items


def eval(results: list[TestItem]) -> Stats:
	stats: Stats = {"time": 0.0, "successes": 0, "errors": 0, "timeouts": 0, "transferred": 0}
	for res in results:
		stats["transferred"] += res.transferred
		stats["successes"] += res.status == ResultStatus.SUCCESS
		stats["errors"] += res.status == ResultStatus.ERROR
		stats["timeouts"] += res.status == ResultStatus.PENDING

		summary["transferred"] += res.transferred
		summary["successes"] += res.status == ResultStatus.SUCCESS
		summary["errors"] += res.status == ResultStatus.ERROR
		summary["timeouts"] += res.status == ResultStatus.PENDING

	stats['transferred'] = stats['transferred'] / (1024 * 1024)

	return stats


def main():
	urls = prep_urls()
	# prepare test items
	test_items = [TestItem(url=url, status=ResultStatus.PENDING, transferred=0, time=0.0) for url in urls]

	print("Starting requests...")

	for i in range(iterations):
		print(f"Run: {i + 1}/{iterations}")

		start = time.time()
		results = asyncio.run(spawn_requests(test_items))
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
