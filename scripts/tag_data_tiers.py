import json

path = 'data/processed/south_lhonak_boundaries.geojson'
with open(path, 'r', encoding='utf-8') as f:
    d = json.load(f)

for f in d['features']:
    p = f['properties']
    date = p.get('date', '')
    
    if date in ('2023-09-26', '2023-10-09'):
        p['data_tier'] = 'EMPIRICAL_MEASURED_SATELLITE'
        p['provenance_label'] = 'Direct Sentinel-2 Level-2A Ingested & Processed Scene'
        p['is_measured'] = True
    elif date in ('2023-09-17', '2023-10-04'):
        p['data_tier'] = 'PUBLISHED_NRSC_ASSESSMENT'
        p['provenance_label'] = 'ISRO NRSC Rapid Disaster Management Support Report'
        p['is_measured'] = False
    else:
        p['data_tier'] = 'HISTORICAL_BASELINE_ARCHIVE'
        p['provenance_label'] = 'Decadal USGS/ESA Baseline Archive (Precomputed)'
        p['is_measured'] = False

with open(path, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2)

print("Tagged all 7 observations with data tiers successfully!")
