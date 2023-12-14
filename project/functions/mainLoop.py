# mainLoop.py
from .recording import Recording
from .api import Translation, STT, PronunciationTest
from gtts import gTTS
from playsound import playsound
from datetime import datetime
import time
from functions.databaseConnector import DatabaseConnector
import os

class MainLoop:
    def __init__(self, database_connector_instance, display_utility_instance):
        self.database_connector_instance = database_connector_instance
        self.display_utility_instance = display_utility_instance
        
        self.recording = Recording()  # 음성 녹음을 위한 클래스 객체
        self.translation = Translation()  # 번역을 위한 클래스 객체
        self.stt = STT()  # Speech To Text를 위한 클래스 객체
        self.pronunciationTest = PronunciationTest()  # 발음 평가를 위한 클래스 객체

        self.action_type = -1
        
        # Sentence 저장을 위한 변수들
        self.uID = -1
        self.ID = ""
        self.content_kor = ""
        self.content_eng = ""
        self.reg_date = ""
        self.reg_time = ""
        self.score = -1
        
        # bookmark를 처리하기 위해 만들어둔 변수들
        self.bookmarkSentenceTotalData = []
        self.bookmarkSIDList = []
        self.isReLearning = False
        self.currentReLearningDataIndex = -1
        self.reLearningSID = -1
    
    def clearDisplay(self):
        '''
            출력 화면을 초기화하는 함수
        '''
        
        self.display_utility_instance.clearDisplay()
        
    

    def saveCurrentUserInfo(self, userInfo):
        '''
            Login을 통해 전달받은 유저의 정보를 저장하는 메서드
        '''
        
        self.uID = int(userInfo[0])
        self.ID = userInfo[1]

    def chooseUserAction(self):
        '''
            MainLoop에서 user의 Input을 받아들이는 메서드
            유저가 0을 입력하면 False를 return하여 프로그램을 종료하고,
            그게 아니라면 True를 return하여 프로그램의 MainLoop을 반복한다.
        '''
        
        print("================================")
        print("Main Screen : Select Your Action")
        print("================================")
        
        user_input = input("\n1. 학습하기\n2. 북마크\n3. 내 정보\n4. 랭킹\n0. 종료\n\n")
        self.clearDisplay() # 출력 화면을 초기화한다.
    
        try:
            action_type = int(user_input)
        except Exception as e:
            print("잘못된 입력입니다. 다시 입력해주세요.\n\n")
            return False
            
        if (action_type == 0):
            # 프로그램 종료
            self.display_utility_instance.terminateProgramAfterNSec(3)
            return True
        elif (action_type in range(1, 5)):
            # 유저가 Action을 선택한 경우 (No Exit)
            if (action_type == 1):
                # 문장 학습을 시작한다.
                self.learnSentence()
            elif (action_type == 2):
                self.getBookmarkListFromDB()

                # Bookmark 데이터가 존재하는 경우
                if (len(self.bookmarkSentenceTotalData) > 0):
                    self.chooseBookmarkAction()
                    self.clearDisplay()
                
            elif (action_type == 3):
                self.showUserScoreInfo()
            elif (action_type == 4):
                self.showUserScoreRank()

            return False
        else:
            # 잘못된 입력
            self.clearDisplay()
            print("잘못된 입력입니다. 다시 입력해주세요.\n")
            return False
    
    def learnSentence(self):
        '''
            1) 문장 학습을 실행하는 메서드
        '''
        
        # 재학습이 아닐 경우에만 한국어 녹음을 실시한다.
        if (self.isReLearning == False):
            # 1) Start Recording
            # 한국어로 녹음을 시작한다.
            self.recording.start_recording("kor")

            # 2) Get speech text from the recorded voice using STT API.
            # Voice Recording으로 얻은 음성 파일에서 한국어 문장 텍스트를 뽑아낸다.
            self.content_kor = self.stt.get_text_from_audio()
        
        self.clearDisplay()
        print(f"학습 문장 : \"{self.content_kor}\"\n")

        # 3) Translate Korean text to English text using Naver Papago API
        # STT를 통해 얻은 한국어 문장을 영어 문장으로 번역한다.
        self.translation.translate_kor_to_eng(self.content_kor)

        # 4) Get Translated Text
        self.content_eng = self.translation.translate_text
        
        print("\n다음 문장을 3초 후에 발음해 보세요.")
        print(f"\"{self.content_eng}\"\n")

        # 5) Play TTS

        
        file_path = "./기말project/code/data/recorded_voice/voice_record_eng.mp3"
        if (os.path.exists(file_path)):
            os.remove(file_path)
        
        tts = gTTS(text=self.content_eng, lang="en")
        tts.save(file_path)
        playsound(file_path)

        print("\n")
        for second in range(3, 0, -1):
            print(f"{second}초 후에 시작하세요.")
            time.sleep(1)
        
        self.clearDisplay()
        print("지금 녹음을 시작하세요!")
        print(f"\"{self.content_eng}\"\n")
        
        # 6) Start recording english speaking
        self.recording.start_recording('eng')
        self.score = self.pronunciationTest.test(self.content_eng)
        
        # 오류가 발생한 경우.
        # 데이터를 저장하지 않고 return한다.
        if (self.score == -1):
            return
        
        self.clearDisplay()
        
        print(f'\"{self.content_eng}\"')
        print(f"다음 문장에 대한 당신의 발음 점수는 {self.score}점 입니다.")
        
        # 7) 데이터 저장
        current_datetime = datetime.now()
        
        self.reg_date = current_datetime.strftime("%Y-%m-%d")
        self.reg_time = current_datetime.strftime("%H:%M:%S")
        
        # 재학습이 아닌 경우
        if (self.isReLearning == False):
        # database_connector_instance를 통해서 데이터(sentence)를 저장한다.
            saveResult = self.database_connector_instance.saveCurrentSentence(
                self.uID, self.content_kor, self.content_eng,
                self.score, self.reg_date, self.reg_time)
            
            if (saveResult):
                while True:
                    
                    print("\n현재 문장을 북마크에 추가하시겠습니까?\n(북마크에 추가하면 재학습이 가능합니다.)\n")
                    addBookmark = input("1. 네\n2. 아니오\n\n")
                    self.clearDisplay()
                    
                    try:
                        addBookmark = int(addBookmark)
                    except Exception as e:         
                        print("잘못된 입력입니다. 다시 입력해 주세요.\n\n")
                        
                    if (addBookmark == 1):
                        # 북마크를 추가한다.
                        isSucceeded = self.database_connector_instance.addSentenceBookmark(self.uID)
                        
                        if (isSucceeded):
                            indicator_str = "재학습 결과를 성공적으로 저장했습니다."
                            
                            self.display_utility_instance.pauseDisplayForNSecBeforeMainScreen(3, indicator_str)
                            self.clearDisplay()
                            break              
                    elif (addBookmark == 2):       
                        self.clearDisplay()
                        break
                    else:
                        print("잘못된 입력입니다. 다시 입력해 주세요.\n\n")
            else: # 데이터 저장에 실패했을 경우
                indicator_str = "데이터를 저장하는 과정에서 에러가 발생했습니다."
                
                self.display_utility_instance.pauseDisplayForNSecBeforeMainScreen(3, indicator_str)
                self.clearDisplay()
        # 재학습인 경우
        else:
            
            # 재학습이 완료되었으므로, repeated_num을 1 증가시킨다.
            self.repeated_num += 1
        
            isSucceeded = self.database_connector_instance.updateReLearningSentence(
                self.reLearningSID, self.score, self.reg_date, self.reg_time, self.repeated_num)  
            
            # 재학습 결과 업데이트 성공
            if (isSucceeded):
                self.clearDisplay()
                eng_indicator = f"\"{self.content_eng}\"\n"
                score_indicator = f"다음 문장에 대한 당신의 발음 점수는 {self.score}점 입니다.\n"+f"Previous : {self.bookmarkSentenceTotalData[self.currentReLearningDataIndex][3]} -> Current : {self.score}"
                update_indicator = "\n\n재학습 결과를 성공적으로 업데이트 했습니다."
                
                indicator_str = eng_indicator + score_indicator + update_indicator
                
                # 재학습 결과 업데이트에 성공했으므로,
                # 현재 결과를 바탕으로 local 데이터를 업데이트한다.
                # self.applyReLearningResultOnLocalData()
                self.applyReLearningResultOnLocalData()
                
                self.display_utility_instance.pauseDisplayForNSecBeforeBookmark(5, indicator_str)
                self.clearDisplay()
            else:
                indicator_str = "재학습 결과를 업데이트하는 과정에서 에러가 발생했습니다."
                
                self.display_utility_instance.pauseDisplayForNSecBeforeBookmark(5, indicator_str)
                self.clearDisplay()
    
    def applyReLearningResultOnLocalData(self):
        
        # 2023.12.03, jdk
        # 데이터가 왜 안바뀌나 했더니... Tuple이여서 안바뀜!
        # Tuple을 새롭게 생성해서 바꾸어주어야 한다.
        newSentenceData = (self.reLearningSID, self.content_kor, self.content_eng, self.score,
                                self.reg_date, self.reg_time, self.repeated_num)

        self.bookmarkSentenceTotalData[self.currentReLearningDataIndex] = newSentenceData
                
    def getBookmarkListFromDB(self):
        '''
            User가 Bookmark에 등록한 문장들을 가져오는 메서드
        '''
        
        # 현재 로그인한 유저가 등록한 Bookmark List를 가져온다.
        isSucceeded = self.database_connector_instance.getBookmarkList(self.uID)
        
        if (isSucceeded):
            
            # Query가 성공했으므로, 얻어온 결과를 불러온다.
            self.bookmarkSentenceTotalData = self.database_connector_instance.getCurrentQueryResult()
            
            # data가 아무것도 존재하지 않을 경우
            if (len(self.bookmarkSentenceTotalData) == 0):
                indicator_str = "Bookmark가 존재하지 않습니다."
                self.display_utility_instance.pauseDisplayForNSecBeforeMainScreen(3, indicator_str)
        else:
            indicator_str = "Bookmark 목록을 가져오는 중에 에러가 발생했습니다."
            self.display_utility_instance.pauseDisplayForNSecBeforeMainScreen(3, indicator_str)

    def displayBookmarkList(self):
        '''
            Query의 결과로 전달받은 Bookmark List를
            Parsing하여 출력하는 메서드이다.
        '''
        
        print("* My Sentence Bookmark *\n")
        print("재학습을 원하는 문제 번호를 입력하세요.")
        print("(0을 입력하면 메인 화면으로 돌아갑니다.)\n")
        
        bookmarkList = self.bookmarkSentenceTotalData
        
        # sID[0], content_kor[1], content_eng[2], score[3], reg_date[4], reg_time[5], repeated_num[6]
        for idx in range(0, len(bookmarkList)):
            bookmarked_sentence_data = bookmarkList[idx]
            sID = bookmarked_sentence_data[0]
            content_kor = bookmarked_sentence_data[1]
            content_eng = bookmarked_sentence_data[2]
            score = bookmarked_sentence_data[3]
            reg_date = bookmarked_sentence_data[4]
            reg_time = bookmarked_sentence_data[5]
            repeated_num = bookmarked_sentence_data[6]
            
            # 현재 유저가 bookmark에 추가한 sID를 list에 추가한다.
            self.bookmarkSIDList.append(int(sID))
            
            print("===============================")
            print(f"Q. : {sID}")
            print(f"SCORE : {score}")
            print(f"DATE : {reg_date} {reg_time}")
            print(f"KOR : \"{content_kor}\"")
            print(f"ENG : \"{content_eng}\"")
            print(f"REPEATED : {repeated_num} times")
            print("===============================")
            print("\n\n")              
            
    def clearAllFlagsForReLearning(self):
        '''
            재학습에 사용되는 모든 Flag 및 변수들을 초기화하는 메서드
        '''
        
        self.isReLearning = False
        self.bookmarkSentenceTotalData = []
        self.bookmarkSIDList = []
        self.currentReLearningDataIndex = -1
        self.reLearningSID = -1
        
    
    def chooseBookmarkAction(self):
        
        self.clearDisplay()
        self.isReLearning = True

        # Bookmark 재학습에 대한 Loop
        while (True):
            
            # 전달받은 BookmarkList 데이터를 parse하고 출력한다
            self.displayBookmarkList()
            
            userActionInput = input("번호를 입력하세요. (0을 입력하면 돌아가기)\n")
            
            try:
                userActionInput = int(userActionInput)
            except Exception as e: 
                self.clearDisplay()
                print("잘못된 입력입니다. 다시 입력하세요.\n")
                continue
            
            # Bookmark 종료.
            if (userActionInput == 0):
                self.clearAllFlagsForReLearning()
                break
            # user가 입력한 숫자가 bookmarkSIDList에 있을 경우 재학습을 시도한다.
            elif (userActionInput in self.bookmarkSIDList):
                self.reLearningSID = userActionInput
                
                # 유저가 입력한 sID가 List 상에서 몇 번째에 존재하는지 index를 검사한다.
                self.currentReLearningDataIndex = self.bookmarkSIDList.index(self.reLearningSID)
                self.startReLearning()
    
    def startReLearning(self):
        
        # 재학습 flag를 set한다.
        self.content_kor = self.bookmarkSentenceTotalData[self.currentReLearningDataIndex][1]
        self.content_eng = self.bookmarkSentenceTotalData[self.currentReLearningDataIndex][2]
        self.repeated_num = self.bookmarkSentenceTotalData[self.currentReLearningDataIndex][6]
        
        # 재학습 실시
        self.learnSentence()
        
    def showUserScoreInfo(self):
        '''
            특정 유저의 발음 점수 정보를 출력하는 메서드
        '''

        # 특정 유저의 발음 점수 정보를 가져옴
        user_score_info = self.database_connector_instance.getUserScoreInfo(self.uID)

        if user_score_info:
            print("\n--- 발음 점수 정보 ---")
            for row in user_score_info:
                print(f"최고점수: {row[1]}, 최저점수: {row[2]}, 평균점수: {row[3]}")
        else:
            print("학습된 데이터가 존재하지 않습니다.")
  
        
    def showUserScoreRank(self):
        '''
        사용자 발음 점수 랭킹을 표시합니다
        '''
        # 데이터베이스에서 사용자 발음 점수 랭킹 정보를 가져옵니다
        user_score_rank_info = self.database_connector_instance.getUserScoreRank()

        if user_score_rank_info:
            print("\n--- 사용자 발음 점수 랭킹 ---")
            print("{:<15} {:<10} {:<10} {:<10}".format("ID", "점수 순위", "문장 갯수", "점수 평균"))
            for row in user_score_rank_info:
                # 특정 유저 ID와 문장 번호에 해당하는 Sentence_Problem 테이블의 content_eng 가져오기
                user_id = row[0]
                
                user_ID_info = self.database_connector_instance.getUserIDInfo(user_id)
                if user_ID_info:
                    userId = user_ID_info  # 전체 ID를 가져오도록 수정
                
                user_avg_score_info = self.database_connector_instance.getUserAvgScoreInfo(user_id)
                if user_avg_score_info:
                    avg_score = user_avg_score_info
                
                print("{:<15} {:<10} \t{:<10} \t{:<10}".format(userId, row[1], row[2], avg_score))
            print("\n")
        else:
            print("사용자 발음 점수 랭킹을 불러오는 데 실패했습니다.")

    
        
                
            
        
        
        

