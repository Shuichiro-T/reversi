import numpy as np
import os
import sys

class Reversi():
    # 基本値の設定
    def __init__(self):
        self.name = os.path.splitext(os.path.basename(__file__))[0]
        self.Blank = 0
        self.White = 1
        self.Black = 2
        self.Board_Size = 8
        # 行動値の設定
        self.enable_actions = np.arange(self.Board_Size*self.Board_Size)
        # 初期設定
        self.reset()

    # 初期化
    def reset(self):
        self.cells = np.zeros((self.Board_Size,self.Board_Size))
        self.set_cell(27, self.White)
        self.set_cell(36, self.White)
        self.set_cell(28, self.Black)
        self.set_cell(35, self.Black)

    # 指定個所の中身を返す
    def get_cell(self,action):
        x = int(action / self.Board_Size)
        y = int(action % self.Board_Size)
        return self.cells[x][y]

    # 石を置く処理
    def set_cell(self,action,color):
        x = int(action / self.Board_Size)
        y = int(action % self.Board_Size)
        self.cells[x][y] = color

    # 石を置いた際の処理
    # または置ける場所の判定
    def put(self,action,color,put=True):
        # まだ置かれていない場所
        if self.get_cell(action) != self.Blank:
            return -1
        l = []
        x = int(action/self.Board_Size)
        y = int(action%self.Board_Size)
        xd = self.Board_Size - x - 1
        yd = self.Board_Size - y - 1
        t = 0
        
        # 置かれた場所の周囲の石を確認していく
        # -9 -8 -7
        # -1  0 +1
        # +7 +8 +9
        # 一次元配列にした際には上のような位置関係になる
        for i,deep in zip([-9,-8,-7,-1,1,7,8,9],[min(x,y),x,min(x,yd),y,yd,min(xd,y),xd,min(xd,yd)]):
            li,b,m = [],[],[]
            k,n = 0,0
            
            # 影響範囲を取得
            li = self.enable_actions[action + i::i][:deep]

            # 影響範囲の値を取得
            for j in li:
                b.append(self.get_cell(j))
            
            # 置いた際の動きについて記憶
            for j in b:
                if int(j) == self.Blank:
                    # 空欄があればBreakする
                    break
                elif int(j) == color:
                    # 自分の色の石があれば集計終了
                    l += m
                    n = k
                    break
                else:
                    # 対戦相手の色があればひっくり返す石リストに追加
                    j += 1
                    m.insert(0,li[k])
                k += 1
            t += n

        # 石がなければパス
        if t == 0:
            return 0
        
        # もし引っ繰り返す処理が必要ならば実行
        if put:
            for i in l:
                self.set_cell(i, color)
            self.set_cell(action,color)

        # 個数を返す
        return t

    # 石を置けるかどうかの判定
    def enable(self, color):
        result = []
        for action in self.enable_actions:
            if self.get_cell(action) == self.Blank:
                if self.put(action, color , False) > 0:
                    result.insert(0, action)
        return result

    # アップデート
    def update(self,action,color):
        n = self.put(action,color,False)
        if n > 0:
            self.put(action,color,True)
        return n

    # 終了判定
    def End_Check(self):
        b = self.enable(self.Black)
        w = self.enable(self.White)
        if len(b) == 0 and len(w) == 0:
            return True
        return False

    def get_score(self,color):
        score = 0
        for i in self.enable_actions:
            if self.get_cell(i) == color:
                score += 1
        return score

    def win_check(self):
        BScore = self.get_score(self.Black)
        WScore = self.get_score(self.White)

        if BScore == WScore:
            return 0
        elif BScore < WScore:
            return 1
        elif BScore > WScore:
            return 2

    # 描画
    def print_screen(self):
        for i in range(0,self.Board_Size):
            s1 = ""
            for j in range(0,self.Board_Size):
                s2 = ""
                if self.cells[i][j] == self.Blank:
                    s2 = str(i * 8 + j)
                    if len(s2) == 1:
                        s2 = " " + s2
                elif self.cells[i][j] == self.Black:
                    s2 = "○"
                elif self.cells[i][j] == self.White:
                    s2 = "●"
                s1 = s1 + " " + s2
            print(s1)


inp = ""
# 直接起動された際に実行（テスト用）
if __name__ == "__main__":
    
    env = Reversi()
    print("---GAME START---")
    env.print_screen()
    while not env.End_Check():
        for i in range(1,3):
            enables = env.enable(i)
            if len(enables) > 0:
                flg = False
                while not flg:
                    if i == env.White:
                        print("●のターン")
                    else:
                        print("○のターン")
                    env.print_screen()
                    print("番号を入力して下さい(exitでゲーム終了)")
                    print(enables)
                    inp = input(">>>")
                    if inp == "exit":
                        print("ゲーム終了")
                        sys.exit()
                    try:
                        action = int(inp)
                    except:
                        continue
                    for j in enables:
                        if action == j:
                            flg = True
                            break
                n = env.update(action, i)
                
            else:
                print("パス")

    print("---GAME OVER---")
    env.print_screen()
    if env.win_check() == env.White:
        print("白の勝ち")
    elif env.win_check() == env.Black:
        print("黒の勝ち")
    else:
        print("引き分け")
    
