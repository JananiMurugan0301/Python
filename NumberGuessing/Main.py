import pyodbc
import random
import math
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

#connection string
conn=pyodbc.connect(
'''
DRIVER={SQL Server};
SERVER=tcp:<servername>.database.windows.net;
DATABASE=<dbname>;
UID=<username>;
PWD=<password>;
'''
)

## Checking the user
UserName=input('Enter your UserName')

cur=conn.cursor()
cur.execute('select * from USERLIST where USERNAME=?',(UserName,))
UserID=cur.fetchone()

if UserID==None:
    cur.execute('INSERT INTO USERLIST(USERNAME) VALUES(?)',(UserName,))
    print('Welcome ',UserName,' Here is your intial 100 points')
    
else:
    print('Welcome back ',UserName,'. Your total points ',UserID[2])
    
conn.commit()

## All Functions

def Getting_Clue(CmpNumber):
    clue_list.append(range_number(CmpNumber))
    clue_list.append(prime(CmpNumber))
    clue_list.append(written_clues(CmpNumber))
    return clue_list

def range_number(num):
    interval=random.randint(1,9)
    min= (0 if num<=9 else num-interval)
    max= (9 if num<=9 else num+abs(random.randint(7,10)-interval))
    clue='1. I am a '+('single' if digit==1 else 'double')+' digit '+mirror+'and living between ' +str(min)+' and '+str(max)
    return clue

def prime(num):
    whole_prime='2. I am '+('a prime' if is_prime(num)==1 else 'not a prime')+' Number' 
    first_prime=is_prime(int(num/10))
    second_prime=is_prime(int(num%10))
    if digit==1:
        clue=whole_prime
    else:
        if first_prime==second_prime:
            clue=whole_prime+(' and my digits are prime number' if first_prime==1 else ' and my digits are not prime number')
        else:
            clue=whole_prime+' and my first digit is '+('a prime' if first_prime==1 else 'not a prime')+' and my second digit is '+('a prime' if second_prime==1 else ' not a prime')
   
    return clue

def is_prime(num):
    prime=1
    if (num==1)|(num==0):
        prime=0
    for i in range(2,num):
        if num%i==0:
            prime=0
    return prime

def written_clues(num):
    first_Number=(-1 if (digit==1)|(mirror=='mirror number ') else int(num/10))
    second_Number=int(num%10)
    sql=pd.read_sql_query('SELECT * FROM CLUELIST WHERE Number IN (?,?)',conn,params=(first_Number,second_Number))
    df=pd.DataFrame(sql)
    df=df.apply(lambda row:row.replace([' Position',' position'],regex=True,value=(''if first_Number==-1 else(' first' if row['NUMBER']==first_Number else ' second'))),axis=1)
    clue_ids=df.groupby('NUMBER').agg(clue_ids=('CLUEID',lambda clist:random.choice(list(clist))))['clue_ids'].to_list()
    return('3. '+(df[df['CLUEID'].isin(clue_ids)]['CLUE'].values[0])+('' if first_Number==-1 else(' and '+(df[df['CLUEID'].isin(clue_ids)]['CLUE'].values[1]))))

def checking_user_input(GuessNumber,Points_Awarded):
    UserInput=input('\nEnter your answer')
    if int(UserInput)==CmpNumber:
        print('\nHooray! Your guess was correct, and you have been awarded '+str(Points_Awarded)+' points.')    
        User_Total_Point=update_points(Points_Awarded)
        print('With '+str(User_Total_Point[0])+' points total, you are now in the '+('lead' if User_Total_Point[1]== 1 else 'position '+str(User_Total_Point[1])))    
    elif GuessNumber>1:
        GuessNumber=GuessNumber-1
        Points_Awarded=math.ceil(Points_Awarded/2)
        print('\nNo its not,'+str(GuessNumber)+' tries left')
        checking_user_input(GuessNumber,Points_Awarded)
    else:
        print('Better luck next time')
    return

def update_points(points):
    cur.execute('UPDATE USERLIST SET TOTALPOINTS=TOTALPOINTS+? WHERE USERNAME=?',(points,UserName))
    conn.commit()
    User_Total_Point=cur.execute(''' SELECT TOTALPOINTS,RANK FROM(
                                     SELECT *,RANK() OVER(ORDER BY TOTALPOINTS DESC) AS RANK
                                     FROM USERLIST)A WHERE USERNAME=?''',(UserName,)).fetchone()
    return User_Total_Point


Game=True

while Game:
    Total_Guess=3
    Points_Awarded=10
    CmpNumber=random.randint(1,99)
    digit=len(str(CmpNumber))
    mirror=('' if digit==1 else (('mirror number ' if int(CmpNumber/10)==int(CmpNumber%10) else 'but not a mirror number ')))    
    clue_list=list()
    Getting_Clue(CmpNumber)
    print('\n')
    for i in clue_list:
        print(i) 
    checking_user_input(Total_Guess,Points_Awarded)
        
    Game=input('\npress Y to continue enter to leave')
    

    
    
