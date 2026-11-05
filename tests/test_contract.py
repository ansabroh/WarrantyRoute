import copy
import datetime
import hashlib
import importlib
import json
import pytest


TERMS = 'Warranty WR-01 for product mixer_01. Purchased 2026-01-01. Coverage ends 2026-12-31. Report by 2026-12-31. Motor manufacturing defects are covered. Cosmetic scratches and misuse are excluded. Authorized repair history is required.'
PURCHASE = 'Issuer receipt WR-01: mixer_01 purchased 2026-01-01 by the registered claimant.'
SERVICE = 'Authorized inspection for mixer_01: motor winding manufacturing defect began 2026-06-01. No misuse, liquid damage or unauthorized repairs. Complete repair history: no previous repairs. Housing scratch is cosmetic.'
BASE = 'https://raw.githubusercontent.com/ansabroh/WarrantyRoute/' + 'a' * 40 + '/fixtures/'

def doc(name, body):
    return {'url': BASE+name+'.txt', 'sha256': hashlib.sha256(body.encode()).hexdigest(), 'bytes': len(body.encode())}

def ordinal(s):
    return datetime.date.fromisoformat(s).toordinal()

def answer(statuses=('COVERED',), identity='MATCH'):
    return {'identity': identity, 'purchase_quote': PURCHASE, 'terms_quote': TERMS, 'service_quote': SERVICE,
            'items': [{'id': 'line'+str(i), 'status': x, 'term_quote': TERMS, 'service_quote': SERVICE, 'reason': 'Motor manufacturing defect, or explicit cosmetic exclusion.'} for i,x in enumerate(statuses)]}

@pytest.fixture
def setup(direct_vm, direct_deploy, direct_owner, direct_alice, direct_bob):
    direct_vm.warp('2026-06-15T00:00:00Z')
    contract = direct_deploy('contracts/warranty_route.py')
    w = {'product':'mixer_01','claimant':'0x'+direct_alice.hex(),'service_provider':'0x'+direct_bob.hex(), 'purchase_day':ordinal('2026-01-01'),'coverage_end_day':ordinal('2026-12-31'),'report_by_day':ordinal('2026-12-31'),'purchase':doc('purchase',PURCHASE),'terms':doc('terms',TERMS)}
    c = {'failure_day':ordinal('2026-06-01'),'items':[{'id':'line0','component':'motor','defect':'Motor winding failure'}]}
    return contract,w,c

def mocks(vm, result=None, corrupt=None, audit='VALID'):
    vm.clear_mocks()
    for name,body in [('purchase',PURCHASE),('terms',TERMS),('service',SERVICE)]:
        vm.mock_web(BASE+name+'.txt', {'status':200,'body':body if name != corrupt else body+' altered'})
    vm.mock_llm('WarrantyRoute independent',json.dumps(result or answer()))
    vm.mock_llm('WarrantyRoute grounding audit',audit)

def ready(setup, vm, alice, bob):
    x,w,c=setup
    x.register_warranty('w1',json.dumps(w))
    vm.sender=alice
    x.file_claim('c1','w1',json.dumps(c))
    vm.sender=bob
    x.attest_service('c1',json.dumps(doc('service',SERVICE)))
    vm.sender=alice
    mocks(vm)
    return x

def test_lifecycle(setup,direct_vm,direct_alice,direct_bob):
    x=ready(setup,direct_vm,direct_alice,direct_bob)
    assert json.loads(x.get_status('c1'))['outcome']=='PENDING'
    x.assess('c1')
    assert json.loads(x.get_status('c1'))['outcome']=='COVERED'
    assert direct_vm.run_validator()
    r=json.loads(x.get_receipt('c1',1)); h=r.pop('receipt_hash')
    assert hashlib.sha256(json.dumps(r,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()==h
    with direct_vm.expect_revert('Assessment final'): x.assess('c1')

@pytest.mark.parametrize('statuses,expected',[(('COVERED',),'COVERED'),(('EXCLUDED',),'EXCLUDED'),(('UNKNOWN',),'INCONCLUSIVE'),(('COVERED','EXCLUDED'),'PARTIALLY_COVERED'),(('COVERED','UNKNOWN'),'INCONCLUSIVE')])
def test_outcomes(setup,direct_vm,direct_alice,direct_bob,statuses,expected):
    x,w,c=setup
    c['items']=[{'id':'line'+str(i),'component':'motor' if i==0 else 'housing','defect':'reported damage'} for i in range(len(statuses))]
    x=ready(setup,direct_vm,direct_alice,direct_bob)
    mocks(direct_vm,answer(statuses)); x.assess('c1')
    assert json.loads(x.get_status('c1'))['outcome']==expected
    assert direct_vm.run_validator()

@pytest.mark.parametrize('field,day,expected', [('failure_day','2025-12-31','INCONCLUSIVE'),('failure_day','2026-12-31','COVERED'),('failure_day','2027-01-01','EXCLUDED')])
def test_dates(setup,direct_vm,direct_alice,direct_bob,field,day,expected):
    direct_vm.warp('2027-01-01T00:00:00Z' if day=='2027-01-01' else '2026-12-31T00:00:00Z')
    x,w,c=setup; c[field]=ordinal(day)
    x=ready(setup,direct_vm,direct_alice,direct_bob)
    x.assess('c1'); assert json.loads(x.get_status('c1'))['outcome']==expected

def test_report_date_is_chain_day(setup,direct_vm,direct_alice,direct_bob):
    direct_vm.warp('2027-01-01T00:00:00Z')
    x=ready(setup,direct_vm,direct_alice,direct_bob); x.assess('c1')
    assert json.loads(x.get_status('c1'))['outcome']=='EXCLUDED'
    assert json.loads(x.get_claim('c1'))['reported_day']==ordinal('2027-01-01')

@pytest.mark.parametrize('which',['purchase','terms','service'])
def test_integrity(setup,direct_vm,direct_alice,direct_bob,which):
    x=ready(setup,direct_vm,direct_alice,direct_bob)
    mocks(direct_vm,corrupt=which); x.assess('c1')
    assert json.loads(x.get_status('c1'))['outcome']=='INCONCLUSIVE'
    assert direct_vm.run_validator()

def test_retries_and_chain(setup,direct_vm,direct_alice,direct_bob):
    x=ready(setup,direct_vm,direct_alice,direct_bob); mocks(direct_vm,answer(identity='UNKNOWN'))
    prev=''
    for i in range(1,4):
        x.assess('c1'); r=json.loads(x.get_receipt('c1',i)); assert r['previous_hash']==prev; prev=r['receipt_hash']
    with direct_vm.expect_revert('Attempt limit'): x.assess('c1')

def test_permissions(setup,direct_vm,direct_alice,direct_bob,direct_charlie,direct_owner):
    x,w,c=setup; direct_vm.sender=direct_charlie
    with direct_vm.expect_revert('Issuer only'): x.register_warranty('w1',json.dumps(w))
    direct_vm.sender=direct_owner; x.register_warranty('w1',json.dumps(w))
    with direct_vm.expect_revert('Warranty already exists'): x.register_warranty('w1',json.dumps(w))
    with direct_vm.expect_revert('Claimant only'): x.file_claim('c1','w1',json.dumps(c))
    direct_vm.sender=direct_alice; x.file_claim('c1','w1',json.dumps(c))
    with direct_vm.expect_revert('Claim already exists'): x.file_claim('c1','w1',json.dumps(c))
    with direct_vm.expect_revert('Duplicate claim'): x.file_claim('c2','w1',json.dumps(c))
    with direct_vm.expect_revert('Service provider only'): x.attest_service('c1',json.dumps(doc('service',SERVICE)))
    with direct_vm.expect_revert('Service attestation required'): x.assess('c1')
    direct_vm.sender=direct_bob; x.attest_service('c1',json.dumps(doc('service',SERVICE)))
    with direct_vm.expect_revert('Service report immutable'): x.attest_service('c1',json.dumps(doc('service',SERVICE)))
    with direct_vm.expect_revert('Assessment unauthorized'): x.assess('c1')

@pytest.mark.parametrize('mutation',['branch','query','traversal','host','hash','bool','future','extra'])
def test_registration_rejects(setup,direct_vm,mutation):
    x,w,c=setup
    if mutation=='branch': w['terms']['url']=BASE.replace('a'*40,'main')+'terms.txt'
    if mutation=='query': w['terms']['url']+='?token=bad'
    if mutation=='traversal': w['terms']['url']=BASE+'../terms.txt'
    if mutation=='host': w['terms']['url']=w['terms']['url'].replace('raw.githubusercontent.com','evil.test')
    if mutation=='hash': w['terms']['sha256']='bad'
    if mutation=='bool': w['purchase_day']=True
    if mutation=='future': w['purchase_day']=ordinal('2027-01-01')
    if mutation=='extra': w['hidden']='bad'
    with direct_vm.expect_revert(): x.register_warranty('w1',json.dumps(w))

@pytest.mark.parametrize('mutation',['quote','missing','status','extra','not_object','huge'])
def test_bad_ai(setup,direct_vm,direct_alice,direct_bob,mutation):
    x=ready(setup,direct_vm,direct_alice,direct_bob); a=answer()
    if mutation=='quote': a['items'][0]['term_quote']='A fabricated warranty clause.'
    if mutation=='missing': a['items']=[]
    if mutation=='status': a['items'][0]['status']='APPROVED'
    if mutation=='extra': a['refund']=100
    raw=json.dumps(a)
    if mutation=='not_object': raw='[1,2,3]'
    if mutation=='huge': raw='x'*15000
    direct_vm.clear_mocks(); mocks(direct_vm)
    # Replace review mock, preserve independent web mocks.
    direct_vm._llm_mocks.clear(); direct_vm.mock_llm('WarrantyRoute independent',raw)
    x.assess('c1'); assert json.loads(x.get_status('c1'))['outcome']=='INCONCLUSIVE'

@pytest.mark.parametrize('mode',['different','audit','quote','error','malformed'])
def test_validator_rejects(setup,direct_vm,direct_alice,direct_bob,mode):
    x=ready(setup,direct_vm,direct_alice,direct_bob); x.assess('c1')
    if mode=='different': mocks(direct_vm,answer(('EXCLUDED',))); assert not direct_vm.run_validator()
    if mode=='audit': mocks(direct_vm,audit='INVALID'); assert not direct_vm.run_validator()
    if mode=='quote':
        a=answer(); a['items'][0]['term_quote']='Fabricated quotation here'
        assert not direct_vm.run_validator(leader_result={'answer':a})
    if mode=='error': assert not direct_vm.run_validator(leader_error=ValueError('fake'))
    if mode=='malformed': assert not direct_vm.run_validator(leader_result={'answer':{}})


def test_duplicate_registration_json(setup,direct_vm):
    x,w,c=setup
    raw=json.dumps(w).replace('"product": "mixer_01"','"product":"wrong","product":"mixer_01"')
    with direct_vm.expect_revert('Duplicate key'): x.register_warranty('w1',raw)
