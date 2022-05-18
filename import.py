import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO book (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                   {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Added {title} by {author} with ISBN {isbn} which was published in {year}.")
    db.commit()


# Improved code for uploading book.csv to database
def main_v2():
    with open("books.csv") as f:
        reader = csv.reader(f)
        for isbn, title, author, year in reader:

            # Skip the first line
            if isbn == "isbn":
                continue

            db.execute(
                "INSERT INTO book (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                {
                    "isbn": isbn,
                    "title": title,
                    "author": author,
                    "year": year
                }
            )
            print(f"Added {title} by {author} with ISBN {isbn} which was published in {year}.")
        db.commit()


if __name__ == "__main__":
    main_v2()
