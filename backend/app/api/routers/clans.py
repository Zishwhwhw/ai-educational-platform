# ==========================================
# File: routers/clans.py
# Description: Clan / Group rating routes
# Author: AI Agent
# Created: 2026-08-02
# ==========================================


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api.deps import CurrentUser
from app.db.session import get_db

router = APIRouter(prefix="/clans", tags=["clans"])


@router.get("/", response_model=list[schemas.ClanResponse])
def list_clans(db: Session = Depends(get_db)):
    return db.query(models.Clan).order_by(models.Clan.total_points.desc()).all()


@router.post("/", response_model=schemas.ClanResponse)
def create_clan(clan: schemas.ClanCreate, current_user: CurrentUser, db: Session = Depends(get_db)):
    user = current_user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.clan_id:
        raise HTTPException(status_code=400, detail="User already in a clan")

    new_clan = models.Clan(name=clan.name, description=clan.description)
    db.add(new_clan)
    db.commit()
    db.refresh(new_clan)

    member = models.ClanMember(clan_id=new_clan.id, user_id=user.id)
    user.clan_id = new_clan.id
    db.add(member)
    db.commit()
    return new_clan


@router.post("/{clan_id}/join")
def join_clan(clan_id: int, current_user: CurrentUser, db: Session = Depends(get_db)):
    clan = db.query(models.Clan).filter(models.Clan.id == clan_id).first()
    if not clan:
        raise HTTPException(status_code=404, detail="Clan not found")

    count = db.query(models.ClanMember).filter(models.ClanMember.clan_id == clan_id).count()
    if count >= clan.max_members:
        raise HTTPException(status_code=400, detail="Clan is full (max 5 members)")

    user = current_user
    if user.clan_id:
        raise HTTPException(status_code=400, detail="Already in a clan")

    member = models.ClanMember(clan_id=clan_id, user_id=user.id)
    user.clan_id = clan_id
    db.add(member)
    db.commit()
    return {"message": f"Successfully joined clan {clan.name}"}
