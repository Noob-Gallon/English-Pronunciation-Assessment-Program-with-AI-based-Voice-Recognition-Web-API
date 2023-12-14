# -*- coding:utf-8 -*-

#####################################################################################
#####################################################################################

from functions.Login import UserLogin
from functions.databaseConnector import DatabaseConnector
from functions.mainLoop import MainLoop
from functions.display import DisplayUtility

#####################################################################################
#####################################################################################
# 데이터베이스 연결을 위한 클래스 객체
database_connector_instance = DatabaseConnector()

# 화면 초기화를 위한 클래스 객체
display_utility_instance = DisplayUtility()

# 회원가입 및 로그인을 위한 클래스 객체
user_login_instance = UserLogin(database_connector_instance)  

# Main Loop을 수행하기 위한 클래스 객체
main_loop_instance = MainLoop(database_connector_instance, display_utility_instance) 

#####################################################################################
#####################################################################################

# 프로그램 시작 전에 화면을 초기화한다.
display_utility_instance.clearDisplay()
print("========================================")
print("English Pronunciation Assessment Program")
print("                made by WC Kim, DK Jeong")
print("========================================")
print("\n\n")

if __name__ == "__main__":
    
    # 1) SignIn & SingUp Procedure
    while (True):
        
        mode = input("1. 로그인\n2. 회원가입\n\n")
        print("\n")

        try:
            if mode == '1':
                display_utility_instance.clearDisplay()
                result = user_login_instance.login()
                if (result): 
                    display_utility_instance.clearDisplay()
                    
                    # Login Succeeded.
                    # 로그인이 성공했으므로, 유저의 정보를 전달받아
                    # main_loop Class 내에 저장하여 사용한다.
                    userInfo = user_login_instance.getCurrentUserInfo()
                    main_loop_instance.saveCurrentUserInfo(userInfo)
                    break
                else:
                    # Login Failed.
                    print("아이디 또는 비밀번호가 잘못되었습니다. 다시 입력해 주세요.\n\n")
                    continue
            elif mode == '2':
                # 회원 가입 후, 다시 로그인으로 돌아간다.
                display_utility_instance.clearDisplay()
                user_login_instance.signup()
                display_utility_instance.clearDisplay()
                print("회원가입이 완료되었습니다.\n\n")
                continue
            else:
                display_utility_instance.clearDisplay()
                print("잘못된 입력입니다. 다시 입력해주세요.\n\n")
        except Exception as e:
            print(f"에러 발생: {e}\n\n")
            print("에러가 발생했습니다. 관리자에게 문의해 주세요.\n\n")
            continue

    # 2) Main Program is started here.
    while (True):
        # 유저의 Action을 전달받는다.
        isExit = main_loop_instance.chooseUserAction()

        # 반환된 값이 True라면, 프로그램을 종료한다. 
        if (isExit):
            break

    # 3) clear connection instances(conn & curs)
    database_connector_instance.close_connection()

#####################################################################################
#####################################################################################