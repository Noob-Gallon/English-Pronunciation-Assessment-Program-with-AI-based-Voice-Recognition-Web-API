import sqlite3

class UserLogin:
    def __init__(self, database_connector_instance):
        self.database_connector_instance = database_connector_instance
    
    def saveUserInfo(self, queryResult):
        '''
            Query로 전달받은 현재 유저의 정보를
            클래스 내에 저장하는 메서드
        '''
        self.uID = queryResult[0]
        self.ID = queryResult[1]
        
    def getCurrentUserInfo(self):
        '''
            현재 로그인한 유저의 정보(uID, ID)를
            반환하는 메서드
        '''
        return (self.uID, self.ID)

    def login(self):
        '''
            로그인 메서드
        '''
        
        # 사용자로부터 입력 받기
        ID = input("사용자 이름을 입력하세요: ")
        PW = input("비밀번호를 입력하세요: ")

        # Query 수행
        result = self.database_connector_instance.verifyUser(ID, PW)

        if result:
            # 로그인에 성공했을 경우,
            # 로그인한 유저의 정보를 저장하고,
            # True를 return하여 결과를 알린다.
            self.saveUserInfo(result)
            return True
        else:
            # 로그인에 실패했을 경우,
            # False를 return하여 결과를 알린다.
            return False

    def signup(self):
        '''
            회원가입 메서드
        '''
        
        # 사용자로부터 입력 받기
        ID = input("사용자 이름을 입력하세요: ")
        PW = input("비밀번호를 입력하세요: ")
        
        self.database_connector_instance.signUpUser(ID, PW)

        



# 2023.12.02, jdk
# 필요없는 부분으로, 주석처리한다.

# if __name__ == "__main__":
#     user_login_instance = UserLogin()

#     # 입력 모드 받기
#     mode = input("1. 로그인\n2. 회원가입\n")

#     try:
#         if mode == '1':
#             user_login_instance.login()
#         elif mode == '2':
#             user_login_instance.signup()

#     except Exception as e:
#         print("에러 발생:", e)

#     finally:
#         user_login_instance.close_connection()