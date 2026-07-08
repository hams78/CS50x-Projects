
import turtle
import time
import random

# إعدادات سرعة اللعبة والنتيجة
delay = 0.1
score = 0
high_score = 0

# 1. إعداد شاشة اللعبة (Screen Setup)
window = turtle.Screen()
window.title("Classic Snake Game by Hams for CS50x")
window.bgcolor("black")
window.setup(width=600, height=600)
window.tracer(0) # يوقف تحديث الشاشة التلقائي لنجعل الحركة ناعمة

# ررسم حدود منطقة اللعب(Border)
# ==========================================
border_pen = turtle.Turtle()
border_pen.speed(0)
border_pen.color("white") # لون الحواف أبيض
border_pen.penup()
border_pen.hideturtle() # إخفاء السهم الخاص بالرسم
border_pen.goto(-300, 300) # الذهاب لأعلى اليسار
border_pen.pendown()
border_pen.pensize(3) # سمك الخط

# رسم المربع المحيط (600x600)
for _ in range(4):
    border_pen.forward(600)
    border_pen.right(90)
# 2. رأس الثعبان (Snake Head)
head = turtle.Turtle()
head.speed(0)
head.shape("square")
head.color("green")
head.penup()
head.goto(0, 0)
head.direction = "stop"

# 3. طعام الثعبان (Snake Food)
food = turtle.Turtle()
food.speed(0)
food.shape("circle")
food.color("red")
food.penup()
food.goto(0, 100)

# مصفوفة لتخزين أجزاء جسم الثعبان الإضافية
segments = []

# 4. لوحة حساب النتيجة على الشاشة (Scoreboard)
pen = turtle.Turtle()
pen.speed(0)
pen.shape("square")
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0, 260)
pen.write("Score: 0  High Score: 0", align="center", font=("Courier", 24, "normal"))

# 5. دالات لتوجيه حركة رأس الثعبان بأسهم الكيبورد
def go_up():
    if head.direction != "down":
        head.direction = "up"

def go_down():
    if head.direction != "up":
        head.direction = "down"

def go_left():
    if head.direction != "right":
        head.direction = "left"

def go_right():
    if head.direction != "left":
        head.direction = "right"

# دالة تحريك الثعبان بناءً على الاتجاه الحالي
def move():
    if head.direction == "up":
        y = head.ycor()
        head.sety(y + 20)
    if head.direction == "down":
        y = head.ycor()
        head.sety(y - 20)
    if head.direction == "left":
        x = head.xcor()
        head.setx(x - 20)
    if head.direction == "right":
        x = head.xcor()
        head.setx(x + 20)

# 6. ربط أزرار الكيبورد باللعبة (Keyboard Bindings)
window.listen()
window.onkeypress(go_up, "Up")
window.onkeypress(go_down, "Down")
window.onkeypress(go_left, "Left")
window.onkeypress(go_right, "Right")

# 7. الحلقة الأساسية لتشغيل اللعبة (Main Game Loop)
while True:
    window.update()

    # أولاً: التحقق من الاصطدام بالحائط (خسارة وإعادة تعيين اللعبة)
    if head.xcor() > 290 or head.xcor() < -290 or head.ycor() > 290 or head.ycor() < -290:
        time.sleep(1)
        head.goto(0, 0)
        head.direction = "stop"
        
        # إخفاء أجزاء الجسم القديمة بعيداً عن الشاشة
        for segment in segments:
            segment.goto(1000, 1000)
        segments.clear()
        
        score = 0
        delay = 0.1
        pen.clear()
        pen.write("Score: {}  High Score: {}".format(score, high_score), align="center", font=("Courier", 24, "normal"))

    # ثانياً: التحقق من وصول الثعبان للطعام وأكله
    if head.distance(food) < 20:
        # نقل الطعام إلى مكان عشوائي جديد على الشاشة
        x = random.randint(-280, 280)
        y = random.randint(-280, 280)
        food.goto(x, y)

        # إضافة جزء جديد لجسم الثعبان ولونه أخضر فاتح للتفريق بينه وبين الرأس
        new_segment = turtle.Turtle()
        new_segment.speed(0)
        new_segment.shape("square")
        new_segment.color("lightgreen")
        new_segment.penup()
        segments.append(new_segment)

        # زيادة سرعة اللعبة قليلاً وزيادة النتيجة
        delay -= 0.003
        score += 10

        if score > high_score:
            high_score = score
        
        pen.clear()
        pen.write("Score: {}  High Score: {}".format(score, high_score), align="center", font=("Courier", 24, "normal"))

    # ثالثاً: تحريك أجزاء الجسم لتتبع الرأس بالترتيب العكسي
    for index in range(len(segments)-1, 0, -1):
        x = segments[index-1].xcor()
        y = segments[index-1].ycor()
        segments[index].goto(x, y)

    # جعل أول جزء في الجسم يذهب إلى مكان الرأس السابق مباشرة
    if len(segments) > 0:
        x = head.xcor()
        y = head.ycor()
        segments[0].goto(x, y)

    move()

    # رابعاً: التحقق من اصطدام رأس الثعبان بجسمه (خسارة وإعادة تعيين)
    for segment in segments:
        if segment.distance(head) < 20:
            time.sleep(1)
            head.goto(0, 0)
            head.direction = "stop"
            for seg in segments:
                seg.goto(1000, 1000)
            segments.clear()
            score = 0
            delay = 0.1
            pen.clear()
            pen.write("Score: {}  High Score: {}".format(score, high_score), align="center", font=("Courier", 24, "normal"))

    time.sleep(delay)

window.mainloop()

# ACADEMIC HONESTY CITATION:
# I used Gemini AI as an educational assistant to help me understand how to map out 
# the coordinate grid logic using Python's turtle module and to refine the loops 
# that make the body segments follow the snake's head correctly.
