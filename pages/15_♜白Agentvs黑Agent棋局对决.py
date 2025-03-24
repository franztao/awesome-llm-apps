import chess
import chess.svg
import streamlit as st
from autogen import ConversableAgent, register_function

if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = None
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "made_move" not in st.session_state:
    st.session_state.made_move = False
if "board_svg" not in st.session_state:
    st.session_state.board_svg = None
if "move_history" not in st.session_state:
    st.session_state.move_history = []
if "max_turns" not in st.session_state:
    st.session_state.max_turns = 5

st.sidebar.title("API配置")
# Get LLM API Key from user
openai_api_key = st.sidebar.text_input("LLM API Key", type="password", value=st.session_state.get('openai_api_key'))
openai_api_model_type = st.sidebar.text_input("LLM API Model Type",
                                      value=st.session_state.get('openai_api_model_type'))
openai_api_base_url = st.sidebar.text_input("LLM API Base URL", value=st.session_state.get('openai_api_base_url'))
if openai_api_key:
    st.session_state.openai_api_key = openai_api_key
    st.sidebar.success("API key saved!")

st.sidebar.info("""
对于一场的完整国际象棋游戏，大约需要 max_turns > 200。但是，这将消耗大量 API 积分和大量时间。出于演示目的，建议使用 5-10 个回合。
""")

max_turns_input = st.sidebar.number_input(
    "输入圈数（max_turns）：",
    min_value=1,
    max_value=1000,
    value=st.session_state.max_turns,
    step=1
)

if max_turns_input:
    st.session_state.max_turns = max_turns_input
    st.sidebar.success(f"总棋步的最大回合数设置为 {st.session_state.max_turns}!")

st.title("♜ 白Agent vs 黑Agent：棋局对决")
st.markdown("""
一个先进的国际象棋游戏系统，其中两个 AI Agent使用 Streamlit 应用中的 Autogen 相互下棋。它具有强大的移动验证和游戏状态管理功能。
## 特征
### 多Agent架构
- 玩家白：LLM支持的战略决策者
- 玩家黑：由LLM提供支持的战术对手
- 棋盘Agent：移动合法性和游戏状态的验证Agent
### 安全与验证
- 强大的动作验证系统
- 预防非法搬家
- 实时板状态监控
- 安全的游戏进程控制
### 策略游戏
- 人工智能职位评估
- 深入的战术分析
- 动态策略调整
- 完整的国际象棋规则集实现
""")
def available_moves() -> str:
    available_moves = [str(move) for move in st.session_state.board.legal_moves]
    return "Available moves are: " + ",".join(available_moves)

def execute_move(move: str) -> str:
    try:
        chess_move = chess.Move.from_uci(move)
        if chess_move not in st.session_state.board.legal_moves:
            return f"Invalid move: {move}. Please call available_moves() to see valid moves."
        
        # Update board state
        st.session_state.board.push(chess_move)
        st.session_state.made_move = True

        # Generate and store board visualization
        board_svg = chess.svg.board(st.session_state.board,
                                  arrows=[(chess_move.from_square, chess_move.to_square)],
                                  fill={chess_move.from_square: "gray"},
                                  size=400)
        st.session_state.board_svg = board_svg
        st.session_state.move_history.append(board_svg)

        # Get piece information
        moved_piece = st.session_state.board.piece_at(chess_move.to_square)
        piece_unicode = moved_piece.unicode_symbol()
        piece_type_name = chess.piece_name(moved_piece.piece_type)
        piece_name = piece_type_name.capitalize() if piece_unicode.isupper() else piece_type_name
        
        # Generate move description
        from_square = chess.SQUARE_NAMES[chess_move.from_square]
        to_square = chess.SQUARE_NAMES[chess_move.to_square]
        move_desc = f"Moved {piece_name} ({piece_unicode}) from {from_square} to {to_square}."
        if st.session_state.board.is_checkmate():
            winner = 'White' if st.session_state.board.turn == chess.BLACK else 'Black'
            move_desc += f"\nCheckmate! {winner} wins!"
        elif st.session_state.board.is_stalemate():
            move_desc += "\nGame ended in stalemate!"
        elif st.session_state.board.is_insufficient_material():
            move_desc += "\nGame ended - insufficient material to checkmate!"
        elif st.session_state.board.is_check():
            move_desc += "\nCheck!"

        return move_desc
    except ValueError:
        return f"Invalid move format: {move}. Please use UCI format (e.g., 'e2e4')."

def check_made_move(msg):
    if st.session_state.made_move:
        st.session_state.made_move = False
        return True
    else:
        return False
# model = "qwen-plus"
# base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
# api_key = "sk-f7f3039f52e3402bbafda926f4da7cb3"
if st.session_state.openai_api_key:
    try:
        agent_white_config_list = [
            {
                "model": openai_api_model_type,
                "api_key": st.session_state.openai_api_key,
                "base_url":openai_api_base_url,
            },
        ]

        agent_black_config_list = [
            {
                "model": openai_api_model_type,
                "api_key": st.session_state.openai_api_key,
                "base_url":openai_api_base_url,
            },
        ]

        agent_white = ConversableAgent(
            name="Agent_White",  
            system_message="You are a professional chess player and you play as white. "
            "First call available_moves() first, to get list of legal available moves. "
            "Then call execute_move(move) to make a move.",
            llm_config={"config_list": agent_white_config_list, "cache_seed": None},
        )

        agent_black = ConversableAgent(
            name="Agent_Black",  
            system_message="You are a professional chess player and you play as black. "
            "First call available_moves() first, to get list of legal available moves. "
            "Then call execute_move(move) to make a move.",
            llm_config={"config_list": agent_black_config_list, "cache_seed": None},
        )

        game_master = ConversableAgent(
            name="Game_Master",  
            llm_config=False,
            is_termination_msg=check_made_move,
            default_auto_reply="Please make a move.",
            human_input_mode="NEVER",
        )

        register_function(
            execute_move,
            caller=agent_white,
            executor=game_master,
            name="execute_move",
            description="Call this tool to make a move.",
        )

        register_function(
            available_moves,
            caller=agent_white,
            executor=game_master,
            name="available_moves",
            description="Get legal moves.",
        )

        register_function(
            execute_move,
            caller=agent_black,
            executor=game_master,
            name="execute_move",
            description="Call this tool to make a move.",
        )

        register_function(
            available_moves,
            caller=agent_black,
            executor=game_master,
            name="available_moves",
            description="Get legal moves.",
        )

        agent_white.register_nested_chats(
            trigger=agent_black,
            chat_queue=[
                {
                    "sender": game_master,
                    "recipient": agent_white,
                    "summary_method": "last_msg",
                }
            ],
        )

        agent_black.register_nested_chats(
            trigger=agent_white,
            chat_queue=[
                {
                    "sender": game_master,
                    "recipient": agent_black,
                    "summary_method": "last_msg",
                }
            ],
        )

        st.info("""
此国际象棋游戏由两个 AG2 AI 代理进行：
- 白agent：一名拥有 LLM 的国际象棋选手，控制白棋
- 黑agent：一名拥有 LLM 的国际象棋选手，控制黑棋

游戏由游戏管理员管理，游戏管理员负责：
- 验证所有走法
- 更新棋盘
- 管理玩家之间的轮换
- 提供合法走法信息
""")

        initial_board_svg = chess.svg.board(st.session_state.board, size=300)
        st.subheader("初始棋盘")
        st.image(initial_board_svg)

        if st.button("开始游戏"):
            st.session_state.board.reset()
            st.session_state.made_move = False
            st.session_state.move_history = []
            st.session_state.board_svg = chess.svg.board(st.session_state.board, size=300)
            st.info("AI Agent现在将相互对战。每个代理将分析棋盘，向游戏管理员（代理）请求合法移动，并做出战略决策。")
            st.success("您可以在终端输出中查看代理之间的交互，代理之间的轮流结束后，您可以看到下面显示的所有棋盘走法！")
            st.write("游戏开始了！轮到白棋了")

            chat_result = agent_black.initiate_chat(
                recipient=agent_white, 
                message="Let's play chess! You go first, its your move.",
                max_turns=st.session_state.max_turns,
                summary_method="reflection_with_llm"
            )
            st.markdown(chat_result.summary)

            # Display the move history (boards for each move)
            st.subheader("移动历史记录")
            for i, move_svg in enumerate(st.session_state.move_history):
                # Determine which agent made the move
                if i % 2 == 0:
                    move_by = "Agent White"  # Even-indexed moves are by White
                else:
                    move_by = "Agent Black"  # Odd-indexed moves are by Black
                
                st.write(f"Move {i + 1} by {move_by}")
                st.image(move_svg)

        if st.button("重新游戏"):
            st.session_state.board.reset()
            st.session_state.made_move = False
            st.session_state.move_history = []
            st.session_state.board_svg = None
            st.write("Game reset! Click 'Start Game' to begin a new game.")

    except Exception as e:
        st.error(f"An error occurred: {e}. Please check your API key and try again.")

else:
    st.warning("Please enter your LLM API Key in the sidebar to start the game.")