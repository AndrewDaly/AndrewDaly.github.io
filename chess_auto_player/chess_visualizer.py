import tkinter as tk
from tkinter import ttk
import threading
import time
import chess
from stockfish import Stockfish
# use C:\Dev\virtual_envs\venv\Scripts\python.exe
# ---------------- CONFIG ---------------- #
STOCKFISH_PATH = r"C:\Dev\cursor_ai\AndrewDaly.github.io\python_projects_audio\stockfish-windows-x86-64-avx2.exe"
ENGINE_DELAY = 0.1  # seconds between moves

# ---------------- SAFE STOCKFISH ---------------- #

class SafeStockfish(Stockfish):
    def __del__(self):
        try:
            if hasattr(self, "_stockfish") and self._stockfish:
                if self._stockfish.poll() is None:
                    self._stockfish.terminate()
        except:
            pass

# ---------------- ENGINE CONTROLLER ---------------- #

class EngineController:
    def __init__(self, board, ui):
        self.board = board
        self.ui = ui
        self.running = False
        self.thread = None

        self.white = SafeStockfish(path=STOCKFISH_PATH)
        self.black = SafeStockfish(path=STOCKFISH_PATH)

        # aggressive settings
        for eng in (self.white, self.black):
            eng.update_engine_parameters({"Contempt": 30})
            eng.set_skill_level(20)

    def set_elos(self, elo_white, elo_black):
        self.white.set_elo_rating(elo_white)
        self.black.set_elo_rating(elo_black)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.loop, daemon=True)
            self.thread.start()

    def pause(self):
        self.running = False

    def reset(self):
        self.running = False
        self.board.reset()
        self.ui.update_all()

    def loop(self):
        while self.running and not self.board.is_game_over():
            engine = self.white if self.board.turn else self.black
            engine.set_fen_position(self.board.fen())

            move = None
            start_time = time.time()
            THINK_TIME = 1  # seconds to calculate

            # Poll Stockfish repeatedly to update eval bar dynamically
            while time.time() - start_time < THINK_TIME:
                # Get current evaluation
                info = engine.get_evaluation()
                self.ui.draw_eval_bar(info)  # pass info to draw_eval_bar
                time.sleep(0.1)  # small delay so UI updates smoothly

            # Get the best move after thinking
            move = engine.get_best_move()
            if move:
                self.board.push_uci(move)
                self.ui.update_all()  # final update after move
            time.sleep(ENGINE_DELAY)



# ---------------- UI ---------------- #

class ChessUI:
    def __init__(self, root):
        self.root = root
        self.board = chess.Board()

        main = tk.Frame(root)
        main.pack(padx=10, pady=10)

        # BOARD CANVAS
        self.canvas = tk.Canvas(main, width=480, height=480)
        self.canvas.grid(row=0, column=0)

        # MOVE LIST
        self.moves = tk.Text(main, width=30, height=30)
        self.moves.grid(row=0, column=1, padx=10)

        # EVAL BAR
        self.eval_bar = tk.Canvas(main, width=40, height=480, bg="white")
        self.eval_bar.grid(row=0, column=2)

        # BUTTONS + ELO INPUT
        control = tk.Frame(main)
        control.grid(row=1, column=0, columnspan=3, pady=10)

        tk.Label(control, text="White ELO:").grid(row=0, column=0)
        tk.Label(control, text="Black ELO:").grid(row=0, column=2)

        self.elo_white_var = tk.IntVar(value=2500)
        self.elo_black_var = tk.IntVar(value=2500)

        tk.Entry(control, textvariable=self.elo_white_var, width=6).grid(row=0, column=1)
        tk.Entry(control, textvariable=self.elo_black_var, width=6).grid(row=0, column=3)

        tk.Button(control, text="Start", command=self.on_start).grid(row=0, column=4, padx=10)
        tk.Button(control, text="Pause", command=self.on_pause).grid(row=0, column=5)
        tk.Button(control, text="Reset", command=self.on_reset).grid(row=0, column=6)

        self.controller = EngineController(self.board, self)
        self.draw_board()
        self.update_all()

    # --- Button Callbacks --- #
    def on_start(self):
        self.controller.set_elos(self.elo_white_var.get(), self.elo_black_var.get())
        self.controller.start()

    def on_pause(self):
        self.controller.pause()

    def on_reset(self):
        self.controller.reset()

    # --- UI updates --- #
    def update_all(self):
        self.draw_board()
        self.update_moves()
        self.draw_eval_bar()

    def draw_board(self):
        size = 60
        self.canvas.delete("all")

        # Unicode chess pieces
        unicode_pieces = {
            'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
            'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚',
        }

        for r in range(8):
            for c in range(8):
                x1, y1 = c * size, r * size
                color = "#EEE" if (r + c) % 2 else "#777"
                self.canvas.create_rectangle(x1, y1, x1 + size, y1 + size, fill=color)

        for square, piece in self.board.piece_map().items():
            r = 7 - (square // 8)
            c = square % 8
            x = c * size + size // 2
            y = r * size + size // 2
            self.canvas.create_text(
                x, y, 
                text=unicode_pieces[piece.symbol()],
                font=("Arial", 32)
            )

    def update_moves(self):
        self.moves.delete("1.0", tk.END)
        move_stack = self.board.move_stack
        move_text = ""
        temp_board = chess.Board()  # start from initial position

        for i, move in enumerate(move_stack):
            if i % 2 == 0:
                move_number = i // 2 + 1
                move_text += f"{move_number}. "

            san_move = temp_board.san(move)  # legal move on temp_board
            move_text += f"{san_move} "

            temp_board.push(move)

            if i % 2 == 1:
                move_text += "\n"

        self.moves.insert(tk.END, move_text)

    def draw_eval_bar(self, info=None):
        self.eval_bar.delete("all")  # clear previous

        if info is None:
            eng = self.controller.white
            eng.set_fen_position(self.board.fen())
            info = eng.get_evaluation()

        # Determine score
        if "type" in info:
            if info["type"] == "cp":
                score = info["value"]
                score_text = f"{score-39}"
            elif info["type"] == "mate":
                score = 1000 * (1 if info["value"] > 0 else -1)
                score_text = f"Mate {info['value']}"
            else:
                score = 0
                score_text = "0"
        else:
            score = 0
            score_text = "0"

        # Clamp score for visual bar
        score = max(-500, min(500, score))
        pct = (score + 500) / 1000  # 0..1

        h = 480
        fill_h = max(5, pct * h)
        self.eval_bar.create_rectangle(0, h - fill_h, 40, h, fill="black")

        # Draw the numeric score in the middle of the bar
        self.eval_bar.create_text(
            20, h/8, text=score_text, font=("Arial", 12), fill="red"
        )

# ---------------- MAIN ---------------- #

root = tk.Tk()
root.title("Stockfish vs Stockfish")
ChessUI(root)
root.mainloop()
