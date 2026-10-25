with open("api/index.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add model
old_model = '''class SyncDataRequest(BaseModel):
    receipts: Optional[List[Dict[str, Any]]] = None
    khata: Optional[List[Dict[str, Any]]] = None
    expenses: Optional[List[Dict[str, Any]]] = None'''

new_model = '''class SyncDataRequest(BaseModel):
    receipts: Optional[List[Dict[str, Any]]] = None
    khata: Optional[List[Dict[str, Any]]] = None
    expenses: Optional[List[Dict[str, Any]]] = None

class BulkDeleteReceiptsRequest(BaseModel):
    receipt_ids: List[int]'''

# 2. Add endpoints after delete_receipt
old_delete = '''@app.delete("/api/receipts/{receipt_id}")
def delete_receipt(receipt_id: int):
    conn = get_db()
    conn.execute("DELETE FROM receipts WHERE id = ?", (receipt_id,))
    conn.commit()
    conn.close()
    return {"success": True}'''

new_delete = '''@app.delete("/api/receipts/{receipt_id}")
def delete_receipt(receipt_id: int):
    conn = get_db()
    conn.execute("DELETE FROM receipts WHERE id = ?", (receipt_id,))
    conn.commit()
    conn.close()
    return {"success": True}

@app.post("/api/receipts/bulk-delete")
def bulk_delete_receipts(req: BulkDeleteReceiptsRequest):
    if not req.receipt_ids:
        return {"success": True, "deleted_count": 0}
    conn = get_db()
    placeholders = ",".join("?" for _ in req.receipt_ids)
    conn.execute(f"DELETE FROM receipts WHERE id IN ({placeholders})", req.receipt_ids)
    conn.commit()
    conn.close()
    return {"success": True, "deleted_count": len(req.receipt_ids)}

@app.delete("/api/receipts/all")
def delete_all_receipts():
    conn = get_db()
    conn.execute("DELETE FROM receipts")
    conn.commit()
    conn.close()
    return {"success": True}'''

content = content.replace(old_model.replace('\r\n', '\n'), new_model.replace('\r\n', '\n'))
content = content.replace(old_delete.replace('\r\n', '\n'), new_delete.replace('\r\n', '\n'))

with open("api/index.py", "w", encoding="utf-8") as f:
    f.write(content)

print("api/index.py updated successfully with bulk delete endpoints!")
