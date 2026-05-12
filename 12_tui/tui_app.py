import sys
from pathlib import Path
from datetime import datetime, timezone

from tui_state import TUIState, write_session_report, VALID_SCREENS
from tui_screens import SCREEN_HANDLERS, SCREEN_RENDERERS
from tui_keymap import KEY_TO_SCREEN, is_valid_key, NAV_KEYS, FORBIDDEN_SCREEN_NAMES
from tui_renderer import SNAPSHOT_FORMATS, SEPARATOR

ROOT = Path(__file__).resolve().parent.parent
_MAX_RAW_INPUT = 1000


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

        print("  [1-9] navigate  [b]back  [d]home  [?]help  [r]refresh  [h]help  [q]quit")
        try:
            raw_line = input("  > ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        raw = raw_line.strip().lower()[:_MAX_RAW_INPUT] if raw_line else ""

        if raw == "q":
            break
        elif raw == "r":
            state.refresh_counter += 1
            state.last_refreshed_at = datetime.now(timezone.utc).isoformat()
            continue
        elif raw == "h":
            state.navigate_to("help")
            continue
        elif raw == "b":
            state.go_back()
            continue
        elif raw == "d":
            state.go_home()
            continue
        elif raw == "?":
            print()
            print("  Screen-specific help for:", state.current_screen)
            print("  See help screen (8) for full keymap.")
            continue
        elif raw == "4":
            state.navigate_to("validator_wall")
            print()
            print(SCREEN_RENDERERS["validator_wall"](state))
            print()
            h = SCREEN_HANDLERS.get("validator_wall")
            if h:
                h(state, "4", lambda prompt="": input(prompt))
            continue
        elif raw == "5":
            state.navigate_to("command_packet_prep")
            print()
            print(SCREEN_RENDERERS["command_packet_prep"](state))
            print()
            h = SCREEN_HANDLERS.get("command_packet_prep")
            if h:
                h(state, "5", lambda prompt="": input(prompt))
            continue
        elif raw == "6":
            state.navigate_to("branch_review_prep")
            print()
            print(SCREEN_RENDERERS["branch_review_prep"](state))
            print()
            h = SCREEN_HANDLERS.get("branch_review_prep")
            if h:
                h(state, "6", lambda prompt="": input(prompt))
            continue
        elif raw == "7":
            state.navigate_to("approval_ledger")
            print()
            print(SCREEN_RENDERERS["approval_ledger"](state))
            print()
            h = SCREEN_HANDLERS.get("approval_ledger")
            if h:
                h(state, "7", lambda prompt="": input(prompt))
            continue
        elif raw in NAV_KEYS:
            new_screen = KEY_TO_SCREEN.get(raw)
            if new_screen and new_screen not in ("quit", "refresh", "help", "back", "dashboard", "screen_help"):
                state.navigate_to(new_screen)
                continue
        elif is_valid_key(raw):
            new_screen = KEY_TO_SCREEN.get(raw)
            if new_screen and new_screen not in ("quit", "refresh", "help", "back", "dashboard", "screen_help"):
                state.navigate_to(new_screen)
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
        prompt = "  [1-9] nav  [b]back  [d]home  [?]help  [r]refresh  [q]quit"
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
            state.last_refreshed_at = datetime.now(timezone.utc).isoformat()
            continue
        elif key == ord("h"):
            state.navigate_to("help")
            continue
        elif key == ord("b"):
            state.go_back()
            continue
        elif key == ord("d"):
            state.go_home()
            continue
        elif key == ord("?"):
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
        elif ord("1") <= key <= ord("3") or key == ord("8") or key == ord("9"):
            raw = chr(key)
            new_screen = KEY_TO_SCREEN.get(raw)
            if new_screen and new_screen not in ("quit", "refresh", "help", "back", "dashboard", "screen_help"):
                state.navigate_to(new_screen)
            continue
        elif chr(key) in KEY_TO_SCREEN:
            new_screen = KEY_TO_SCREEN.get(chr(key))
            if new_screen and new_screen not in ("quit", "refresh", "help", "back", "dashboard", "screen_help", "4", "5", "6", "7"):
                state.navigate_to(new_screen)
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


def run_snapshot(state, fmt="text", save=False, output_dir=None):
    if fmt not in SNAPSHOT_FORMATS:
        print(f"ERROR: Unknown snapshot format: {fmt}")
        print("Supported formats: text, markdown, json, compact, full")
        sys.exit(2)
    render_fn = SNAPSHOT_FORMATS[fmt]
    output = render_fn(state)
    if save:
        if output_dir is None:
            from tui_state import SNAPSHOT_DIR
            output_dir = SNAPSHOT_DIR
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        ext = {"text": "txt", "markdown": "md", "json": "json", "compact": "txt", "full": "txt"}
        ext_map = ext.get(fmt, "txt")
        output_dir.mkdir(parents=True, exist_ok=True)
        snap_path = output_dir / f"snapshot_{ts}.{ext_map}"
        snap_path.write_text(output)
        print(f"Snapshot saved: {snap_path}")
    else:
        print(output)


def run_format_help():
    print("Snapshot format options:")
    print("  --snapshot --format text       Plain text (default)")
    print("  --snapshot --format markdown   Markdown document")
    print("  --snapshot --format json       JSON data")
    print("  --snapshot --format compact    Compact one-line summary")
    print("  --snapshot --format full       Full detailed snapshot")
    print("  --snapshot --format json --save  Save to file")
