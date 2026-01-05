from fastapi import FastAPI
from backend.api.player_replacement import router as replacement_router
from backend.api.pvp import router as pvp_router
from backend.api.pvt import router as pvt_router
from backend.api.synergy import router as synergy_router
from backend.api.bestxi import router as bestxi_router
from backend.api.meta import router as meta_router







app = FastAPI(title="Cricket Analysis API")

app.include_router(replacement_router)
app.include_router(pvp_router)
app.include_router(pvt_router)
app.include_router(synergy_router)
app.include_router(bestxi_router)
app.include_router(meta_router)