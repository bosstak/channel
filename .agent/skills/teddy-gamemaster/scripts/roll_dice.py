import random
import sys

dice_roll = random.randint(1, 20)
print(f"🎲 주사위 결과: {dice_roll}")

if dice_roll == 20:
    print("STATUS: CRITICAL SUCCESS (대성공! 기적이 일어납니다)")
elif dice_roll >= 12:
    print("STATUS: SUCCESS (성공! 위기를 넘깁니다)")
elif dice_roll > 1:
    print("STATUS: FAILURE (실패... 곤란해집니다)")
else:
    print("STATUS: CRITICAL FAILURE (대실패! 끔찍한 일이 벌어집니다)")