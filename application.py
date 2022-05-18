import os

from flask import Flask, session, render_template , request
import requests
import json
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from passlib.hash import sha256_crypt


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL_V2"):
    raise RuntimeError("DATABASE_URL is not set")


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


engine = create_engine(os.getenv("DATABASE_URL_V2"))
db = scoped_session(sessionmaker(bind=engine))



@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "POST":

        m_q = request.form.get('search') 
        search_request = True
        
        if m_q == "":
            if session.get("user_id") is None or session.get("user_id") == [] :
                session["user_id"] = []
                l= False
                
                return render_template("home.html", l=l, m_input=m_q, a = 1 , b=50, search_request=search_request ,)
            else:
                u_id = session.get("user_id")
                name = db.execute("SELECT username FROM users WHERE id = :u_id", {"u_id":u_id}).fetchone()[0]  
                l= True
                return render_template("home.html", l=l , name=name , a=1 , b=50, search_request=search_request)


        books = db.execute("SELECT book.id, title, author, year , isbn ,AVG(review.score) as rate, Count(review.msg) as comm FROM book FULL OUTER JOIN review ON review.book_id = book.id WHERE title LIKE :m_q OR author LIKE :m_q OR year LIKE :m_q OR isbn LIKE :m_q GROUP BY book.id ORDER BY book.id", {"m_q":f"%{m_q}%"})
        mList = db.execute("SELECT isbn FROM book WHERE title LIKE :m_q OR author LIKE :m_q OR year LIKE :m_q OR isbn LIKE :m_q",  {"m_q":f"%{m_q}%"}).fetchall()
        
        if books.fetchall() ==[]:
            if session.get("user_id") is None or session.get("user_id") == []:
                session["user_id"] = []
                l = False

                return render_template("home.html", l=l, m_input=m_q, a=1, b=50, search_request=search_request, )
        else:
            u_id = session.get("user_id")
            name = db.execute("SELECT username FROM users WHERE id = :u_id", {"u_id": u_id}).fetchone()[0]
            l = True
            return render_template("home.html", l=l, name=name, a=1, b=50, search_request=search_request)
        
        astring = ""

        for m in mList:
            a = f"{m}"
            astring = astring + "," + a[2:-3]

        muri = f"https://www.goodreads.com/book/review_counts.json?isbns={astring[1:]}"
        

        mGoodData = requests.get(muri).json()["books"]
        if session.get("user_id") is None or session.get("user_id") == [] :
            session["user_id"] = []
            l= False
            
            return render_template("home.html", books=books, l=l, m_input=m_q, a = 1 , b=50, mGoodData=mGoodData)
        else:
            u_id = session.get("user_id")
            name = db.execute("SELECT username FROM users WHERE id = :u_id", {"u_id":u_id}).fetchone()[0]  
            l= True
            return render_template("home.html", books=books, l =l , name=name, m_input=m_q, a = 1 , b=50, mGoodData=mGoodData)


    

        if books is None :
            return "Nothing Found"

    else:
        search_request = False 
        if session.get("user_id") is None or session.get("user_id") == [] :
            session["user_id"] = []
            books = db.execute("SELECT book.id, title, author, year , isbn ,AVG(review.score) as rate, Count(review.msg) as comm FROM book FULL OUTER JOIN review ON review.book_id = book.id WHERE book.id BETWEEN 2 AND 51 GROUP BY book.id ORDER BY book.id").fetchall() 
            l= False
            mList = db.execute("SELECT isbn FROM book WHERE book.id BETWEEN 2 AND 51").fetchall()
            
            astring = ""

            for m in mList:
                a = f"{m}"
                astring = astring + "," + a[2:-3]

            muri = f"https://www.goodreads.com/book/review_counts.json?isbns={astring[1:]}"
            print(muri)

            mGoodData = requests.get(muri).json()["books"]

            return render_template("home.html", books=books, l= l , a = 1 , b=50 , search_request=search_request , mGoodData=mGoodData)
        elif session.get("user_id") !=[]:
            try:
                u_id = session.get("user_id")
                name = db.execute("SELECT username FROM users WHERE id = :u_id", {"u_id":u_id}).fetchone()[0]  

                books = db.execute("SELECT book.id, title, author, year , isbn ,AVG(review.score) as rate, Count(review.msg) as comm FROM book FULL OUTER JOIN review ON review.book_id = book.id WHERE book.id BETWEEN 2 AND 51 GROUP BY book.id ORDER BY book.id ").fetchall()  
                l = True

                mList = db.execute("SELECT isbn FROM book WHERE book.id BETWEEN 2 AND 51").fetchall()
            
                astring = ""

                for m in mList:
                    a = f"{m}"
                    astring = astring + "," + a[2:-3]

                muri = f"https://www.goodreads.com/book/review_counts.json?isbns={astring[1:]}"
                print(muri)

                mGoodData = requests.get(muri).json()["books"]
                return render_template("home.html", books=books, name=name, l=l, a = 1 , b=50, search_request=search_request, mGoodData=mGoodData)    
            except:
                session["user_id"] = []
                return render_template("toast2.html", message_body="Something Went Wrong", message_title="Error", error="True")

@app.route("/<int:a>-<int:b>", methods=['GET', 'POST'])
def index_range(a, b ):


    a = int(a) 
    b = int(b) 
    books = db.execute(F"SELECT book.id, title, author, year , isbn ,AVG(review.score) as rate, Count(review.msg) as comm FROM book FULL OUTER JOIN review ON review.book_id = book.id WHERE book.id BETWEEN :a AND :b  GROUP BY book.id ORDER BY book.id ", {"a":a, "b":b}).fetchall()  
  
    mList = db.execute("SELECT isbn FROM book WHERE id between :a and :b",  {"a":a, "b":b}).fetchall()
        
    astring = ""

    for m in mList:
        x = f"{m}"
        astring = astring + "," + x[2:-3]

    muri = f"https://www.goodreads.com/book/review_counts.json?isbns={astring[1:]}"
    

    mGoodData = requests.get(muri).json()["books"]

    if session.get("user_id") is None or session.get("user_id") == [] :
        session["user_id"] = []
        l= False
        return render_template("home.html", books=books, l= l , a=a, b=b , search_request=False, mGoodData=mGoodData )
    elif session.get("user_id") !=[]:
        try:
            u_id = session.get("user_id")
            name = db.execute("SELECT username FROM users WHERE id = :u_id", {"u_id":u_id}).fetchone()[0]  

            l = True
            return render_template("home.html", books=books, name=name, l=l, a = a , b=b, search_request=False, mGoodData=mGoodData )    
        except:
            session["user_id"] = []
            return render_template("toast2.html", message_body="Something Went Wrong", message_title="Error", error="True")


@app.route("/isbn-<string:isbn__>", methods=['GET', 'POST'])
def book_view(isbn__):
    if request.method == "POST":
        score = int(request.form.get('score'))
        msg = request.form.get('msg')
        user_id = session.get("user_id")
        book_id = db.execute("SELECT id FROM book WHERE isbn = :isbn", {"isbn":isbn__}).fetchone()[0]

        justSay = False

        mUsers = db.execute("SELECT user_id FROM review WHERE book_id = :book_id", {"book_id":book_id}).fetchall()
        print(mUsers)
        for a_user in mUsers:
            print(a_user.user_id)
            if user_id == a_user.user_id:
                justSay = True

       
        if justSay == False:
            db.execute("INSERT INTO review (book_id, user_id, score , msg) VALUES (:book_id, :user_id, :score , :msg)", {"book_id":book_id, "user_id":user_id , "score":score, "msg":msg})
            db.commit()

            name = db.execute("SELECT username FROM users WHERE id = :u_id", {"u_id":user_id}).fetchone()[0]  
            l= True
            mBooks = books = db.execute("SELECT book.id, title, author, year , isbn ,AVG(review.score) as rate, Count(review.msg) as comm FROM book FULL OUTER JOIN review ON review.book_id = book.id WHERE isbn = :m_isbn GROUP BY book.id ORDER BY book.id", {"m_isbn":isbn__}).fetchall() 
            mComments = db.execute("SELECT username , msg , score FROM review FULL OUTER JOIN users ON users.id = review.user_id FULL OUTER JOIN book ON book.id=review.book_id WHERE book.isbn = :isbn  LIMIT 10", {"isbn" : isbn__})
            mGoodData = requests.get("https://www.goodreads.com/book/review_counts.json", params={"isbns": isbn__}).json()["books"][0]
            return render_template("book.html",  l =l , name=name, mBooks=mBooks, mComments=mComments, mGoodData=mGoodData)
        else:
            return render_template("toast2.html", error="True", message_body="You can comment more than once", message_title="Error")
        

    if session.get("user_id") is None or session.get("user_id") == [] :
        session["user_id"] = []
        l= False

        mBooks = db.execute("SELECT book.id, title, author, year , isbn ,AVG(review.score) as rate, Count(review.msg) as comm FROM book FULL OUTER JOIN review ON review.book_id = book.id WHERE isbn = :m_isbn GROUP BY book.id ORDER BY book.id", {"m_isbn":isbn__}).fetchall() 
        mComments = db.execute("SELECT username , msg , score FROM review FULL OUTER JOIN users ON users.id = review.user_id FULL OUTER JOIN book ON book.id=review.book_id WHERE book.isbn = :isbn  LIMIT 10", {"isbn" : isbn__})

        mGoodData = requests.get("https://www.goodreads.com/book/review_counts.json", params={"isbns": isbn__}).json()["books"][0]

        return render_template("book.html", l=l  , mBooks=mBooks, mComments=mComments, mGoodData=mGoodData)
    else:
        u_id = session.get("user_id")
        name = db.execute("SELECT username FROM users WHERE id = :u_id", {"u_id":u_id}).fetchone()[0]  
        l= True

        mBooks = db.execute("SELECT book.id, title, author, year , isbn ,AVG(review.score) as rate, Count(review.msg) as comm FROM book FULL OUTER JOIN review ON review.book_id = book.id WHERE isbn = :m_isbn GROUP BY book.id ORDER BY book.id", {"m_isbn":isbn__}).fetchall() 
        mComments = db.execute("SELECT username , msg , score FROM review FULL OUTER JOIN users ON users.id = review.user_id FULL OUTER JOIN book ON book.id=review.book_id WHERE book.isbn = :isbn  LIMIT 10", {"isbn" : isbn__})

        mGoodData = requests.get("https://www.goodreads.com/book/review_counts.json", params={"isbns": isbn__}).json()["books"][0]

        return render_template("book.html",  l =l , name=name, mBooks=mBooks, mComments=mComments, mGoodData=mGoodData)

@app.route("/login")
def login():
    
    if session.get("user_id") !=[]:
        u_id = session.get("user_id")
        name = db.execute("SELECT username FROM users WHERE id = :u_id", {"u_id":u_id}).fetchone()[0]  
        return render_template("logout.html", name=name)

    else :
        return render_template("login.html")

@app.route("/logout_sucess", methods=['post'])
def logout_sucess():
    session["user_id"] = []
    return render_template("toast2.html", message_title="Logoed out", message_body="Sucessfull Logout", REDIRECT="True")    

@app.route("/login_sucess" , methods=['post'])
def login_sucess():

    username = request.form.get("username")
    passw = request.form.get("pass")

    check_username = db.execute("SELECT username FROM users WHERE username = :username", {"username": username}).fetchone()

    if check_username is not None:
        res_pass = db.execute("SELECT password FROM users WHERE username = :username ", {"username":username}).fetchone()
        loged = sha256_crypt.verify(passw  + username, res_pass[0])

        if loged == True:
            session["user_id"] = db.execute("SELECT id FROM users WHERE username = :username ", {"username":username}).fetchone()[0]     

        return render_template('toast.html', loged=loged)
    else:
        return render_template("toast2.html", message_body=f"{username} is not registered. Please Register", nessage_title="Not Registered.", error="True")

@app.route("/register")
def register():

    if session.get("user_id") !=[]:
        u_id = session.get("user_id")
        name = db.execute("SELECT username FROM users WHERE id = :u_id", {"u_id":u_id}).fetchone()[0]  
        return render_template("logout.html", name=name)
    else :
        return render_template("register.html")

@app.route("/registered", methods=['POST'])
def registered():

    email = (request.form.get("email"))
    passw = (request.form.get("pass"))

 

    name = (request.form.get("name"))
    username = ( request.form.get("username"))

    check_username = db.execute("SELECT username FROM users WHERE username = :username", {"username": username}).fetchone()

    if check_username is None:
        password_hashed = sha256_crypt.encrypt(passw  + username)
        db.execute("INSERT INTO users (name, username, email, password) VALUES (:name , :username, :email, :password)",{"name":name, "username":username, "email":email, "password":password_hashed})
        db.commit()

    
        if session["user_id"] is None:
            session["user_id"] =[]

        session["user_id"] = db.execute("SELECT id FROM users WHERE username = :username ", {"username":username}).fetchone()[0]     
        return render_template("toast2.html", message_title="Regestered", message_body=f" Welcome {name}! You are registered scuessfully with username {username}", REDIRECT="True")
    else:
        return render_template("toast2.html",message_title="Error", message_body="An account is registered with this username. Please try different username", error="True")

@app.route("/api/<string:isbn>")
def api(isbn):
    
    books = db.execute("SELECT title, author, cast(year as integer) , isbn ,cast(AVG(review.score) as varchar(4)) as average_score, Count(review.msg) as review_count FROM book FULL OUTER JOIN review ON review.book_id = book.id WHERE isbn = :m_q GROUP BY book.id ORDER BY book.id", {"m_q":isbn}).fetchall()
        
    test = json.dumps([dict(r) for r in books])

    if test == "[]" :
        return """{"error" : 404}""", 404

    return f"{test[1:-1]}"



if __name__ == '__main__':
   app.run()
