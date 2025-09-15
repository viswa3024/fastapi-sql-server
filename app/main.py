from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List

# ---------- SQL Server Connection ----------
DATABASE_URL = "mssql+pyodbc://sa:test1234@localhost\\SQLEXPRESS/EMPLOYEE?driver=ODBC+Driver+17+for+SQL+Server"

# SQLAlchemy engine and session
engine = create_engine(DATABASE_URL, fast_executemany=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# ---------- SQLAlchemy Model ----------
class Emp(Base):
    __tablename__ = "EMP"
    ID = Column(Integer, primary_key=True, index=True, autoincrement=False)
    NAME = Column(String(50), nullable=False)

# Create table if not exists
Base.metadata.create_all(bind=engine)

# ---------- Pydantic Schemas ----------
class EmpCreate(BaseModel):
    ID: int
    NAME: str

class EmpUpdate(BaseModel):
    NAME: str

# ---------- FastAPI App ----------
app = FastAPI(title="Employee CRUD API")

# ---------- Dependency ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- CRUD Endpoints ----------

@app.get("/emp/", response_model=List[EmpCreate])
def get_all_emps(db: Session = Depends(get_db)):
    emps = db.query(Emp).all()
    return emps

@app.post("/emp/", response_model=EmpCreate)
def create_emp(emp: EmpCreate, db: Session = Depends(get_db)):
    existing = db.query(Emp).filter(Emp.ID == emp.ID).first()
    if existing:
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    new_emp = Emp(ID=emp.ID, NAME=emp.NAME)
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return new_emp

@app.get("/emp/{emp_id}", response_model=EmpCreate)
def read_emp(emp_id: int, db: Session = Depends(get_db)):
    emp = db.query(Emp).filter(Emp.ID == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

@app.put("/emp/{emp_id}", response_model=EmpCreate)
def update_emp(emp_id: int, emp: EmpUpdate, db: Session = Depends(get_db)):
    db_emp = db.query(Emp).filter(Emp.ID == emp_id).first()
    if not db_emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    db_emp.NAME = emp.NAME
    db.commit()
    db.refresh(db_emp)
    return db_emp

@app.delete("/emp/{emp_id}")
def delete_emp(emp_id: int, db: Session = Depends(get_db)):
    db_emp = db.query(Emp).filter(Emp.ID == emp_id).first()
    if not db_emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(db_emp)
    db.commit()
    return {"detail": "Employee deleted successfully"}


# Health
@app.get("/health")
def health():
    return {"status": "ok"}

