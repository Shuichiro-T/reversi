from __future__ import division

import argparse
import os
import sys

from main import Reversi
from dqn_agent import DQNAgent

inp = ""
# 直接起動された際に実行（テスト用）
if __name__ == "__main__":
    
    env = Reversi()
    agent = DQNAgent(env.enable_actions,env.name,env.Board_Size)
    agent.load_model()
    print("---GAME START---")
    env.print_screen()
    while not env.End_Check():
        print("USERのターン")
        enables = env.enable(1)
        if len(enables) > 0:
            flg = False
            while not flg:
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
                        print(action)
                        print(j)
                        flg = True
                        break
            n = env.update(action, 1)
            
        else:
            print("パス")
        if env.End_Check == True:break
        
        print("AIのターン")
        env.print_screen()
        enables = env.enable(2)
        if len(enables) > 0:
            qvalue, action_t = agent.select_enable_action(env.cells, enables)
            print('>>>  {:}'.format(action_t))              
            env.update(action_t, 2)
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