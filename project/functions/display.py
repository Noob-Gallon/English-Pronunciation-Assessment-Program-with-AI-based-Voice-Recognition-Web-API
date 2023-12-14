import os
import time

class DisplayUtility:
    def __init__(self):
        # 화면 초기화를 위한 lambda 함수 (clear)
        self.clear = lambda : os.system('cls')
        
    def clearDisplay(self):
        self.clear()
        
    def pauseDisplayForNSecBeforeMainScreen(self, N, indicatorStr=""):
        for sec in range(N, 0, -1):
            if (indicatorStr != ""):
                print(f"{indicatorStr}\n\n")
            
            print(f"\n{sec}초 뒤에 메인 화면으로 돌아갑니다...")
            time.sleep(1)
            self.clearDisplay()   
            
    def pauseDisplayForNSecBeforeBookmark(self, N, indicatorStr=""):
        for sec in range(N, 0, -1):
            if (indicatorStr != ""):
                print(f"{indicatorStr}\n\n")
            
            print(f"\n{sec}초 뒤에 북마크로 돌아갑니다...")
            time.sleep(1)
            self.clearDisplay()   
    
    def pauseDisplayForNSecBeforeTermination(self, N):
        for sec in range(N, 0, -1):
            print(f"{sec}초 뒤에 프로그램이 종료됩니다...")
            time.sleep(1)
            self.clearDisplay()   
    
    def terminateProgramAfterNSec(self, N):
        self.pauseDisplayForNSecBeforeTermination(N)
        self.clearDisplay()