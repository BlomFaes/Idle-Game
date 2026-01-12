import random
from typing import Any
import time
import threading
import queue
from sympy import isprime, divisors





# -----------------------------------------------------------------------------
# SETTINGS & COLORS
# -----------------------------------------------------------------------------

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"
BOLD = "\033[1m"

MINER_COST = 5000.0

game_state: dict[str, Any] = {
    "running": True,
    "points": 10000.0,
    "points_per_sec": 1.0,
    "mode": "idle",
    "area_mode": "prime",
    "current_puzzle": None,
    "current_difficulty": None,
    "last_update": time.time(),
    "unlocked_areas": ["prime"],
    "area_costs": {"binary": 200.0, "multi": 3000.0},
    "crew": [
            {"name": "Miner 1", "level": 0, "base_pps": 50, "unlock_cost": MINER_COST}
        ]
}

commands = queue.Queue()


# -----------------------------------------------------------------------------
# PUZZLE GENERATORS
# -----------------------------------------------------------------------------

def generate_prime_puzzle(difficulty):
    if difficulty == "easy":
        number = random.randrange(11, 51, 2)
        reward = 0.5
    elif difficulty == "normal":
        number = random.randrange(51, 201, 2)
        reward = 1.0
    elif difficulty == "hard":
        number = random.randrange(201, 1001, 2)
        reward = 2.0
    else:
        number = random.randint(11, 51)
        reward = 0.5

    question = f" Is {number} prime? ({GREEN}yes{RESET}/{RED}no{RESET})"
    answer = "yes" if isprime(number) else "no"
    return question, answer, reward, number


def generate_binary_puzzle(difficulty):
    if difficulty == "easy":
        number = random.randint(2, 10)
        reward = 2.0
    elif difficulty == "normal":
        number = random.randint(11, 30)
        reward = 4.0
    elif difficulty == "hard":
        number = random.randint(31, 100)
        reward = 8.0
    else:
        number = random.randint(2, 10)
        reward = 2.0

    question = f" Convert {number} to binary:"
    answer = bin(number)[2:]
    return question, answer, reward, number


def generate_multi_puzzle(difficulty):
    if difficulty == "easy":
        n1, n2 = random.randint(2, 9), random.randint(2, 9)
    elif difficulty == "normal":
        n1, n2 = random.randint(10, 20), random.randint(2, 9)
    elif difficulty == "hard":
        n1, n2 = random.randint(10, 50), random.randint(10, 20)
    else:
        n1, n2 = 5, 5

    question = f"\n {BOLD}{RED}⚠ EMERGENCY!{RESET} Mining shaft collapsing in {BOLD}10s{RESET}!"
    question += f"\n What is {n1} x {n2}?"
    answer = str(n1 * n2)
    start_time = time.time()
    return question, answer, None, (n1, n2, start_time)


# -----------------------------------------------------------------------------
# CORE LOGIC
# -----------------------------------------------------------------------------

def run():
    while game_state["running"]:
        try:
            command = input("")
            if command.strip():
                commands.put(command.strip())
        except EOFError:
            break


def game_update():
    now = time.time()
    if now - game_state["last_update"] >= 1.0:
        seconds_passed = int(now - game_state["last_update"])

        crew_pps = sum(m["base_pps"] * m["level"] for m in game_state["crew"])
        total_pps = game_state["points_per_sec"] + crew_pps

        game_state["points"] += total_pps * seconds_passed
        game_state["last_update"] += seconds_passed


def render():
    print(f"\n{BOLD}{CYAN}=== MATH MINING RIG ==={RESET}")
    print(f"Balance: {YELLOW}{game_state['points']:.2f}💎{RESET}")

    crew_pps = sum(m["base_pps"] * m["level"] for m in game_state["crew"] if m["level"] > 0)

    print(f"Personal Rate: {GREEN}{game_state['points_per_sec']:.2f}/sec{RESET}")
    print(f"Crew Rate:     {MAGENTA}{crew_pps:.2f}/sec{RESET}")
    print(f"Total Output:  {BOLD}{game_state['points_per_sec'] + crew_pps:.2f}/sec{RESET}\n")

    print(f"{BOLD}Available Shafts:{RESET}")
    print(f"  {GREEN}prime{RESET}  - The Prime Pits")

    if "binary" in game_state["unlocked_areas"]:
        print(f"  {CYAN}binary{RESET} - The Binary Cave")
    else:
        cost = game_state["area_costs"]["binary"]
        print(f"  {RED}🔒 binary{RESET} - Cost: {YELLOW}{cost:.2f}💎{RESET}")

    if "multi" in game_state["unlocked_areas"]:
        print(f"  {MAGENTA}multi{RESET}  - The Multiply Cavern")
    else:
        cost = game_state["area_costs"]["multi"]
        print(f"  {RED}🔒 multi{RESET} - Cost: {YELLOW}{cost:.2f}💎{RESET}")

    print(f"\n{BOLD}Commands:{RESET} crew, status, quit")
    print("-" * 30)

def render_crew_ui():
    print("\n" * 50)
    print(f"{BOLD}{MAGENTA}=== CREW QUARTERS ==={RESET}")
    for i, m in enumerate(game_state["crew"]):
        if m["level"] == 0:
            print(f" {i + 1}. {RED}🔒 {m['name']}{RESET} (LOCKED)")
            print(f"    Unlock Cost: {YELLOW}{m['unlock_cost']:.2f}💎{RESET}")
        else:
            current_prod = m["base_pps"] * m["level"]
            upgrade_cost = 5000.0 * (m["level"] ** 1.5)
            print(
                f" {i + 1}. {BOLD}{m['name']}{RESET} | Lvl: {YELLOW}{m['level']}{RESET} | Prod: {GREEN}+{current_prod:.2f}/sec{RESET}")
            print(f"    Next Level: {YELLOW}{upgrade_cost:.2f}💎{RESET}")
    print(f"\n Type {BOLD}upgrade [number]{RESET} or {BOLD}back{RESET}.")

def process_commands():
    while not commands.empty():
        command = commands.get().lower()
        print("\n" * 50)

        if game_state["mode"] == "puzzle":
            correct_answer = game_state["current_puzzle"][1]
            reward = game_state["current_puzzle"][2]
            number = game_state["current_puzzle"][3]
            difficulty = game_state.get("current_difficulty", "easy")

            if command not in ["yes", "no"] and game_state["area_mode"] == "prime":
                print(f" {YELLOW}⚠ Invalid answer.{RESET} Please type {BOLD}yes{RESET} or {BOLD}no{RESET}.")
            else:
                if command == correct_answer:
                    if game_state["area_mode"] == "multi":
                        start_time = number[2]
                        time_taken = time.time() - start_time

                        if difficulty == "easy":
                            max_bonus = 0.1
                        elif difficulty == "normal":
                            max_bonus = 0.4
                        else:
                            max_bonus = 0.8

                        time_factor = (10 - time_taken) / 10
                        multiplier = 1.0 + (max_bonus * time_factor)

                        old_pps = game_state["points_per_sec"]
                        game_state["points_per_sec"] *= multiplier

                        print(f" {GREEN}✔ FAST WORK!{RESET} ({time_taken:.1f}s)")
                        print(f" {BOLD}{difficulty.upper()} BONUS: {multiplier:.2f}x{RESET}")
                        # New formula display
                        print(
                            f" {CYAN}New rate:{RESET} {old_pps:.2f} * {multiplier:.2f} = {GREEN}{game_state['points_per_sec']:.2f}{RESET} / sec")
                    else:
                        print(f" {GREEN}✔ Correct!{RESET} +{reward:.1f} points/sec")

                else:
                    print(f" {RED}✘ Incorrect.{RESET}")
                    if game_state["area_mode"] == "prime":
                        if correct_answer == "no":
                            d_list = divisors(number)[1:-1]
                            print(f" {CYAN}Tip:{RESET} {number} is not prime. Divisors: {d_list}")
                        else:
                            print(f" {CYAN}Tip:{RESET} {number} {BOLD}is{RESET} a prime number!")
                    elif game_state["area_mode"] == "binary":
                        print(f" {CYAN}Tip:{RESET} The binary for {number} is {BOLD}{correct_answer}{RESET}.")
                    elif game_state["area_mode"] == "multi":
                        print(
                            f" {CYAN}Tip:{RESET} {number[0]}x{number[1]}={correct_answer} \n")

                game_state["current_puzzle"] = None
                game_state["mode"] = "idle"
                time.sleep(2)
                print("\n" * 50)
                render()
            continue

        elif game_state["mode"] == "choose_difficulty":
            if command in ["easy", "normal", "hard"]:
                game_state["current_difficulty"] = command
                area = game_state.get("area_mode", "prime")
                if area == "binary":
                    q, a, r, n = generate_binary_puzzle(command)
                elif area == "multi":
                    q, a, r, n = generate_multi_puzzle(command)
                else:
                    q, a, r, n = generate_prime_puzzle(command)

                game_state["current_puzzle"] = (q, a, r, n)
                game_state["mode"] = "puzzle"
                print("\n" * 50)
                print(q)
            else:
                print(f" {YELLOW}⚠ Invalid choice.{RESET} (easy/normal/hard)")
            continue

        elif game_state["mode"] == "crew_management":
            if command == "back":
                game_state["mode"] = "idle"
                print("\n" * 50)
                render()
            elif command.startswith("upgrade "):
                try:
                    idx = int(command.split()[1]) - 1

                    if idx < 0 or idx >= len(game_state["crew"]):
                        print(f" {RED}✘ ERROR:{RESET} Miner ID {idx + 1} does not exist.")
                        time.sleep(1)
                        render_crew_ui()
                        continue

                    miner = game_state["crew"][idx]

                    if miner["level"] == 0:
                        cost = miner["unlock_cost"]
                        action = "UNLOCK"
                    else:
                        cost = 5000.0 * (miner["level"] ** 1.5)
                        action = "UPGRADE"

                    if game_state["points"] >= cost:
                        game_state["points"] -= cost
                        miner["level"] += 1

                        if action == "UNLOCK":
                            next_id = len(game_state["crew"]) + 1
                            next_miner = {
                                "name": f"Miner {next_id}",
                                "level": 0,
                                "base_pps": 50,
                                "unlock_cost": MINER_COST * next_id
                            }
                            game_state["crew"].append(next_miner)

                        print(f" {GREEN}✔ {action} SUCCESS!{RESET} {miner['name']} is Level {miner['level']}.")
                    else:
                        print(f" {RED}✘ Not enough points!{RESET} Need {YELLOW}{cost:.2f}💎{RESET}.")

                    time.sleep(1)
                    render_crew_ui()
                except (ValueError, IndexError):
                    print(f" {RED}Usage: upgrade [number]{RESET}")
                    time.sleep(1)
                    render_crew_ui()
            else:
                print(f" {RED}Unknown command in Crew Quarters:{RESET} {command}")
                print(f" Type {BOLD}upgrade [number]{RESET} or {BOLD}back{RESET}.")
                time.sleep(1)
                render_crew_ui()
            continue
        # ---------------------------------------------------------------------
        # MODE: IDLE (Main Commands)
        # ---------------------------------------------------------------------
        elif game_state["mode"] == "idle":
            if command == "crew":
                game_state["mode"] = "crew_management"
                render_crew_ui()
            elif command == "prime":
                game_state["area_mode"], game_state["mode"] = "prime", "choose_difficulty"
                print(f" Entering {GREEN}Prime Pits{RESET}...")
                print(f" Choose a difficulty: ({GREEN}easy{RESET}/{YELLOW}normal{RESET}/{RED}hard{RESET})")

            elif command == "binary":
                cost = game_state["area_costs"]["binary"]
                if "binary" in game_state["unlocked_areas"]:
                    game_state["area_mode"], game_state["mode"] = "binary", "choose_difficulty"
                    print(f" Entering {CYAN}Binary Cave{RESET}...")
                    print(f" Choose a difficulty: ({GREEN}easy{RESET}/{YELLOW}normal{RESET}/{RED}hard{RESET})")
                elif game_state["points"] >= cost:
                    game_state["points"] -= cost
                    game_state["unlocked_areas"].append("binary")

                    print("\n" * 2)
                    print(f" {BOLD}{GREEN}★ CONGRATULATIONS! ★{RESET}")
                    print(f" {BOLD}The {CYAN}Binary Cave{RESET}{BOLD} has been blast-opened!{RESET}")
                    print(f" New binary data streams are now available for mining.")
                    time.sleep(2)
                    render()
                else:
                    print(f" {RED}✘ LOCKED!{RESET} Need {YELLOW}{cost - game_state['points']:.2f}💎{RESET} more")
                    time.sleep(1)
                    render()

            elif command == "multi":
                cost = game_state["area_costs"]["multi"]
                if "multi" in game_state["unlocked_areas"]:
                    game_state["area_mode"], game_state["mode"] = "multi", "choose_difficulty"
                    print(f" Entering {MAGENTA}Multiply Cavern{RESET}...")
                    print(f" Choose a difficulty: ({GREEN}easy{RESET}/{YELLOW}normal{RESET}/{RED}hard{RESET})")
                elif game_state["points"] >= cost:
                    game_state["points"] -= cost
                    game_state["unlocked_areas"].append("multi")

                    print("\n" * 2)
                    print(f" {BOLD}{GREEN}★ CONGRATULATIONS! ★{RESET}")
                    print(f" {BOLD}The {MAGENTA}Multiply Cavern{RESET}{BOLD} has been blast-opened!{RESET}")
                    print(f" New high-speed multipliers are now available for mining.")
                    time.sleep(2)
                    render()
                else:
                    print(f" {RED}✘ LOCKED!{RESET} Need {YELLOW}{cost - game_state['points']:.2f}💎{RESET} more")
                    time.sleep(1)
                    render()
            elif command == "status":
                render()
            elif command == "quit":
                game_state["running"] = False
            else:
                print(f" {RED}Unknown command:{RESET}", command)
                render()


def game_loop():
    while game_state["running"]:
        game_update()
        process_commands()
        if game_state["mode"] == "puzzle" and game_state.get("area_mode") == "multi":
            start_time = game_state["current_puzzle"][3][2]
            if time.time() - start_time > 10.0:
                print("\n" * 100)
                print(f" {BOLD}{RED}💥 BOOM! SHAFT EXPLODED!{RESET}")
                game_state["mode"] = "idle"
                time.sleep(2)
                render()
        time.sleep(0.05)


# -----------------------------------------------------------------------------
# EXECUTION
# -----------------------------------------------------------------------------

print("\n" * 50)
render()

t = threading.Thread(target=run)
t.start()

game_loop()

print("Game Over! (Press Enter to exit)")