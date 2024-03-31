from game_shop import db, app
from game_shop.models import User, Game, Review
from game_shop.routes import bcrypt

print("Trying to create database...")
try:
    with app.app_context():
        db.drop_all()
        db.create_all()

        user1 = User("admin", password_hash=bcrypt.generate_password_hash("Pass.123").decode("utf-8"), email="admin@test.com", avatar_img="", role="admin")
        user2 = User("Marko", password_hash=bcrypt.generate_password_hash("Pass.123").decode("utf-8"), email="marko@test.com", avatar_img="", role="user")
        user3 = User("Jovan", password_hash=bcrypt.generate_password_hash("Pass.123").decode("utf-8"), email="jovan@test.com", avatar_img="", role="user")

        game1 = Game(title="CoD", desc="Massive shooter", cover_img="cod.jpeg", qty=512, price=69.99)
        game2 = Game(title="WoW", desc="MMORPG of the ages! Don't miss out!!!", cover_img="wow.jpg", qty=512, price=169.99)
        game3 = Game(title="Super Mario", desc="Yeah, a classic. You can never go wrong with this one!", cover_img="mario.jpg", qty=512, price=13.50)
        game4 = Game(title="World of Tanks", desc="A lifelike war simulation. Take the role of a tank, and make the Nazis proud!", cover_img="wod.jpg", qty=512, price=9.99)

        review1 = Review(rating=4, review_text="I enjoyed this game a lot! WoW rocks!!!")
        review2 = Review(rating=1, review_text="WoW is a terrible game. Please delete")
        review3 = Review(rating=5, review_text="Super mario is such a classic. 10/10 (or, in this case, 5/5 :P)")
        review4 = Review(rating=3, review_text="WoD is so realistic. I feel like I'm actually in a battle. Just better, because I'm not really scared!")

        user1.my_games.append(game1)
        user1.my_games.append(game4)
        user1.my_games.append(game2)
        user2.my_games.append(game1)

        user1.reviews.append(review1)
        game2.reviews.append(review1)
        user3.reviews.append(review2)
        game2.reviews.append(review2)
        user3.reviews.append(review3)
        game3.reviews.append(review3)
        user3.reviews.append(review4)
        game4.reviews.append(review4)

        db.session.add_all([user1, user2, user3])
        db.session.add_all([game1, game2, game3, game4])

        db.session.commit()
        # pw = bcrypt.generate_password_hash("Pass.123").decode("utf-8")
        # db.session.add(User("admin", pw, "admin@test.com", "", "admin"))
        # db.session.commit()
    print("Successfully created the db!")
except Exception as e:
    print(e)
