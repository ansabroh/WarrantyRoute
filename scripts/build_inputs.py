"""Build Studio inputs from exact fixture bytes at a published commit. No secrets."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--commit',required=True)
p.add_argument('--claimant',required=True)
p.add_argument('--service-provider',required=True)
p.add_argument('--output',default='evidence/studio-inputs.json')
a=p.parse_args()
if len(a.commit)!=40 or any(c not in '0123456789abcdef' for c in a.commit): p.error('40 lowercase hex commit required')
root=Path(__file__).resolve().parents[1]
def doc(name):
    body=(root/'fixtures'/f'{name}.txt').read_bytes()
    return {'url':f'https://raw.githubusercontent.com/ansabroh/WarrantyRoute/{a.commit}/fixtures/{name}.txt','sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body)}
def day(s): return datetime.date.fromisoformat(s).toordinal()
w={'product':'mixer_01','claimant':a.claimant,'service_provider':a.service_provider,'purchase_day':day('2026-01-01'),'coverage_end_day':day('2026-12-31'),'report_by_day':day('2026-12-31'),'purchase':doc('purchase'),'terms':doc('terms')}
c={'failure_day':day('2026-06-01'),'items':[{'id':'motor','component':'motor','defect':'Motor winding manufacturing defect confirmed by inspection.'},{'id':'housing','component':'housing','defect':'Cosmetic housing scratch.'}]}
result={'register_warranty':['w_demo',json.dumps(w,separators=(',',':'))],'file_claim':['c_demo','w_demo',json.dumps(c,separators=(',',':'))],'attest_service':['c_demo',json.dumps(doc('service'),separators=(',',':'))],'assess':['c_demo']}
target=root/a.output; target.parent.mkdir(parents=True,exist_ok=True); target.write_text(json.dumps(result,indent=2)+'\n')
print(target)
