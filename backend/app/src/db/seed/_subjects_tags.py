"""Seed subjects and tags."""

from db.seed.constants import (
    SUBJ_CHEMISTRY,
    SUBJ_ENGLISH,
    SUBJ_HISTORY,
    SUBJ_MATH,
    SUBJ_PHYSICS,
    SUBJ_RUSSIAN,
    TAG_EGE,
    TAG_EXPERIENCED,
    TAG_INDIVIDUAL,
    TAG_INTERACTIVE,
    TAG_PATIENT,
    TAG_REMOTE,
    TAG_STRICT,
    TAG_YOUNG,
)
from models.tables import Subject, Tag
from sqlalchemy.ext.asyncio import AsyncSession


def seed_subjects_and_tags(session: AsyncSession) -> None:
    subjects = [
        Subject(id=SUBJ_MATH, name="Математика"),
        Subject(id=SUBJ_PHYSICS, name="Физика"),
        Subject(id=SUBJ_RUSSIAN, name="Русский язык"),
        Subject(id=SUBJ_ENGLISH, name="Английский язык"),
        Subject(id=SUBJ_CHEMISTRY, name="Химия"),
        Subject(id=SUBJ_HISTORY, name="История"),
    ]
    session.add_all(subjects)

    tags = [
        Tag(id=TAG_PATIENT, name="Терпеливый"),
        Tag(id=TAG_INTERACTIVE, name="Интерактивный"),
        Tag(id=TAG_STRICT, name="Строгий"),
        Tag(id=TAG_EXPERIENCED, name="Опытный"),
        Tag(id=TAG_YOUNG, name="Молодой специалист"),
        Tag(id=TAG_REMOTE, name="Дистанционно"),
        Tag(id=TAG_INDIVIDUAL, name="Индивидуальный подход"),
        Tag(id=TAG_EGE, name="Подготовка к ЕГЭ"),
    ]
    session.add_all(tags)
