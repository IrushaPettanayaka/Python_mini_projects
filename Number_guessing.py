import random

ran_num = random.randint(1,100)
attempt_count = 0
guess = int(input("Guess the number (Between 1 and 100): "))
attempt_count += 1
if not isinstance(guess,int):
    print("Guess should be an integer")
if guess > ran_num:
    print('Too high! Try again')
elif guess < ran_num:
    print("Too low! Try again")
elif guess > 100 or guess < 1:
    print('Invalid input')
elif guess == ran_num:
    print(f"Congradulations! You guessed the number in {attempt_count} attemps")