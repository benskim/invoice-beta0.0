## load po, invoice files
po_lines = [  {
      "id": "PO1",
      "desc": "Battery Rack 600x800x2000 SECC 48V",
      "features": {
            "category": "Structure", ##
            "core_spec": "Battery Rack Frame",
            "material": "SECC",
            "voltage": "48V",
            "dimension": "600x800x2000mm"
        },
      "qty": 10,
      "unit_price": 1200,
      "amt": 12000
    },
    {
      "id": "PO2",
      "desc": "Cooling Unit Industrial Air Conditioner 220VAC 5kW",
        "features": {
                "category": "Cooling", #Thermal Management
                "core_spec": "Air Conditioner",
                "material": None,
                "voltage": "220VAC",
                "power": "5kW"
            },
      "qty": 4,
      "unit_price": 2500,
      "amt": 10000
    },
    {
      "id": "PO3",
      "desc": "BMS Module V2 RJ45 Interface",
      "features": {
            "category": "Control Logic",
            "core_spec": "BMS Module", #battery management system
            "material": None,
            "interface": "RJ45",
            "version": "V2"
        },
      "qty": 20,
      "unit_price": 450,
      "amt": 9000
    },
    {
      "id": "PO4",
      "desc": "Busbar Copper M8 300mm",
      "features": {
            "category": "Electrical", #Electrical Component
            "core_spec": "Busbar", 
            "material": "Copper",
            "dimension": "300mm",
            "terminal": "M8"
        },
      "qty": 100,
      "unit_price": 15,
      "amt": 1500
    },
    {
      "id": "PO5",
      "desc": "Battery Module LG 100Ah 48V",
      "features": {
            "category": "Battery", 
            "core_spec": "Battery Module", 
            "material": None,
            "capacity": "100Ah",
            "voltage": "48V"
        },
      "qty": 30,
      "unit_price": 850,
      "amt": 25500
    }]
invoice_lines = [ {
      "id": "INV1",
      "po_ref": "PO2",
      "desc": "Industrial Cooling Unit 48V 5kW",
      "features": {
            "category": "Cooling", #Thermal Management
            "core_spec": "Air Conditioner",
            "material": None,
            "voltage": "48V",
            "power": "5kW"
        },
      "qty": 10,
      "unit_price": 1200,
      "amt": 12000,
    #   "error_type": "different_product",
    #   "severity": "L1"
    },{
      "id": "INV2",
      "po_ref": "PO1",
      "desc": "Battery Rack 600x800x2000 SUS304 110V",
      "features": {
            "category": "Structure", ##
            "core_spec": "Battery Rack Frame",
            "material": "SUS304",
            "voltage": "110V",
            "dimension": "600x800x2000mm"
        },
      "qty": 10,
      "unit_price": 1250,
      "amt": 12500,
    #   "error_type": "specification_conflict",
    #   "severity": "L2"
    },{
      "id": "INV3",
      "po_ref": "PO4",
      "desc": "Busbar Copper M6 250mm",
      "features": {
            "category": "Electrical", #Electrical Component
            "core_spec": "Busbar", 
            "material": "Copper",
            "dimension": "250mm",
            "terminal": "M6"
        },
      "qty": 100,
      "unit_price": 15,
      "amt": 1500,
    #   "error_type": "model_conflict",
    #   "severity": "L3"
    }
    ]


from collections import defaultdict
import re
from rapidfuzz import fuzz


def normalize_text(text):
    # next version
    # Unit Normalization (단위 정규화): 인보이스에 30cm로 적혀 있어도 L5의 300mm와 동일값으로 인식하도록 
    # 변환 로직을 갖춰야 합니다.
    # Material Alias (재질 별칭): SECC와 Steel 혹은 Copper와 Cu를 동일한 속성값으로 매핑하여 
    # 텍스트 불일치를 해결합니다.
    return text.strip().lower().replace("  ", "")



# def extract_features(desc):
#     # 향후 dictionary, regex-map으로 해결
#     return {
#         "category": extract_category(desc),
#         # core specifications conflict - material, voltage, power
#         "material": extract_material(desc),
#         "voltage": extract_voltage(desc),
#         # key identifier conflict - model, dimension, interface, capacity
#         "model": extract_model(desc), #version
#         # "interface": extract_interface(desc), # network
#         # "dimension": extract_dimension(desc),
#         # "capacity": extract_capacity(desc),
#     }


# build po index db (changable by company)
def build_po_index(po_lines):
    # return
    # { "battery rack" : [ "stainless" : [ {po_line1}, {po_line2} ]
    #                      , "steel" : [ {po_line3} ] ] }
    # }
    index = defaultdict(lambda: defaultdict(dict))

    # extract features for each PO line and build index by category
    for po_line in po_lines:
        po_line["desc"] = normalize_text(po_line["desc"])

        # w/o LLM version
        # features = extract_features(po_line["desc"])
        # po_line["features"] = features
        
        # w/ LLM version
        features = po_line["features"]

        # name --> key value

        category = normalize_text(features.get("category", "unknown"))
        core_spec = normalize_text(features.get("core_spec", "unknown"))
        # voltage = features.get("voltage", "unknown")
        index[category][core_spec][po_line["id"]] = po_line
    return index

def retrieve_candidates(invoice_line, po_index):
    # return
    # [ {po_line1}, {po_line2} ]
   
    invoice_line["desc"] = normalize_text(invoice_line["desc"])
    
    # w/o LLM version
    # features = extract_features(invoice_line["desc"])
    
    # w/ LLM version
    features = invoice_line["features"]
    category = normalize_text(features.get("category", "unknown"))
    core_spec = normalize_text(features.get("core_spec", "unknown"))
    # voltage = features.get("voltage", "unknown")

    candidates = []

    # Level 1
    if category not in po_index:
        return candidates

    # Level 2
    if core_spec not in po_index[category]:
        # fallback:
        # core_spec 무시하고 category 전체 사용
        for items in po_index[category].values():
            candidates.extend(list(items.values()))
        return candidates

    # Level 3
    candidates = list(po_index[category][core_spec].values())
    return candidates


def tokenize(text: str):
    """
    Example:
    Samsung SSD 1TB 10ea
    ->
    ['samsung', 'ssd', '1tb', '10ea']
    """
    # text = normalize(text)
    tokens = re.findall(r"[a-zA-Z0-9\.]+", text)
    return tokens

def extract_numbers(tokens):
    """    Extract numeric-ish tokens
    Example:
    ['ssd', '1tb', '10ea']
    ->
    ['1tb', '10ea']
    """
    nums = []
    for t in tokens:
        if re.search(r"\d", t):
            nums.append(t)
    return nums

def coverage(tokens1, tokens2):
    """
    How much of PO is covered by invoice
    invoice covers PO 얼마나 많이 포함?
    """
    s1 = set(tokens1)
    s2 = set(tokens2)
    if not s2:
        return 0.0
    inter = len(s1 & s2)
    return inter / len(s2)

def numeric_overlap(nums1, nums2):
    """    
    Numeric token overlap
    Example:   
    ['1tb', '10ea']    vs    ['1tb', '12ea']
    -> 0.5
    """
    s1 = set(nums1)
    s2 = set(nums2)
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    inter = len(s1 & s2)
    union = len(s1 | s2)
    return inter / union

# def token_frequency_similarity(tokens1, tokens2):
#     """
#     Counter-based similarity : boundles/qunatity similarity
#     Helps repeated token cases
#     """
#     c1 = Counter(tokens1)
#     c2 = Counter(tokens2)
#     common = 0
#     for k in c1:
#         common += min(c1[k], c2.get(k, 0))
#     total = max(sum(c1.values()), sum(c2.values()))
#     if total == 0:
#         return 0.0
#     return common / total

def format_similarity(text1, text2):
    """
    Fuzz token sort ratio as similarity score
    """
    return fuzz.token_sort_ratio(text1, text2) / 100

def calculate_similarity(inv_text, po_text):

    # 1. text similarity
    coverage_score = coverage(tokenize(inv_text), tokenize(po_text))
    fuzzy_score = format_similarity(inv_text, po_text)

    # 2. numeric similarity
    numeric_score = numeric_overlap(extract_numbers(tokenize(inv_text)), extract_numbers(tokenize(po_text)))

    # -------------------------------
    # weighted final score
    # -------------------------------
    final_score = (
        0.30 * coverage_score +
        0.30 * fuzzy_score +
        0.40 * numeric_score 
    )

    return {
        "final_score": round(final_score, 4),
        "detail": {
            "coverage": round(coverage_score, 4),
            "fuzzy": round(fuzzy_score, 4),
            "numeric": round(numeric_score, 4),  
        }
    }


# def classify_severity_score(severity_score):
#     # severity_score 기반으로 severity 결정
#     if severity_score <= -3:
#         return "L1"
#     elif severity_score <= -2:
#         return "L2"
#     elif severity_score == -1:
#         return "L3"
#     else:
#         return "L4"

def classify_severity_reason(severity_reason):
    if severity_reason:
        reasons = severity_reason.strip(', ').split(', ')
        if "category" in reasons or "core spec" in reasons:
            return "L1"
        elif "material" in reasons or "voltage" in reasons or "power" in reasons:
            return "L2"
        elif "model" in reasons or "interface" in reasons:
            return "L3" 
        elif "dimension" in reasons or "capacity" in reasons:
            return "L4"
    return "L5"  # No significant issues   
# def classify_severity(pof,invf):
    # feature importance 기반으로 severity 결정
    # 예시: specification conflict > quantity mismatch
    # if pof["category"] != invf["category"]:
    #     return "L1"
    # elif pof["material"] != invf["material"]:
    #     return "L2"
    # elif pof["voltage"] != invf["voltage"]:
    #     return "L3"
    # else:
    #     return "L4" 

def predict_decision(score, severity):
    # score + severity 기반으로 승인/거절 결정
    if severity in ["L1", "L2"]:
        return "Reject"
    elif severity in ["L3", "L4"] and score < 0.7:
        return "Review"
    else:
        return "Approve"
    

# workflow
#upload
#parse+extract
#indexing
po_index_db = build_po_index(po_lines)

for line in invoice_lines:
    # print(line['desc']) - debug
    # print(line['features']) #- debug
    #retrieve candidates for each invoice line
    line["candidates"] = retrieve_candidates(line, po_index_db)
    # print(line["candidates"]) #- debug

    for po_item in line["candidates"]:
        po_item["severity_score"] = 0 #setdefault하면 중복 저장됨.
        po_item["score"] = 0
        po_item["severity_reason"] = ""

    # 인보이스에서 추출된 유효한 피처만 추출
    valid_features = {k: v for k, v in line['features'].items() if v is not None}

    # feature 기반 후보군 평가 및 점수 계산 --> feature weight map 필요[ver3]
    for feature_name, inv_value in valid_features.items():
        for po_item in line["candidates"]:
            po_value = po_item['features'].get(feature_name)
            
            if po_value is not None:
                print("yes : " , po_value ," === ?",inv_value) #- debug
                # 둘 다 값이 있을 때만 본격적인 '유사도 계산' 혹은 '단순 비교' 수행
    
                # feature comparision
                sim_result =  calculate_similarity(inv_value, po_value)["final_score"]
                po_item["score"] += sim_result *0.2 #feature별 가중치 예시(소수점 float)
                if sim_result < 0.8:
                    po_item['severity_score'] = po_item.get('severity_score', 0) - 1
                    po_item['severity_reason'] = po_item.get('severity_reason', '') + feature_name + ', '
                # desc comparison
                # po_item["score"] = calculate_similarity(line['desc'], po_item['desc'])["final_score"]

            else:
                # PO에 정보가 없는 경우: 심각한 탈락!
                # 일치도에 영향을 주지 않거나 감점 처리
                po_item['severity_score'] = po_item.get('severity_score', 0) - 1
                po_item['severity_reason'] = po_item.get('severity_reason', '') + feature_name + ', '
                print("no : ",inv_value, "=== ?",po_value) #- debug
    
    # rank candidates by score and select best match
    line["candidates"].sort(
        key=lambda x: (x.get("severity_score", 0), x.get("score", 0)),
        reverse=True,
    )
    line["best_match"] = line["candidates"][0] if line["candidates"] else None  
    # print(line["candidates"]) - debug

    # classifiy serverity : L1~L5 based on feature importance and error type 
    # (예시: specification conflict > quantity mismatch)
    best_match = line["best_match"]
    best_severity_score = best_match.get("severity_score", 0) if best_match else 0
    best_score = best_match.get("score", 0) if best_match else 0
    best_severity_reason = best_match.get("severity_reason", "") if best_match else ""

    line["severity"] = classify_severity_reason(best_severity_reason)
    line["decision"] = predict_decision(best_score, line["severity"])

    score_text = f"{best_score:.4f}" if best_match else "N/A"
    print(
        f"severity_reason : {best_severity_reason}",
        f"Invoice Line: {line['id']}, Best Match PO Line: {best_match['id'] if best_match else 'None'}, "
        f"Score: {score_text}, Severity: {line['severity']}, Decision: {line['decision']}"
    )
