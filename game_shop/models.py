from game_shop import db

owned_games = db.Table(
    "owned_games",
    db.Column("user_id", db.Integer, db.ForeignKey("users._id", ondelete="CASCADE")),
    db.Column("game_id", db.Integer, db.ForeignKey("games._id", ondelete="CASCADE")),
)

class User(db.Model):
    __tablename__ = "users"
    _id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(50), unique=True)
    avatar_img = db.Column(db.String(100))
    role = db.Column(db.String(10), nullable=False, server_default="user")
    my_games = db.relationship("Game", secondary=owned_games, backref="users")
    reviews = db.relationship("Review", backref="user")
    def __init__(self, name, password_hash, email, avatar_img, role):
        self.username = name
        self.password_hash = password_hash
        self.email = email
        self.avatar_img = avatar_img
        self.role = role

class Game(db.Model):
    __tablename__ = "games"
    _id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    desc = db.Column(db.Text)
    cover_img = db.Column(db.String(100))
    qty = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    owners = db.relationship("User", secondary=owned_games, backref="games")
    reviews = db.relationship("Review", backref="game")
    def __init__(self, title, desc, cover_img, qty, price):
        self.title = title
        self.desc = desc
        self.cover_img = cover_img
        self.qty = qty
        self.price = price

class Review(db.Model):
    __tablename__ = "reviews"
    _id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("users._id", ondelete="SET NULL"))
    game_id = db.Column(db.Integer, db.ForeignKey("games._id", ondelete="CASCADE"))
