from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Contact, User
from schemas import ContactCreate, ContactResponse
from services.auth import get_current_user

router = APIRouter(
    prefix="/contacts",
    tags=["Contacts"]
)


# CREATE
@router.post("/", response_model=ContactResponse)
def create_contact(
    contact: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_contact = (
        db.query(Contact)
        .filter(
            Contact.email == contact.email,
            Contact.user_id == current_user.id
        )
        .first()
    )

    if existing_contact:
        raise HTTPException(
            status_code=409,
            detail="Contact with this email already exists"
        )

    new_contact = Contact(
        **contact.model_dump(),
        user_id=current_user.id
    )

    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)

    return new_contact


# READ ALL
@router.get("/", response_model=list[ContactResponse])
def get_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Contact)
        .filter(Contact.user_id == current_user.id)
        .all()
    )


# SEARCH
@router.get("/search/", response_model=list[ContactResponse])
def search_contacts(
    first_name: str | None = Query(None),
    last_name: str | None = Query(None),
    email: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = (
        db.query(Contact)
        .filter(Contact.user_id == current_user.id)
    )

    if first_name:
        query = query.filter(
            Contact.first_name.ilike(f"%{first_name}%")
        )

    if last_name:
        query = query.filter(
            Contact.last_name.ilike(f"%{last_name}%")
        )

    if email:
        query = query.filter(
            Contact.email.ilike(f"%{email}%")
        )

    return query.all()


# BIRTHDAYS NEXT 7 DAYS
@router.get("/birthdays/", response_model=list[ContactResponse])
def upcoming_birthdays(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contacts = (
        db.query(Contact)
        .filter(Contact.user_id == current_user.id)
        .all()
    )

    today = date.today()
    next_week = today + timedelta(days=7)

    result = []

    for contact in contacts:
        birthday_this_year = contact.birthday.replace(
            year=today.year
        )

        if today <= birthday_this_year <= next_week:
            result.append(contact)

    return result


# READ ONE
@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact = (
        db.query(Contact)
        .filter(
            Contact.id == contact_id,
            Contact.user_id == current_user.id
        )
        .first()
    )

    if not contact:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )

    return contact


# UPDATE
@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int,
    contact_data: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact = (
        db.query(Contact)
        .filter(
            Contact.id == contact_id,
            Contact.user_id == current_user.id
        )
        .first()
    )

    if not contact:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )

    for key, value in contact_data.model_dump().items():
        setattr(contact, key, value)

    db.commit()
    db.refresh(contact)

    return contact


# DELETE
@router.delete("/{contact_id}")
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact = (
        db.query(Contact)
        .filter(
            Contact.id == contact_id,
            Contact.user_id == current_user.id
        )
        .first()
    )

    if not contact:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )

    db.delete(contact)
    db.commit()

    return {
        "message": "Contact deleted successfully"
    }
