# databaseConnector.py
import sqlite3

class DatabaseConnector:
    def __init__(self):
        self.conn = sqlite3.connect(
            "c:\\Users\\kwc18\\OneDrive\\바탕 화면\\공부자료\\데이터베이스\\기말project\\my_db.db")
        
        self.curs = self.conn.cursor()
        
        # Current Query Result
        self.currentQueryResult = None
        
        # Query List
        self.bookmarkQuery = (
        "select Sentence_Bookmark.sID, content_kor, content_eng, "
        "score, reg_date, reg_time, repeated_num "
        "from Sentence_Problem, Sentence_Bookmark "
        "where Sentence_Problem.sID = Sentence_Bookmark.sID "
        "and Sentence_Bookmark.uID = ?;")       
        self.reLearningUpdateQuery_Problem = (
        "update Sentence_Problem set score = ?," 
        "reg_date = ?, reg_time = ? where sID = ?;")
        self.reLearningUpdateQuery_Bookmark = "update Sentence_Bookmark set repeated_num = ? where sID = ?;"
            
    def getCurrentQueryResult(self):
        '''
            2023.12.03, jdk
            가장 최근에 수행한 Query의 결과를 return하는 메서드
            Query 수행이 올바르게 되었는지 확인하기가 쉽지 않아서
            이와 같이 결과를 return하는 메서드를 추가하였음.
        '''
        
        return self.currentQueryResult
            
    def verifyUser(self, ID, PW):
        
        # 데이터베이스에서 로그인 정보 확인
        self.curs.execute(
            "SELECT * FROM User_Info WHERE ID = ? AND PW = ?", (ID, PW))
        result = self.curs.fetchone()

        return result

    def signUpUser(self, ID, PW):
        
        # 데이터 삽입 (uID는 자동으로 생성되도록 설정)
        self.curs.execute(
            "INSERT INTO User_Info (ID, PW) VALUES (?, ?)", (ID, PW))
        
        self.conn.commit()
            
    def saveCurrentSentence(self, uID, content_kor, content_eng, score, reg_date, reg_time):
        '''
            유저가 학습한 문장을 Database에 저장하는 메서드
        '''

        try:
            self.curs.execute("insert into Sentence_Problem (uID, content_kor, content_eng, score, reg_date, reg_time)" 
                              "values (?, ?, ?, ?, ?, ?);", 
            (uID, content_kor, content_eng, score, reg_date, reg_time))
            self.conn.commit()
            
            # 데이터베이스 저장 성공
            return True
            
        except Exception as e:     
            # 데이터베이스 저장 실패
            return False
    
    def addSentenceBookmark(self, uID):
        '''
            유저가 가장 최근에 학습한 문장을 Bookmark에 추가하는 메서드
        '''
        
        sentence_sID = None
        
        # 유저가 최근에 학습한 Sentence의 sID를 가져온다.
        try:
            self.curs.execute("select sID from Sentence_Problem where uID = ? order by reg_date desc, reg_time desc;", (uID,))
            query_result = self.curs.fetchone()[0] # 가장 최근에 학습한 Sentence의 sID를 얻어낸다.
            sentence_sID = int(query_result)
        except Exception as e:
            print(f"\n북마크를 지정하는 과정에서 오류가 발생했습니다. : {e}\n\n")
            return False
        
        # 해당 sID에 대해서 Bookmark를 추가한다.
        try:
            self.curs.execute("insert into Sentence_Bookmark (uID, sID) values(?, ?)", (uID, sentence_sID))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"\n북마크를 지정하는 과정에서 오류가 발생했습니다. : {e}\n\n")
            return False
    
    def getBookmarkList(self, uID):
        '''
            유저가 Bookmark에 등록한 Sentence의 List를 가져오는 메서드
        '''
        
        try:
            self.curs.execute(self.bookmarkQuery, (uID,))
            self.currentQueryResult = self.curs.fetchall()
            return True
        except Exception as e:
            return False
        
        
    def getUserScoreInfo(self, user_id):
        # 특정 유저의 발음 점수 정보를 데이터베이스에서 가져오는 메서드
        try:
            self.curs.execute(
                "SELECT * FROM User_Score_Info WHERE uID = ?", (user_id,))
            user_score_info = self.curs.fetchall()
            return user_score_info
        except Exception as e:
            print("발음 점수 정보를 가져오는 과정에서 에러가 발생했습니다. ")
            return None        
        
    def getUserScoreRank(self):
        '''
            User_Score_Rank 뷰에서 모든 사용자 점수 랭킹 정보를 가져오는 메서드
        '''
        try:
            self.curs.execute(
                "SELECT * FROM User_Score_Rank"
            )
            user_score_rank_info = self.curs.fetchall()
            return user_score_rank_info
        except Exception as e:
            print(f"데이터베이스에서 정보를 가져오는 중 오류 발생: {e}")
            return None
        
    def getUserAvgScoreInfo(self, user_id):
        # 특정 유저의 평균 발음 점수 정보를 데이터베이스에서 가져오는 메서드
        
        self.curs.execute(
            "SELECT avg_score FROM User_Score_Info WHERE uID = ?", (user_id,))
        
        return self.curs.fetchone()[0]
        
    def getUserIDInfo(self, uID):
        
        # 데이터베이스에서 ID 정보 확인
        self.curs.execute(
            "SELECT ID FROM User_Info WHERE uID = ?", (uID,))
        
        return self.curs.fetchone()[0]
    
    
    def close_connection(self):
        '''
            Cursor와 DB Connection의 연결을 끊는 메서드
        '''
        
        # 커서와 연결 닫기
        if self.curs:
            self.curs.close()

        # 데이터베이스 연결 닫기
        if self.conn:
            self.conn.close()
                  
    def updateReLearningSentence(self, sID, score, reg_date, reg_time, repeated_num):
        '''
            재학습 결과에 따라 기존 데이터를 updaet하는 메서드
        '''
        
        try:
            self.curs.execute(self.reLearningUpdateQuery_Problem, (score, reg_date, reg_time, sID))
            self.conn.commit()
        except Exception as e:
            print(f"\n재학습 결과를 저장하는 과정에서 오류가 발생했습니다. : {e}\n\n")
            return False
        
        try:
            self.curs.execute(self.reLearningUpdateQuery_Bookmark, (repeated_num, sID))
            self.conn.commit()
        except Exception as e:
            print(f"\n재학습 결과를 저장하는 과정에서 오류가 발생했습니다. : {e}\n\n")
            return False
        
        return True
        
        