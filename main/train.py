import numpy as np
import copy

from main import Reversi
from dqn_agent import DQNAgent


if __name__ == "__main__":
    # parameters
    n_epochs = 10000
    env = Reversi()

    ID = [env.White,env.Black,env.White]
    players = []
    players.append(DQNAgent(env.enable_actions,env.name,env.Board_Size))
    players.append(DQNAgent(env.enable_actions,env.name,env.Board_Size))

    for e in range(n_epochs):
        # 初期化
        env.reset()
        end_check = False
        while not end_check:
            for i in range(0,len(players)):
                state = env.cells
                targets = env.enable(ID[i])

                if len(targets) > 0:
                    for tr in targets:
                        tmp = copy.deepcopy(env)
                        tmp.update(tr, ID[i])
                        win = tmp.win_check()
                        end = tmp.End_Check()
                        state_X = tmp.cells
                        target_X = tmp.enable(ID[i+1])
                        if len(target_X) == 0:
                            target_X = tmp.enable(ID[i])
                        for j in range(0, len(players)):
                            reword = 0
                            if end == True:
                                if win == ID[j]:
                                    reword = 1
                            
                            players[j].store_experience(state, targets, tr, reword, state_X, target_X, end)
                            players[j].experience_replay()
                    
                    action = players[i].select_action(state,targets,players[i].exploration)
                    env.update(action,ID[i])

                    loss = players[i].current_loss
                    Q_max, Q_action = players[i].select_enable_action(state,targets)
                    print("player:{:1d} | pos:{:2d} | LOSS: {:.4f} | Q_MAX: {:.4f}".format(ID[i], action, loss, Q_max))


            end_check = env.End_Check()
        
        w = env.win_check()
        print("EPOCH:{:03d}/{:03d} | wih player{:1d}".format(e,n_epochs,w))
    players[1].save_model()


