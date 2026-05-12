import sys
import shutil
from pathlib import Path

from tui_state import TUIState, write_session_report
from tui_screens import SCREEN_HANDLERS, SCREEN_RENDERERS
from tui_keymap import KEY_TO_SCREEN, is_valid_key, HELP_TEXT
from tui_renderer import render_snapshot, SEPARATOR

ROOT = Path(__file__).resolve().parent.parent


def run_plain_text(state):
    while True:
        screen = state.current_screen
        renderer = SCREEN_RENDERERS.get(screen)
        if renderer:
            print(renderer(state))
            print()

        handler = SCREEN_HANDLERS.get(screen)
        if not handler:
            break

        print("  [1-8] navigate  [r] refresh  [h] help  [q] quit")
        try:
            raw = input("  > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if raw == "q":
            break
        elif raw == "r":
            state.refresh_counter += 1
            continue
        elif raw == "h":
            state.current_screen = "help"
            state.record_screen("help")
            continue
        elif is_valid_key(raw):
            new_screen = KEY_TO_SCREEN.get(raw)
            if new_screen and new_screen not in ("quit", "refresh", "help"):
                state.current_screen = new_screen
                state.record_screen(new_screen)
                continue
        elif raw == "4":
            handler(state, "4", lambda prompt="": input(prompt))
            continue
        elif raw == "5":
            handler(state, "5", lambda prompt="": input(prompt))
            continue
        elif raw == "6":
            handler(state, "6", lambda prompt="": input(prompt))
            continue
        elif raw == "7":
            handler(state, "7", lambda prompt="": input(prompt))
            continue
        else:
            print(f"  Unknown key: {raw}")
            continue

    write_session_report(state)
    print()
    print("  Session report written.")
    print("  Boundary secure. Exiting.")
    print(SEPARATOR)


def _curses_main(stdscr):
    from tui_state import TUIState, write_session_report
    from tui_screens import SCREEN_HANDLERS, SCREEN_RENDERERS

    curses = __import__("curses")
    curses.curs_set(0)
    stdscr.keypad(True)
    stdscr.nodelay(False)

    state = TUIState()

    def getch_input(prompt=""):
        if prompt:
            status_line = f"  {prompt}"
            max_y, max_x = stdscr.getmaxyx()
            if len(status_line) > max_x:
                status_line = status_line[:max_x]
            try:
                stdscr.addstr(max_y - 1, 0, status_line)
            except curses.error:
                pass
            stdscr.refresh()
        return stdscr.getch()

    while True:
        stdscr.clear()
        screen = state.current_screen
        renderer = SCREEN_RENDERERS.get(screen)
        if renderer:
            rendered = renderer(state)
            for i, line in enumerate(rendered.splitlines()):
                max_y, max_x = stdscr.getmaxyx()
                if i >= max_y - 1:
                    break
                display = line[:max_x - 1] if len(line) > max_x - 1 else line
                try:
                    stdscr.addstr(i, 0, display)
                except curses.error:
                    pass

        max_y, max_x = stdscr.getmaxyx()
        prompt = "  [1-8] navigate  [r] refresh  [h] help  [q] quit"
        try:
            stdscr.addstr(max_y - 1, 0, prompt[:max_x - 1])
        except curses.error:
            pass
        stdscr.refresh()

        key = stdscr.getch()

        if key == ord("q"):
            break
        elif key == ord("r"):
            state.refresh_counter += 1
            continue
        elif key == ord("h"):
            state.current_screen = "help"
            state.record_screen("help")
            continue
        elif key == ord("4"):
            handler = SCREEN_HANDLERS.get("validator_wall")
            if handler:
                stdscr.clear()
                stdscr.addstr(0, 0, SCREEN_RENDERERS["validator_wall"](state)[:max_y * max_x])
                stdscr.refresh()
                handler(state, "4", lambda prompt="": _curses_get_input(stdscr, prompt))
            continue
        elif key == ord("5"):
            handler = SCREEN_HANDLERS.get("command_packet_prep")
            if handler:
                stdscr.clear()
                stdscr.addstr(0, 0, SCREEN_RENDERERS["command_packet_prep"](state)[:max_y * max_x])
                stdscr.refresh()
                handler(state, "5", lambda prompt="": _curses_get_input(stdscr, prompt))
            continue
        elif key == ord("6"):
            handler = SCREEN_HANDLERS.get("branch_review_prep")
            if handler:
                stdscr.clear()
                stdscr.addstr(0, 0, SCREEN_RENDERERS["branch_review_prep"](state)[:max_y * max_x])
                stdscr.refresh()
                handler(state, "6", lambda prompt="": _curses_get_input(stdscr, prompt))
            continue
        elif key == ord("7"):
            handler = SCREEN_HANDLERS.get("approval_ledger")
            if handler:
                stdscr.clear()
                stdscr.addstr(0, 0, SCREEN_RENDERERS["approval_ledger"](state)[:max_y * max_x])
                stdscr.refresh()
                handler(state, "7", lambda prompt="": _curses_get_input(stdscr, prompt))
            continue
        elif ord("1") <= key <= ord("3") or key == ord("8"):
            raw = chr(key)
            new_screen = KEY_TO_SCREEN.get(raw)
            if new_screen and new_screen not in ("quit", "refresh", "help"):
                state.current_screen = new_screen
                state.record_screen(new_screen)
            continue
        elif chr(key) in KEY_TO_SCREEN:
            new_screen = KEY_TO_SCREEN.get(chr(key))
            if new_screen and new_screen not in ("quit", "refresh", "help", "4", "5", "6", "7"):
                state.current_screen = new_screen
                state.record_screen(new_screen)
            continue

    write_session_report(state)
    stdscr.clear()
    msg = "  Session report written. Boundary secure. Exiting."
    try:
        stdscr.addstr(0, 0, msg)
    except curses.error:
        pass
    stdscr.refresh()
    curses.napms(1500)


def _curses_get_input(stdscr, prompt=""):
    curses = __import__("curses")
    max_y, max_x = stdscr.getmaxyx()
    curses.curs_set(1)
    display_prompt = f"  {prompt}" if prompt else "  > "
    try:
        stdscr.addstr(max_y - 1, 0, display_prompt[:max_x - 1])
    except curses.error:
        pass
    stdscr.refresh()
    result = []
    while True:
        ch = stdscr.getch()
        if ch == 10 or ch == 13:
            break
        elif ch == 27:
            result = []
            break
        elif ch in (curses.KEY_BACKSPACE, 127, 8):
            if result:
                result.pop()
                try:
                    stdscr.addstr(max_y - 1, len(display_prompt) + len(result), " ")
                except curses.error:
                    pass
        elif 32 <= ch <= 126:
            result.append(chr(ch))
            try:
                stdscr.addstr(max_y - 1, len(display_prompt) + len(result) - 1, chr(ch))
            except curses.error:
                pass
        stdscr.refresh()
    curses.curs_set(0)
    return "".join(result)


def run_curses():
    curses = __import__("curses")
    curses.wrapper(_curses_main)


def run_snapshot(state):
    print(render_snapshot(state))
