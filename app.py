"""
2048 Game — Streamlit web app
--------------------------------
Run locally with:
    streamlit run app.py

Deploy live at streamlit.io (see instructions given alongside this file).
"""

import random
import pandas as pd
import streamlit as st

st.set_page_config(page_title="2048", page_icon="🎮", layout="centered")

SIZE = 4
TILE_COLORS = {
    0: "#cdc1b4", 2: "#eee4da", 4: "#ede0c8", 8: "#f2b179",
    16: "#f59563", 32: "#f67c5f", 64: "#f65e3b", 128: "#edcf72",
    256: "#edcc61", 512: "#edc850", 1024: "#edc53f", 2048: "#edc22e",
    4096: "#3c3a32", 8192: "#3c3a32",
}
TEXT_COLORS = {0: "#cdc1b4", 2: "#776e65", 4: "#776e65"}


def new_board():
    return [[0] * SIZE for _ in range(SIZE)]


def add_tile(board):
    empty = [(r, c) for r in range(SIZE) for c in range(SIZE) if board[r][c] == 0]
    if empty:
        r, c = random.choice(empty)
        board[r][c] = 4 if random.random() < 0.1 else 2


def compress_merge(line):
    gained = 0
    new_line = [v for v in line if v != 0]
    i = 0
    while i < len(new_line) - 1:
        if new_line[i] == new_line[i + 1]:
            new_line[i] *= 2
            gained += new_line[i]
            del new_line[i + 1]
        i += 1
    new_line += [0] * (SIZE - len(new_line))
    return new_line, gained


def slide(board, direction):
    original = [row[:] for row in board]
    total_gained = 0

    if direction == "left":
        for r in range(SIZE):
            board[r], g = compress_merge(board[r])
            total_gained += g
    elif direction == "right":
        for r in range(SIZE):
            rev = board[r][::-1]
            new_row, g = compress_merge(rev)
            board[r] = new_row[::-1]
            total_gained += g
    elif direction == "up":
        for c in range(SIZE):
            col = [board[r][c] for r in range(SIZE)]
            new_col, g = compress_merge(col)
            for r in range(SIZE):
                board[r][c] = new_col[r]
            total_gained += g
    elif direction == "down":
        for c in range(SIZE):
            col = [board[r][c] for r in range(SIZE)][::-1]
            new_col, g = compress_merge(col)
            new_col = new_col[::-1]
            for r in range(SIZE):
                board[r][c] = new_col[r]
            total_gained += g

    moved = original != board
    return moved, total_gained


def can_move(board):
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == 0:
                return True
            if c < SIZE - 1 and board[r][c] == board[r][c + 1]:
                return True
            if r < SIZE - 1 and board[r][c] == board[r + 1][c]:
                return True
    return False


def check_win(board):
    return any(val == 2048 for row in board for val in row)


def board_to_html(board):
    df = pd.DataFrame(board)

    def cell_style(val):
        bg = TILE_COLORS.get(val, "#3c3a32")
        color = TEXT_COLORS.get(val, "#f9f6f2")
        return (
            f"background-color:{bg}; color:{color}; font-weight:800; "
            f"font-size:26px; text-align:center; vertical-align:middle; "
            f"height:68px; width:68px; border-radius:6px; "
            f"border:6px solid #bbada0; font-family:'Trebuchet MS',sans-serif;"
        )

    try:
        display_df = df.map(lambda v: "" if v == 0 else v)
    except AttributeError:
        display_df = df.applymap(lambda v: "" if v == 0 else v)

    try:
        styler = display_df.style.map(lambda v: cell_style(int(v) if v != "" else 0))
    except AttributeError:
        styler = display_df.style.applymap(lambda v: cell_style(int(v) if v != "" else 0))
    styler = styler.set_table_attributes(
        "style='border-collapse:separate;border-spacing:6px;background:#bbada0;"
        "padding:10px;border-radius:10px;margin:auto;'"
    )
    try:
        styler = styler.hide(axis="index").hide(axis="columns")
    except Exception:
        try:
            styler = styler.hide_index()
            styler = styler.hide_columns()
        except Exception:
            pass
    try:
        return styler.to_html()
    except Exception:
        return styler.render()


# ---------------- session state ----------------
if "board" not in st.session_state:
    st.session_state.board = new_board()
    st.session_state.score = 0
    st.session_state.max_score = 0
    st.session_state.started = False
    st.session_state.game_over = False
    st.session_state.won = False


def start_game():
    st.session_state.board = new_board()
    add_tile(st.session_state.board)
    add_tile(st.session_state.board)
    st.session_state.score = 0
    st.session_state.started = True
    st.session_state.game_over = False
    st.session_state.won = False


def do_move(direction):
    if st.session_state.game_over or not st.session_state.started:
        return
    moved, gained = slide(st.session_state.board, direction)
    if moved:
        st.session_state.score += gained
        st.session_state.max_score = max(st.session_state.max_score, st.session_state.score)
        add_tile(st.session_state.board)
        if check_win(st.session_state.board):
            st.session_state.won = True
        if not can_move(st.session_state.board):
            st.session_state.game_over = True


# ---------------- UI ----------------
st.markdown(
    "<h1 style='text-align:center;color:#776e65;font-family:\"Trebuchet MS\",sans-serif;'>2048</h1>",
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)
col1.metric("Score", st.session_state.score)
col2.metric("Max Score", st.session_state.max_score)

top_l, top_r = st.columns(2)
if not st.session_state.started:
    if top_l.button("▶ Play", use_container_width=True):
        start_game()
        st.rerun()
else:
    if top_r.button("⟲ Restart", use_container_width=True):
        start_game()
        st.rerun()

if st.session_state.started:
    st.markdown(board_to_html(st.session_state.board), unsafe_allow_html=True)

    if st.session_state.won:
        st.success("🎉 You reached 2048! Keep playing or restart.")
    if st.session_state.game_over:
        st.error(f"💀 Game Over! Final Score: {st.session_state.score} | Max Score: {st.session_state.max_score}")

    st.write("")
    _, up_col, _ = st.columns([1, 1, 1])
    if up_col.button("⬆️", use_container_width=True):
        do_move("up")
        st.rerun()

    left_col, down_col, right_col = st.columns([1, 1, 1])
    if left_col.button("⬅️", use_container_width=True):
        do_move("left")
        st.rerun()
    if down_col.button("⬇️", use_container_width=True):
        do_move("down")
        st.rerun()
    if right_col.button("➡️", use_container_width=True):
        do_move("right")
        st.rerun()
else:
    st.info("Press **Play** to start the game!")
