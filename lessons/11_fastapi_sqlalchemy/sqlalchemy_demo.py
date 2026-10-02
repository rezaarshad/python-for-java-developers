"""Lesson 11 demo: SQLAlchemy 2.0 ORM with SQLite (in memory).

Run: uv run python lessons/11_fastapi_sqlalchemy/sqlalchemy_demo.py
"""

from datetime import datetime

from sqlalchemy import ForeignKey, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    notes: Mapped[list["Note"]] = relationship(back_populates="author", cascade="all, delete-orphan")  # @OneToMany

    def __repr__(self) -> str:
        return f"Author({self.id}, {self.name!r})"


class Note(Base):
    __tablename__ = "notes"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    body: Mapped[str] = mapped_column(default="")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped[Author] = relationship(back_populates="notes")                                  # @ManyToOne

    def __repr__(self) -> str:
        return f"Note({self.id}, {self.title!r})"


engine = create_engine("sqlite://", echo=False)      # "sqlite://" = in-memory; set echo=True to see the SQL
Base.metadata.create_all(engine)

with Session(engine) as session:
    reza = Author(name="Reza")
    ana = Author(name="Ana")
    reza.notes = [Note(title="RAG", body="retrieval"), Note(title="FastAPI", body="type hints everywhere")]
    ana.notes.append(Note(title="Pandas", body="dataframes"))
    session.add_all([reza, ana])
    session.commit()                                  # INSERTs happen here (unit of work, like JPA)

    # SELECT ... WHERE ... ORDER BY
    stmt = select(Note).where(Note.body.ilike("%e%")).order_by(Note.title)
    print("ilike:", session.scalars(stmt).all())

    # find by id
    print("get:", session.get(Note, 1), session.get(Note, 999))

    # JOIN
    stmt = select(Note.title, Author.name).join(Note.author).where(Author.name == "Reza")
    print("join:", session.execute(stmt).all())

    # GROUP BY
    stmt = select(Author.name, func.count(Note.id)).join(Author.notes).group_by(Author.name)
    print("count per author:", dict(session.execute(stmt).all()))

    # Navigate relationships (lazy loading, like JPA)
    print("reza's notes:", [n.title for n in reza.notes], "| author of Pandas:", session.get(Note, 3).author)

    # UPDATE through dirty checking
    note = session.get(Note, 1)
    note.title = "RAG (updated)"
    session.commit()
    print("updated:", session.get(Note, 1))

    # DELETE with cascade
    session.delete(ana)
    session.commit()
    print("after delete:", session.scalars(select(Note)).all())
