"""Verify exported receipt chain and exact canonical receipt hashes."""
import hashlib
import json
import sys
rows=json.load(open(sys.argv[1]))
assert isinstance(rows,list) and rows, 'Provide ordered receipt objects'
previous=''
for i,row in enumerate(rows,1):
    row=dict(row); h=row.pop('receipt_hash')
    assert row['sequence']==i and row['previous_hash']==previous, 'Broken chain'
    assert row['claim_id']==rows[0]['claim_id'], 'Mixed claims'
    actual=hashlib.sha256(json.dumps(row,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
    assert actual==h, 'Invalid receipt hash'
    previous=h
print(f'Verified {len(rows)} receipt(s); head {previous}')
