from fastapi import APIRouter, HTTPException, Query
from backend.database.MySQLDatabase import MySQLDatabase

router = APIRouter()


@router.get("/api/pingdb")
def api_ping_db():
    result = MySQLDatabase.instance().query("SELECT 1")
    result = result.iloc[0, 0]
    return "pong " + str(result)
    
