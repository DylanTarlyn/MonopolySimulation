
import random
import csv
import psycopg2

class board:
    rollList = [] #result of the dice roll
    rollNumber = [] #nummber of rolls
    positionList = [] #postiion on board
    chanceCards = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16] #chance cards
    communityChestCards = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16] #community chest cards

    roll = 0 #number of rolls
    position = 0 #position on board

    CCfreeJailCard = False #community chest free jail card
    chanceFreeJailCard = False #chance free jail card


def updatePosition(total):
    board.positionList.append(board.position)
    board.rollList.append(total)
    board.rollNumber.append(board.roll)

def rollDice():
    board.roll = board.roll+1

    dice1 = random.randint(1,6)
    dice2 = random.randint(1,6)
    total= dice1 + dice2

    board.position = board.position + total

    #check for jail
    if board.position == 30: #go to jail
        updatePosition(total)
        rollJail()
        return
    
    #check for go
    if board.position >40: #when passing go, reset position to 0
        board.position = board.position - 40

    #check for chance and community chest
    if board.position == 7 or board.position == 22 or board.position == 36:
        updatePosition(total) #record they landed on this spot
        chance()
        return
    if board.position == 2 or board.position == 17 or board.position == 33:
        updatePosition(total)
        communityChest()
        return

    updatePosition(total)

def rollJail():
    board.position=10 #jail position

    roll = 0
    inJail = True
    rollJail.rollsToOut = 0

    while inJail:

        #check for get out of jail free card

        if board.CCfreeJailCard == True: #community chest free jail card
            board.CCfreeJailCard = False #remove card
            #put the card back in the deck
            board.communityChestCards.append(2)
            inJail = False #get out of jail
            return

        if board.chanceFreeJailCard == True: #chance free jail card
            board.chanceFreeJailCard = False #remove card
            #put the card back in the deck
            board.chanceCards.append(6)
            inJail = False #get out of jail
            return

        dice1 = random.randint(1,6)
        dice2 = random.randint(1,6)
        total= dice1 + dice2

        board.roll = board.roll + 1
        
        rollJail.rollsToOut +=1

        roll = roll + 1
        if dice1 == dice2:
            updatePosition(total)
            inJail = False
        else:
            updatePosition(total)
            if roll == 3:
                inJail = False

def communityChest():
    board.roll = board.roll+1 # for clarity of roll numbers/elimitate duplicate turn values

    if board.communityChestCards[0] == 1: #advance to go
        board.position = 0 #move player to go

    if board.communityChestCards[0] == 2: #get out of jail free
        #remove card from list
        board.communityChestCards.pop(0) #remove card from list
        board.CCfreeJailCard = True #add card to player
        
    if board.communityChestCards[0] == 3: #go to jail
        board.jailFromCC=True
        rollJail()
    else:
        pass
    #move card to end of list
    board.communityChestCards.append(board.communityChestCards[0])
    board.communityChestCards.pop(0)

    #write players new position
    updatePosition(0)
        

def chance():
    board.roll = board.roll+1 # for clarity of roll numbers/elimitate duplicate turn values
    #1. Advance to Go
    if board.chanceCards[0] == 1:
        board.position = 40 #move player to go
    #2. Advance to Illinois Ave
    if board.chanceCards[0] == 2:
        board.position = 24 #move player to Illinois Ave
    #3. Advance to St. Charles Place
    if board.chanceCards[0] == 3:
        board.position = 11
    #4. Advance token to nearest Utility
    if board.chanceCards[0] == 4:
        if board.position == 7 or board.position == 36:
            board.position = 12
    #5. Advance token to the nearest Railroad
    if board.chanceCards[0] == 5:
        if board.position == 7:
            board.position = 15
        if board.position == 22:
            board.position = 25
        if board.position == 36:
            board.position = 5
    #6. Get out of Jail Free
    if board.chanceCards[0] == 6:
        board.chanceFreeJailCard = True
        board.chanceCards.pop(0)
    #7. Go back 3 spaces
    if board.chanceCards[0] == 7:
        board.position = board.position - 3
    #8. Go to Jail – Go directly to Jail
    if board.chanceCards[0] == 8:
        board.jailFromChance = True
        rollJail()
    #9. Take a trip to Reading Railroad
    if board.chanceCards[0] == 9:
        board.position = 5
    #10. Advance token to Boardwalk
    if board.chanceCards[0] == 10:
        board.position = 39
    # 6 null
    else:
        pass

    #move card to end of list
    board.chanceCards.append(board.chanceCards[0])
    board.chanceCards.pop(0)

    #write players new position
    updatePosition(0)

def main():

    #WRITING TO DATABASE

    try:
        connection = psycopg2.connect(user="postgres",
                                    password="tarlydyl",
                                    host="localhost",
                                    port="5432",
                                    database="Monopoly")
        cursor = connection.cursor()


        for j in range(100000): #number of games to play

            #reset the board
            board.rollList = [] #result of the dice roll
            board.rollNumber = [] #nummber of rolls
            board.positionList = [] #postiion on board
            board.chanceCards = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16] #chance cards
            board.communityChestCards = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16] #community chest cards

            board.roll = 0 #number of rolls
            board.position = 0 #position on board

            board.CCfreeJailCard = False #community chest free jail card
            board.chanceFreeJailCard = False #chance free jail card

            for i in range(35): #Simulate a single average game (not including turns in jail)
                #shuffle the chance and community chest cards
                random.shuffle(board.chanceCards)
                random.shuffle(board.communityChestCards)
                rollDice()

            for i in range(len(board.rollNumber)):
                sqlString = """ INSERT INTO monopoly (rollnumber, rollvalue, position, rollsout) VALUES (%s,%s,%s,%s)"""
                record = (board.rollNumber[i], board.rollList[i], board.positionList[i],rollJail.rollsToOut)
                cursor.execute(sqlString, record)

                rollJail.rollsToOut = 0
            j = j + 1 #start next game

        connection.commit()
        count = cursor.rowcount
        print(count, "Record inserted successfully into mobile table")

    except (Exception, psycopg2.Error) as error:
        print("Failed to insert record into mobile table", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

    #WRITING TO A CSV FILE

    # with open('game1.csv', 'w',newline='') as csvfile:
    #     fieldnames = ['rollNumber', 'rollValue', 'position', 'rollsToOut']
    #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #     writer.writeheader()

        # for j in range(1000): #number of games to play

        #     #reset the board
        #     board.rollList = [] #result of the dice roll
        #     board.rollNumber = [] #nummber of rolls
        #     board.positionList = [] #postiion on board
        #     board.chanceCards = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16] #chance cards
        #     board.communityChestCards = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16] #community chest cards

        #     board.roll = 0 #number of rolls
        #     board.position = 0 #position on board

        #     board.CCfreeJailCard = False #community chest free jail card
        #     board.chanceFreeJailCard = False #chance free jail card

        #     for i in range(35): #Simulate a single average game (not including turns in jail)
        #         #shuffle the chance and community chest cards
        #         random.shuffle(board.chanceCards)
        #         random.shuffle(board.communityChestCards)
        #         rollDice()

        #     for i in range(len(board.rollNumber)):
        #         #print(board.rollNumber[i], board.rollList[i], board.positionList[i])
        #         writer.writerow({'rollNumber': board.rollNumber[i], 
        #         'rollValue': board.rollList[i], 
        #         'position': board.positionList[i],
        #         'rollsToOut': rollJail.rollsToOut})

        #         rollJail.rollsToOut = 0
        #     j = j + 1 #start next game

        # csvfile.close()
        # print("done")
        return

main()