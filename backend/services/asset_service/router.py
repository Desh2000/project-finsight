# FinVest | Asset Service | router.py
# Member 2: Platform Asset & Market Data — FastAPI route definitions

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import (
    AssetCreate, AssetUpdate, TradeableToggle,
    AssetResponse, AssetEnrichedResponse, AssetListResponse,
)
import crud
from external import fetch_live_prices, is_data_stale
from datetime import datetime, timezone

router = APIRouter(prefix="/api/assets", tags=["Assets"])


def _enrich_asset(asset, prices: dict) -> dict:
    """Attach live price data to an asset object."""
    cg_id = asset.coingecko_id
    price = prices.get(cg_id) if cg_id else None
    return {
        "id": asset.id,
        "ticker": asset.ticker,
        "name": asset.name,
        "asset_type": asset.asset_type,
        "risk_rating": asset.risk_rating,
        "is_tradeable": asset.is_tradeable,
        "live_price_usd": price,
        "stale_data": is_data_stale(cg_id) if cg_id else False,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }


@router.post(
    "/",
    response_model=AssetResponse,
    status_code=201,
    summary="Add a new asset",
    description="Register a new investable asset on the platform. Ticker must be uppercase.",
)
def create_asset(asset_data: AssetCreate, db: Session = Depends(get_db)):
    existing = crud.get_asset_by_ticker(db, asset_data.ticker)
    if existing:
        raise HTTPException(status_code=400, detail=f"Asset with ticker '{asset_data.ticker}' already exists")
    return crud.create_asset(db, asset_data)


@router.get(
    "/",
    response_model=AssetListResponse,
    summary="List all assets with live prices",
    description="Returns all platform assets enriched with live market prices from CoinGecko.",
)
def list_assets(db: Session = Depends(get_db)):
    assets = crud.list_assets(db)
    # Gather all CoinGecko IDs and batch-fetch prices
    cg_ids = [a.coingecko_id for a in assets if a.coingecko_id]
    prices = fetch_live_prices(cg_ids) if cg_ids else {}
    enriched = [_enrich_asset(a, prices) for a in assets]
    return {"assets": enriched, "total": len(enriched)}


@router.get(
    "/ticker/{ticker}",
    response_model=AssetEnrichedResponse,
    summary="Look up asset by ticker",
    description="Find an asset by its ticker symbol (e.g., BTC) and return with live price.",
)
def get_asset_by_ticker(ticker: str, db: Session = Depends(get_db)):
    asset = crud.get_asset_by_ticker(db, ticker)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset with ticker '{ticker.upper()}' not found")
    cg_ids = [asset.coingecko_id] if asset.coingecko_id else []
    prices = fetch_live_prices(cg_ids) if cg_ids else {}
    return _enrich_asset(asset, prices)


@router.get(
    "/{asset_id}",
    response_model=AssetEnrichedResponse,
    summary="Get asset by ID",
    description="Fetch a single asset by UUID with live market price data.",
)
def get_asset(asset_id: str, db: Session = Depends(get_db)):
    asset = crud.get_asset_by_id(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    cg_ids = [asset.coingecko_id] if asset.coingecko_id else []
    prices = fetch_live_prices(cg_ids) if cg_ids else {}
    return _enrich_asset(asset, prices)


@router.put(
    "/{asset_id}",
    response_model=AssetResponse,
    summary="Update asset metadata",
    description="Update an asset's description, risk_rating, coingecko_id, or other metadata.",
)
def update_asset(asset_id: str, update_data: AssetUpdate, db: Session = Depends(get_db)):
    db_asset = crud.update_asset(db, asset_id, update_data)
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return db_asset


@router.patch(
    "/{asset_id}/tradeable",
    response_model=AssetResponse,
    summary="Toggle tradeable status",
    description="Enable or disable trading for an asset on the platform.",
)
def toggle_tradeable(asset_id: str, toggle: TradeableToggle, db: Session = Depends(get_db)):
    db_asset = crud.toggle_tradeable(db, asset_id, toggle.is_tradeable)
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return db_asset


@router.delete(
    "/{asset_id}",
    status_code=200,
    summary="Delete an asset",
    description="Hard-delete an asset from the platform. Returns 409 if transactions reference it.",
)
def delete_asset(asset_id: str, db: Session = Depends(get_db)):
    success, error = crud.delete_asset(db, asset_id)
    if not success:
        if error == "Asset not found":
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(status_code=409, detail=error)
    return {"message": f"Asset '{asset_id}' has been permanently deleted."}
