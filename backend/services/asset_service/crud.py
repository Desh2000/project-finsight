# FinVest | Asset Service | crud.py
# Member 2: Platform Asset & Market Data — all database operations

from sqlalchemy.orm import Session
from models import Asset
from schemas import AssetCreate, AssetUpdate
import uuid
from datetime import datetime, timezone


# ── Seed data for pre-populating the assets table ──
SEED_ASSETS = [
    {"ticker": "BTC", "name": "Bitcoin", "coingecko_id": "bitcoin", "risk_rating": "High", "asset_type": "Crypto",
     "description": "The first and most widely recognized cryptocurrency."},
    {"ticker": "ETH", "name": "Ethereum", "coingecko_id": "ethereum", "risk_rating": "High", "asset_type": "Crypto",
     "description": "A decentralized platform for smart contracts."},
    {"ticker": "SOL", "name": "Solana", "coingecko_id": "solana", "risk_rating": "High", "asset_type": "Crypto",
     "description": "High-performance blockchain for fast transactions."},
    {"ticker": "ADA", "name": "Cardano", "coingecko_id": "cardano", "risk_rating": "Medium", "asset_type": "Crypto",
     "description": "Proof-of-stake blockchain with a research-driven approach."},
    {"ticker": "USDT", "name": "Tether", "coingecko_id": "tether", "risk_rating": "Low", "asset_type": "Crypto",
     "description": "A stablecoin pegged to the US dollar."},
]


def seed_assets(db: Session) -> None:
    """Insert seed assets if the table is empty (check-before-insert pattern)."""
    count = db.query(Asset).count()
    if count > 0:
        return

    now = datetime.now(timezone.utc).isoformat()
    for asset_data in SEED_ASSETS:
        db_asset = Asset(
            id=str(uuid.uuid4()),
            ticker=asset_data["ticker"],
            name=asset_data["name"],
            asset_type=asset_data["asset_type"],
            coingecko_id=asset_data["coingecko_id"],
            description=asset_data["description"],
            risk_rating=asset_data["risk_rating"],
            is_tradeable=True,
            created_at=now,
            updated_at=now,
        )
        db.add(db_asset)
    db.commit()


def create_asset(db: Session, asset_data: AssetCreate) -> Asset:
    """Add a new asset ticker to the platform."""
    now = datetime.now(timezone.utc).isoformat()
    db_asset = Asset(
        id=str(uuid.uuid4()),
        ticker=asset_data.ticker,
        name=asset_data.name,
        asset_type=asset_data.asset_type.value,
        coingecko_id=asset_data.coingecko_id,
        description=asset_data.description,
        risk_rating=asset_data.risk_rating.value,
        is_tradeable=True,
        created_at=now,
        updated_at=now,
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


def get_asset_by_id(db: Session, asset_id: str) -> Asset | None:
    return db.query(Asset).filter(Asset.id == asset_id).first()


def get_asset_by_ticker(db: Session, ticker: str) -> Asset | None:
    return db.query(Asset).filter(Asset.ticker == ticker.upper()).first()


def list_assets(db: Session) -> list[Asset]:
    return db.query(Asset).all()


def update_asset(db: Session, asset_id: str, update_data: AssetUpdate) -> Asset | None:
    db_asset = get_asset_by_id(db, asset_id)
    if not db_asset:
        return None

    update_dict = update_data.model_dump(exclude_unset=True)
    # Convert enums to strings
    if "risk_rating" in update_dict and update_dict["risk_rating"] is not None:
        update_dict["risk_rating"] = update_dict["risk_rating"].value
    if "asset_type" in update_dict and update_dict["asset_type"] is not None:
        update_dict["asset_type"] = update_dict["asset_type"].value

    for field, value in update_dict.items():
        setattr(db_asset, field, value)

    db_asset.updated_at = datetime.now(timezone.utc).isoformat()
    db.commit()
    db.refresh(db_asset)
    return db_asset


def toggle_tradeable(db: Session, asset_id: str, is_tradeable: bool) -> Asset | None:
    db_asset = get_asset_by_id(db, asset_id)
    if not db_asset:
        return None
    db_asset.is_tradeable = is_tradeable
    db_asset.updated_at = datetime.now(timezone.utc).isoformat()
    db.commit()
    db.refresh(db_asset)
    return db_asset


def delete_asset(db: Session, asset_id: str) -> tuple[bool, str | None]:
    """
    Hard-delete an asset. In a real system we would check for transactions
    referencing this asset. Since transaction_service has its own DB, we
    simply delete here. Returns (success, error_message).
    """
    db_asset = get_asset_by_id(db, asset_id)
    if not db_asset:
        return False, "Asset not found"
    db.delete(db_asset)
    db.commit()
    return True, None
