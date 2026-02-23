from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Integer, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)

    # 1 -> N
    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
        }


class Planet(db.Model):
    __tablename__ = "planet"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    climate: Mapped[str | None] = mapped_column(String(120), nullable=True)
    terrain: Mapped[str | None] = mapped_column(String(120), nullable=True)
    population: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # 1 -> N (favoritos que apuntan a este planeta)
    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite",
        back_populates="planet",
        cascade="all, delete-orphan"
    )

    # 1 -> N (personajes cuyo homeworld es este planeta)
    residents: Mapped[list["People"]] = relationship(
        "People",
        back_populates="homeworld"
    )

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "population": self.population
        }


class People(db.Model):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    gender: Mapped[str | None] = mapped_column(String(40), nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mass: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # N -> 1 (muchos personajes pueden compartir homeworld)
    homeworld_id: Mapped[int | None] = mapped_column(ForeignKey("planet.id"), nullable=True)
    homeworld: Mapped["Planet"] = relationship("Planet", back_populates="residents")

    # 1 -> N (favoritos que apuntan a este personaje)
    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite",
        back_populates="people",
        cascade="all, delete-orphan"
    )

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "height": self.height,
            "mass": self.mass,
            "homeworld_id": self.homeworld_id
        }


class Favorite(db.Model):
    """
    Favoritos del usuario.
    Un favorito puede apuntar a un planeta O a un personaje (People).
    """
    __tablename__ = "favorite"

    __table_args__ = (
        # Evita duplicados por usuario:
        UniqueConstraint("user_id", "planet_id", name="uq_user_planet_fav"),
        UniqueConstraint("user_id", "people_id", name="uq_user_people_fav"),

        # Obliga a que exista AL MENOS uno (planet_id o people_id)
        CheckConstraint("(planet_id IS NOT NULL) OR (people_id IS NOT NULL)", name="ck_fav_has_target"),

        # Evita que estén ambos a la vez (opcional pero recomendado)
        CheckConstraint("NOT (planet_id IS NOT NULL AND people_id IS NOT NULL)", name="ck_fav_only_one_target"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    planet_id: Mapped[int | None] = mapped_column(ForeignKey("planet.id"), nullable=True)
    people_id: Mapped[int | None] = mapped_column(ForeignKey("people.id"), nullable=True)

    # N -> 1
    user: Mapped["User"] = relationship("User", back_populates="favorites")
    planet: Mapped["Planet"] = relationship("Planet", back_populates="favorites")
    people: Mapped["People"] = relationship("People", back_populates="favorites")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "people_id": self.people_id
        }