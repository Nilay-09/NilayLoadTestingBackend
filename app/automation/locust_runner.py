import gevent
from locust.env import Environment
from locust.runners import LocalRunner
from locust.stats import stats_printer
from .locustfile import SingleRunSeleniumUser, user_results

def run_locust_test(user_count: int, spawn_rate: int, run_time: int):
    # Clear global results before running
    user_results.clear()
    print("[Runner] Starting test with", user_count, "users.")
    env = Environment(user_classes=[SingleRunSeleniumUser])
    runner = env.create_local_runner()

    gevent.spawn(stats_printer, env.stats)
    
    runner.start(user_count, spawn_rate=spawn_rate)
    gevent.sleep(run_time)
    runner.quit()
    runner.greenlet.join()

    stats_total = env.runner.stats.total
    summary = {
        "users_completed": len(user_results),
        "total_requests": stats_total.num_requests,
        "total_failures": stats_total.num_failures,
        "average_response_time_ms": stats_total.avg_response_time,
        "min_response_time_ms": stats_total.min_response_time,
        "max_response_time_ms": stats_total.max_response_time,
    }
    print("[Runner] Summary:", summary)
    print("[Runner] User results:", user_results)
    return {"summary": summary, "user_results": user_results}

if __name__ == "__main__":
    res = run_locust_test(user_count=2, spawn_rate=1, run_time=90)
    print("Test Completed. Results:")
    print(res)
