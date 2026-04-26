import threading
import requests
import json
import os
import sys

try:
    from tqdm import tqdm

    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print(
        "[!] 'tqdm' module not found. Progress bars will be simplified. (Run 'pip install tqdm' for better visuals)"
    )

URL = "https://janfadaa.ir/ajax"
BROKEN_POINTERS_FILE = "broken_pointers.txt"
OUTPUT_FILE = "broken_comments.jsonl"

USE_PROXY = False
PROXIES = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}

write_lock = threading.Lock()
print_lock = threading.Lock()


def process_pointer(pointer, thread_index):
    session = requests.Session()
    if USE_PROXY:
        session.proxies.update(PROXIES)
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "identity",
        }
    )

    data = {"action": "getComments"}
    if str(pointer) != "0":
        data["pointer"] = str(pointer)

    pbar = None
    if TQDM_AVAILABLE:
        pbar = tqdm(
            total=1000,
            desc=f"Ptr {pointer: <10}",
            position=thread_index,
            leave=False,
            colour="cyan",
        )

    for attempt in range(1, 1001):
        if pbar:
            pbar.update(1)
        elif attempt % 100 == 0:
            with print_lock:
                print(f"[Thread {pointer}] Attempt {attempt}/1000")

        try:
            response = session.post(URL, data=data, timeout=1.0)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    comments = result.get("data", {}).get("all", [])

                    if comments:
                        with write_lock:
                            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                                for comment in comments:
                                    f.write(
                                        json.dumps(comment, ensure_ascii=False) + "\n"
                                    )

                        if pbar:
                            pbar.close()
                        with print_lock:
                            print(
                                f"\n[✓] SUCCESS: Thread [{pointer}] received data on attempt {attempt}. Saved {len(comments)} comments. Terminating thread."
                            )
                    else:
                        if pbar:
                            pbar.close()
                        with print_lock:
                            print(
                                f"\n[✓] SUCCESS: Thread [{pointer}] succeeded on attempt {attempt}, but 0 comments returned. Terminating thread."
                            )

                    return
        except Exception:
            pass

    if pbar:
        pbar.close()
    with print_lock:
        print(
            f"\n[!] FAILED: Thread [{pointer}] completely failed after 1000 attempts."
        )


def main():
    if not os.path.exists(BROKEN_POINTERS_FILE):
        print(f"[!] File not found: {BROKEN_POINTERS_FILE}")
        return

    with open(BROKEN_POINTERS_FILE, "r") as f:
        pointers = list(set([line.strip() for line in f if line.strip()]))

    if not pointers:
        print(f"[!] No pointers found in {BROKEN_POINTERS_FILE}.")
        return

    # Clear screen for tqdm multi-bars
    if TQDM_AVAILABLE:
        print("\033[2J\033[H", end="")

    print("==================================================")
    print("PARALLEL BROKEN POINTERS RETRY SCRIPT")
    print(f"[*] Launching {len(pointers)} parallel threads...")
    print("==================================================")
    print("\n" * len(pointers))  # Create space for the progress bars

    threads = []
    for i, ptr in enumerate(pointers):
        t = threading.Thread(target=process_pointer, args=(ptr, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("\n[*] All threads finished execution.")


if __name__ == "__main__":
    main()
