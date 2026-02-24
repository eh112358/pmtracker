from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database import engine, SessionLocal, Base
from . import models
from .routes import metals, products, holdings, portfolio, auth

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Precious Metals Tracker",
    description="Track your physical precious metals portfolio",
    version="1.0.0"
)

# Include routers
app.include_router(auth.router)
app.include_router(metals.router)
app.include_router(products.router)
app.include_router(holdings.router)
app.include_router(portfolio.router)


@app.on_event("startup")
def seed_database():
    """Seed the database with initial metals and common products."""
    db = SessionLocal()

    try:
        # Check if metals already exist
        if db.query(models.Metal).count() == 0:
            # Seed metals
            metals_data = [
                {"name": "Gold", "symbol": "gold"},
                {"name": "Silver", "symbol": "silver"},
                {"name": "Platinum", "symbol": "platinum"},
                {"name": "Palladium", "symbol": "palladium"},
            ]

            for metal_data in metals_data:
                metal = models.Metal(**metal_data)
                db.add(metal)

            db.commit()

            # Get metal IDs
            gold = db.query(models.Metal).filter(models.Metal.symbol == "gold").first()
            silver = db.query(models.Metal).filter(models.Metal.symbol == "silver").first()
            platinum = db.query(models.Metal).filter(models.Metal.symbol == "platinum").first()
            palladium = db.query(models.Metal).filter(models.Metal.symbol == "palladium").first()

            # Seed common products
            products_data = [
                # Gold products
                {"name": "American Gold Eagle 1 oz", "metal_id": gold.id, "weight_oz": 1.0, "description": "US Mint gold bullion coin"},
                {"name": "American Gold Eagle 1/2 oz", "metal_id": gold.id, "weight_oz": 0.5, "description": "US Mint gold bullion coin"},
                {"name": "American Gold Eagle 1/4 oz", "metal_id": gold.id, "weight_oz": 0.25, "description": "US Mint gold bullion coin"},
                {"name": "American Gold Eagle 1/10 oz", "metal_id": gold.id, "weight_oz": 0.1, "description": "US Mint gold bullion coin"},
                {"name": "Canadian Gold Maple Leaf 1 oz", "metal_id": gold.id, "weight_oz": 1.0, "description": "Royal Canadian Mint gold coin"},
                {"name": "South African Krugerrand 1 oz", "metal_id": gold.id, "weight_oz": 1.0, "description": "South African gold bullion coin"},
                {"name": "Austrian Gold Philharmonic 1 oz", "metal_id": gold.id, "weight_oz": 1.0, "description": "Austrian Mint gold coin"},
                {"name": "Gold Bar 1 oz", "metal_id": gold.id, "weight_oz": 1.0, "description": "Generic 1 oz gold bar"},
                {"name": "Gold Bar 10 oz", "metal_id": gold.id, "weight_oz": 10.0, "description": "Generic 10 oz gold bar"},
                # Silver products
                {"name": "American Silver Eagle 1 oz", "metal_id": silver.id, "weight_oz": 1.0, "description": "US Mint silver bullion coin"},
                {"name": "Canadian Silver Maple Leaf 1 oz", "metal_id": silver.id, "weight_oz": 1.0, "description": "Royal Canadian Mint silver coin"},
                {"name": "Austrian Silver Philharmonic 1 oz", "metal_id": silver.id, "weight_oz": 1.0, "description": "Austrian Mint silver coin"},
                {"name": "Silver Round 1 oz", "metal_id": silver.id, "weight_oz": 1.0, "description": "Generic 1 oz silver round"},
                {"name": "Silver Bar 10 oz", "metal_id": silver.id, "weight_oz": 10.0, "description": "Generic 10 oz silver bar"},
                {"name": "Silver Bar 100 oz", "metal_id": silver.id, "weight_oz": 100.0, "description": "Generic 100 oz silver bar"},
                {"name": "90% Silver US Coins (per $1 face)", "metal_id": silver.id, "weight_oz": 0.715, "description": "Pre-1965 US silver coins"},
                # Platinum products
                {"name": "American Platinum Eagle 1 oz", "metal_id": platinum.id, "weight_oz": 1.0, "description": "US Mint platinum bullion coin"},
                {"name": "Canadian Platinum Maple Leaf 1 oz", "metal_id": platinum.id, "weight_oz": 1.0, "description": "Royal Canadian Mint platinum coin"},
                {"name": "Platinum Bar 1 oz", "metal_id": platinum.id, "weight_oz": 1.0, "description": "Generic 1 oz platinum bar"},
                # Palladium products
                {"name": "Canadian Palladium Maple Leaf 1 oz", "metal_id": palladium.id, "weight_oz": 1.0, "description": "Royal Canadian Mint palladium coin"},
                {"name": "Palladium Bar 1 oz", "metal_id": palladium.id, "weight_oz": 1.0, "description": "Generic 1 oz palladium bar"},
            ]

            for product_data in products_data:
                product = models.Product(**product_data)
                db.add(product)

            db.commit()
            print("Database seeded with metals and products")

    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Precious Metals Tracker API", "docs": "/docs"}


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}


@app.post("/api/admin/reseed", tags=["admin"])
def reseed_database():
    """Force reseed the database with metals and products."""
    db = SessionLocal()
    try:
        # Clear existing data
        db.query(models.Product).delete()
        db.query(models.Metal).delete()
        db.commit()

        # Seed metals
        metals_data = [
            {"name": "Gold", "symbol": "gold"},
            {"name": "Silver", "symbol": "silver"},
            {"name": "Platinum", "symbol": "platinum"},
            {"name": "Palladium", "symbol": "palladium"},
        ]

        for metal_data in metals_data:
            metal = models.Metal(**metal_data)
            db.add(metal)
        db.commit()

        # Get metal IDs
        gold = db.query(models.Metal).filter(models.Metal.symbol == "gold").first()
        silver = db.query(models.Metal).filter(models.Metal.symbol == "silver").first()
        platinum = db.query(models.Metal).filter(models.Metal.symbol == "platinum").first()
        palladium = db.query(models.Metal).filter(models.Metal.symbol == "palladium").first()

        # Seed products
        products_data = [
            {"name": "American Gold Eagle 1 oz", "metal_id": gold.id, "weight_oz": 1.0, "description": "US Mint gold bullion coin"},
            {"name": "American Gold Eagle 1/2 oz", "metal_id": gold.id, "weight_oz": 0.5, "description": "US Mint gold bullion coin"},
            {"name": "American Gold Eagle 1/4 oz", "metal_id": gold.id, "weight_oz": 0.25, "description": "US Mint gold bullion coin"},
            {"name": "American Gold Eagle 1/10 oz", "metal_id": gold.id, "weight_oz": 0.1, "description": "US Mint gold bullion coin"},
            {"name": "Canadian Gold Maple Leaf 1 oz", "metal_id": gold.id, "weight_oz": 1.0, "description": "Royal Canadian Mint gold coin"},
            {"name": "South African Krugerrand 1 oz", "metal_id": gold.id, "weight_oz": 1.0, "description": "South African gold bullion coin"},
            {"name": "Austrian Gold Philharmonic 1 oz", "metal_id": gold.id, "weight_oz": 1.0, "description": "Austrian Mint gold coin"},
            {"name": "Gold Bar 1 oz", "metal_id": gold.id, "weight_oz": 1.0, "description": "Generic 1 oz gold bar"},
            {"name": "Gold Bar 10 oz", "metal_id": gold.id, "weight_oz": 10.0, "description": "Generic 10 oz gold bar"},
            {"name": "American Silver Eagle 1 oz", "metal_id": silver.id, "weight_oz": 1.0, "description": "US Mint silver bullion coin"},
            {"name": "Canadian Silver Maple Leaf 1 oz", "metal_id": silver.id, "weight_oz": 1.0, "description": "Royal Canadian Mint silver coin"},
            {"name": "Austrian Silver Philharmonic 1 oz", "metal_id": silver.id, "weight_oz": 1.0, "description": "Austrian Mint silver coin"},
            {"name": "Silver Round 1 oz", "metal_id": silver.id, "weight_oz": 1.0, "description": "Generic 1 oz silver round"},
            {"name": "Silver Bar 10 oz", "metal_id": silver.id, "weight_oz": 10.0, "description": "Generic 10 oz silver bar"},
            {"name": "Silver Bar 100 oz", "metal_id": silver.id, "weight_oz": 100.0, "description": "Generic 100 oz silver bar"},
            {"name": "90% Silver US Coins (per $1 face)", "metal_id": silver.id, "weight_oz": 0.715, "description": "Pre-1965 US silver coins"},
            {"name": "American Platinum Eagle 1 oz", "metal_id": platinum.id, "weight_oz": 1.0, "description": "US Mint platinum bullion coin"},
            {"name": "Canadian Platinum Maple Leaf 1 oz", "metal_id": platinum.id, "weight_oz": 1.0, "description": "Royal Canadian Mint platinum coin"},
            {"name": "Platinum Bar 1 oz", "metal_id": platinum.id, "weight_oz": 1.0, "description": "Generic 1 oz platinum bar"},
            {"name": "Canadian Palladium Maple Leaf 1 oz", "metal_id": palladium.id, "weight_oz": 1.0, "description": "Royal Canadian Mint palladium coin"},
            {"name": "Palladium Bar 1 oz", "metal_id": palladium.id, "weight_oz": 1.0, "description": "Generic 1 oz palladium bar"},
        ]

        for product_data in products_data:
            product = models.Product(**product_data)
            db.add(product)
        db.commit()

        return {"message": "Database reseeded successfully", "metals": 4, "products": len(products_data)}
    finally:
        db.close()


# Serve frontend static files (when built frontend is present)
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="static-assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = static_dir / full_path
        if full_path and file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(static_dir / "index.html")
