# -*- coding: utf-8 -*-

import argparse
import tkinter as tk
from main import Reversi
from dqn_agent import DQNAgent


class ReversiDisplay(tk.Tk):
    def __init__(self, model_path):
        super(ReversiDisplay, self).__init__()
        
        self.BORD_PX_SIZE = 480
        self.keylock = False
        
        self.model_path = model_path
        self.title("リバーシ")
        self.geometry("{}x{}+{}+{}".format(self.BORD_PX_SIZE + 30, self.BORD_PX_SIZE + 30 + 100, self.BORD_PX_SIZE, 100))
        self.color = ["", "white", "black"]
        # {tag: position}
        self.tag2pos = {}
        # 座標からtagの変換
        self.z2tag = {}
        
        #メインクラスの作成
        env = Reversi()
        self.bord_size = env.Board_Size
        self.env = env
        
        #対戦エージェントの作成
        self.agent = DQNAgent(env.enable_actions, env.name, env.Board_Size)
        self.agent.load_model(args.model_path)
       
        
        # 符号
        self.numstr = self.make_numstr()
        self.alpstr = self.make_alpstr()
        # Set up some variables
        self.set_variables()
        # Set up game board
        self.set_board()
        # Set up some buttons
        self.set_button()
        
    def make_numstr(self):
        numstr = ''
        for i  in range(self.bord_size):
            numstr = numstr + str(i + 1)
        return numstr

    def make_alpstr(self):
        alpstr = ''
        for i  in range(self.bord_size):
            alpstr = alpstr + chr(i + ord('a'))
        return alpstr


    def set_variables(self):
        self.sentinel = [2] * (self.bord_size + 2) + [[0, 2][i in [0, (self.bord_size + 1)]] for i in range((self.bord_size + 2))] * self.bord_size + [2] * (self.bord_size + 2)
        #self.sentinel = [2] * 10 + [[0, 2][i in [0, 9]] for i in range(10)] * 8 + [2] * 10
        self.board2info = [0] * (self.bord_size ** 2)
        self.playerTurn = 1
        self.gorilla = 0
        self.is_end = 0

    def set_board(self):
        # オセロ盤
        self.board = tk.Canvas(self, bg="lime green", width=self.BORD_PX_SIZE + 30, height=self.BORD_PX_SIZE + 30)
        self.board.place(x=0, y=0)
        
        #マス目のサイズ
        cell_size = int(self.BORD_PX_SIZE / self.bord_size)
        
        # オセロ盤を作成
        for i, y in zip(self.numstr, range(15, self.BORD_PX_SIZE - 15 + 1, cell_size)):
            for j, x in zip(self.alpstr, range(15, self.BORD_PX_SIZE - 15 + 1,  cell_size)):
                pos = x, y, x + cell_size, y + cell_size
                tag = i + j
                self.tag2pos[tag] = pos
                self.board.create_rectangle(*pos, fill="lime green", tags=tag)
                self.z2tag[self.z_coordinate(tag)] = tag
                self.board.tag_bind(tag, "<ButtonPress-1>", self.pressed)
        # 初期設定
        #self.get_sentinel_info()
        #self.get_board_info()
        
        #基準点計算
        std = int((self.bord_size + 2) * ((self.bord_size + 2) / 2) - ((self.bord_size + 2) / 2)) 
        #for z, turn in [(44, 1), (45, -1), (54, -1), (55, 1)]:
        for z, turn in [(std - 1, 1), (std, -1), (std + self.bord_size + 1, -1), (std + self.bord_size + 2, 1)]:
            tag = self.z2tag[z]
            self.sentinel[z] = turn
            self.board.create_oval(*self.tag2pos[tag], fill=self.color[turn], tags=tag)
        self.sent2board()
        #self.get_sentinel_info()
        #self.get_board_info()
        #self.get_board_info()
        self.get_candidates()
        self.switch_board()


    def set_button(self):
        self.reset = tk.Button(self, text="reset", relief="groove", command=self.clear)
        self.reset.place(x=self.BORD_PX_SIZE * 2 / 8 , y=self.BORD_PX_SIZE + 60)
        self.quit_program = tk.Button(self, text="quit", relief="groove", command=self.close)
        self.quit_program.place(x=self.BORD_PX_SIZE * 6 / 8, y=self.BORD_PX_SIZE + 60)
        

    def get_sentinel_info(self):
        # self.sentinelを表示
        print("{:-^31s}".format("self.sentinel"))
        print(*[str(" {:2d} " * self.bord_size).format(*self.sentinel[i:i+self.bord_size]) \
            #for i in range(11, 89, 10)], sep="\n")
            for i in range( self.bord_size + 3,  ((self.bord_size + 2) ** 2) - ( self.bord_size + 3),  self.bord_size + 2)], sep="\n")
        print('-'*31)

    def get_board_info(self):
        # self.board2infoを表示
        print("{:-^31s}".format("self.board2info"))
        print(*[str(" {:2d} " * self.bord_size).format(*self.board2info[i:i+self.bord_size]) \
            for i in range(0, self.bord_size ** 2, self.bord_size)], sep="\n")
        print('-'*31)

    def sent2board(self):
        # self.sentinelをself.board2infoに変換
        self.board2info = [self.sentinel[j] for i in range(self.bord_size + 2 + 1, (self.bord_size + 2) ** 2 - (self.bord_size + 2 + 1) , self.bord_size + 2) for j in range(i, i+self.bord_size)]

    def z_coordinate(self, tag):
        x = self.alpstr.index(tag[1])+1
        y = self.numstr.index(tag[0])+1
        return y*(self.bord_size + 2) + x

    def get_candidates(self):
        # 置ける場所を探す
        self.candidates = {}
        for y in self.numstr:
            for x in self.alpstr:
                tag = y + x
                if self.sentinel[self.z_coordinate(tag)] != 0:
                    continue
                self.search(tag)

        if len(self.candidates) == 0:
            # 候補手がない
            print("パスしまーす（{}）".format(['', '白', '黒'][self.playerTurn]))
            # ターンを変えて候補手を探す。
            self.gorilla += 1
            if self.gorilla == 2:
                self.is_end = 1
                self.print_result()
            else:
                self.playerTurn = -self.playerTurn
                self.get_candidates()
                self.switch_board()
        else:
            # 候補手がある。
            self.print_turn()
            self.gorilla = 0

    def pressed(self, event):
        if self.keylock or True if self.is_end == 1 else False:
            return
        self.keylock = True
        
        item_id = self.board.find_closest(event.x, event.y)
        tag = self.board.gettags(item_id[0])[0]
        if tag not in self.candidates:
            return
        self.update_board(tag)
        
        self.keylock = False

    def update_board(self, tag):
        """ 色々更新する。
            1. 盤面の更新。
            2. 盤情報の更新。
            3. ターンの更新。
        """
        #ゲームが終わっていたら実行しない
        if self.is_end == 1:
            return 

        ### 1. 盤面の更新。###
        self.switch_board(0)
        # 反転処理
        for z in self.candidates[tag]:
            ctag = self.z2tag[z]
            self.board.create_oval(*self.tag2pos[ctag], fill=self.color[self.playerTurn])
            self.sentinel[z] = self.playerTurn
        # 新しく石を置く
        self.board.create_oval(*self.tag2pos[tag], fill=self.color[self.playerTurn])

        ### 2. 盤情報の更新。###
        self.sentinel[self.z_coordinate(tag)] = self.playerTurn
        self.sent2board()
        #メインも更新
        self.env.update(self.tag2action(tag), self.convertPlayer())
        
        
        # 盤情報を出力
        #self.get_board_info()
        #print(self.env.cells)
        ### 3. ターンの更新。###
        self.playerTurn = -self.playerTurn
        # 候補手を探す。
        self.get_candidates()
        self.switch_board()
        #黒の場合
        if self.playerTurn == -1:
        #    self.thread()
        ##ここでAgentを呼び出す。
            qvalue, action_t = self.agent.select_enable_action(self.env.cells, self.env.enable(self.convertPlayer()))
            self.update_board(self.action2tag(action_t))
        
    def tag2action(self, tag):
        row = int(tag[0:1]) - 1
        col = ord(tag[1:2]) - ord('a')
        return row * self.bord_size + col
    
    def action2tag(self, action):
    
        #タグの最初の数字を求める
        numstr = str(int(action / self.bord_size) + 1)
        alpstr =  chr(action % self.bord_size + ord('a'))
        return numstr + alpstr
    
    def convertPlayer(self):
        return 1 if self.playerTurn == 1 else 2


    def search(self, tag):
        z = self.z_coordinate(tag)
        #for num in [-10, 10, 1, -1, -11, 11, -9, 9]:
        for num in [- (self.bord_size + 2) , (self.bord_size + 2), 1, -1, -(self.bord_size + 3), (self.bord_size + 3), -(self.bord_size + 1), (self.bord_size + 1)]:
            self.flag = False
            self.tmp = []
            result = self._search(z+num, num)
            if result == -1:
                continue
            if tag in self.candidates:
                self.candidates[tag] += self.tmp
            else:
                self.candidates[tag] = self.tmp

    def _search(self, z, num):
        v = self.sentinel[z]
        if v in [0, 2]:
            return -1
        if v == self.playerTurn:
            return z if self.flag else -1
        self.flag = True
        self.tmp.append(z)
        return self._search(z+num, num)

    def switch_board(self, color=1):
        # 候補手のところの色を変える
        for tag in self.candidates.keys():
            self.board.itemconfig(tag, fill=["lime green", "lawn green"][color])

    def print_turn(self):
        print("{}のターンです。".format(['', '白', '黒'][self.playerTurn]))

    def print_result(self):
        # 結果の表示
        total_black = sum([0, 1][x == -1] for x in self.board2info)
        total_white = sum([0, 1][x == 1] for x in self.board2info)
        print("{:-^29s}".format("結果"))
        if total_black == total_white:
            print(f"{'引き分け':^29s}")
        else:
            result = ["黒", "白"][total_black < total_white]
            print(f"{result+'の勝ち':^29s}")
        print("黒：{}".format(total_black))
        print("白：{}".format(total_white))

    def clear(self):
        # 初期化
        print("\n"*30)
        self.board.delete("all")
        self.set_variables()
        self.set_board()
        self.keylock = False
        
        self.env.reset()

    def close(self):
        # 終了処理
        self.quit()

    def run(self):
        self.mainloop()


   


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    #学習済モデルのパスを引数より受け取る
    parser.add_argument(
        "-m",
        "--model_path",
        default="",
        help="学習モデルのパス")
    args = parser.parse_args() 
    
    app = ReversiDisplay(args.model_path)
    app.run()